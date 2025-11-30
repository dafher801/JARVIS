import os
import re
import json
import anthropic
import shutil
from datetime import datetime


PROMPT_TEMPLETE_PATH = "C:/Github/JARVIS/src/Prompt/Prompt Templete.txt"
PROMPT_PATH = "C:/Github/JARVIS/src/Prompt/"
RESULT_PATH = "C:/Github/JARVIS/src/Result/"
RECORD_PATH = "C:/Github/JARVIS/src/Record/"
REFERENCE_PATH = "C:/Github/JARVIS/src/Reference.txt"


class GameDeveloper:
    system_prompt: str

    def __init__(self):
        atexit.register(self.backup)

        with open(REFERENCE_PATH, 'w', encoding="utf-8") as file:
            file.write("")

        with open(PROMPT_PATH + "System Prompt.txt", 'r', encoding="utf-8") as file:
            system_prompt_content = file.read()

        with open(PROMPT_PATH + "Client Request.txt", 'r', encoding="utf-8") as file:
            client_request = file.read()

        self.system_prompt = system_prompt_content.replace("{CLIENT_REQUEST}", client_request)


    def backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = RECORD_PATH + timestamp + "/"
        
        shutil.copytree(PROMPT_PATH, target_path + "Prompt")
        shutil.copytree(RESULT_PATH, target_path + "Result")
        
        print(f"백업 완료: {target_path}")


    def __send_message(self, prompt: str) -> str:
        client = anthropic.Anthropic(api_key=os.environ.get("GAME_DEVELOPMENT_CLAUDE_API"),)

        with client.messages.stream(
            model="claude-opus-4-5-20251101",
            max_tokens=64000,
            temperature=1,
            system = self.system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            full_text = ""
            for text in stream.text_stream:
                full_text += text

        full_text = full_text.strip()
        full_text = re.sub(r'^```(?:json)?\s*', '', full_text)
        full_text = re.sub(r'\s*```$', '', full_text)
        full_text = full_text.strip()

        with open(REFERENCE_PATH, 'a', encoding="utf-8") as file:
            file.write(full_text + "\n\n")

        print(full_text)
        return full_text


    def __generate_prompt(self, source_file_name: str) -> str:
        source_path = PROMPT_PATH + source_file_name

        with open(REFERENCE_PATH, 'r', encoding="utf-8") as file:
            reference_data = file.read()
        
        with open(source_path, 'r', encoding="utf-8") as file:
            source_content = file.read()
        
        first_brace_index = source_content.find('{')
        
        if first_brace_index == -1:
            raise ValueError("'{' not found in source file.")
        
        request_part = source_content[:first_brace_index].strip()
        json_format_part = source_content[first_brace_index:].strip()
        
        with open(PROMPT_TEMPLETE_PATH, 'r', encoding="utf-8") as file:
            prompt_templete = file.read()
        
        prompt = prompt_templete.replace("{REQUEST}", request_part)
        prompt = prompt.replace("{JSON_FORMAT}", json_format_part)
        prompt = prompt.replace("{REFERENCE_DATA}", reference_data)
        
        return prompt


    def generate_game_pitching(self):
        prompt = self.__generate_prompt("Game Pitching.txt")
        result = self.__send_message(prompt)

        with open(RESULT_PATH + "Game Pitching.txt", 'w', encoding="utf-8") as file:
            file.write(result)


    def generate_object_list(self):
        prompt = self.__generate_prompt("Object List.txt")
        result = self.__send_message(prompt)

        with open(RESULT_PATH + "Object List.txt", 'w', encoding="utf-8") as file:
            file.write(result)


    def generate_prefab_list(self):
        prompt = self.__generate_prompt("Prefab List.txt")
        result = self.__send_message(prompt)

        with open(RESULT_PATH + "Prefab List.txt", 'w', encoding="utf-8") as file:
            file.write(result)


    def generate_prefab_constructure(self):
        with open(RESULT_PATH + "Prefab List.txt", 'r', encoding="utf-8") as file:
            prefab_list_text = file.read()

        prefab_list = json.loads(prefab_list_text)
        length = len(prefab_list["prefabs"])

        for i in range(0, length):
            prefab_name = prefab_list["prefabs"][0]["name"]
            prompt = self.__generate_prompt("Prefab Constructure.txt")
            prompt = prompt.replace("{PREFAB_NAME}", prefab_name)

            result = self.__send_message(prompt)

            with open(RESULT_PATH + prefab_name + ".txt", 'w', encoding="utf-8") as file:
                file.write(result)


game_developer = GameDeveloper()
game_developer.generate_game_pitching()
game_developer.generate_object_list()
game_developer.generate_prefab_list()
game_developer.generate_prefab_constructure()