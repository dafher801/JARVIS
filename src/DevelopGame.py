import os
import re
import json
import anthropic
import shutil
import atexit
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

        self.clear_folder(RESULT_PATH)

        with open(REFERENCE_PATH, 'w', encoding="utf-8") as file:
            file.write("")

        with open(PROMPT_PATH + "System Prompt.txt", 'r', encoding="utf-8") as file:
            system_prompt_content = file.read()

        with open(PROMPT_PATH + "Client Request.txt", 'r', encoding="utf-8") as file:
            client_request = file.read()

        self.system_prompt = system_prompt_content.replace("{CLIENT_REQUEST}", client_request)


    def clear_folder(self, path: str):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                self.clear_folder(file_path)


    def backup(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        target_path = RECORD_PATH + timestamp + "/"
        
        shutil.copytree(PROMPT_PATH, target_path + "Prompt")
        shutil.copytree(RESULT_PATH, target_path + "Result")
        
        print(f"백업 완료: {target_path}")


    def __send_message(self, prompt: str) -> str:
        client = anthropic.Anthropic(api_key=os.environ.get("GAME_DEVELOPMENT_CLAUDE_API"),)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                with client.messages.stream(
                    model="claude-opus-4-5-20251101",
                    max_tokens=64000,
                    temperature=1,
                    system=self.system_prompt,
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

            except (httpx.RemoteProtocolError, Exception) as e:
                print(f"\n연결 오류 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print("5초 후 재시도...")
                    time.sleep(5)
                else:
                    raise Exception("최대 재시도 횟수 초과")


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


    def generate_prefabs(self):
        prompt = self.__generate_prompt("Prefab List.txt")
        result = self.__send_message(prompt)

        with open(RESULT_PATH + "Prefab List.txt", 'w', encoding="utf-8") as file:
            file.write(result)


    def generate_prefab_constructure(self):
        with open(RESULT_PATH + "Prefab List.txt", 'r', encoding="utf-8") as file:
            prefabs_text = file.read()

        prefabs = json.loads(prefabs_text)
        length = len(prefabs["prefabs"])

        for i in range(0, length):
            prefab_name = prefabs["prefabs"][i]["name"]
            prompt = self.__generate_prompt("Prefab Constructure.txt")
            prompt = prompt.replace("{PREFAB_NAME}", prefab_name)

            result = self.__send_message(prompt)

            with open(RESULT_PATH + "Prefabs/" + prefab_name + ".txt", 'w', encoding="utf-8") as file:
                file.write(result)

    
    def generate_none_prefab_constructure(self):
        with open(RESULT_PATH + "Prefab List.txt", 'r', encoding="utf-8") as file:
            none_prefabs_text = file.read()

        none_prefabs = json.loads(none_prefabs_text)
        length = len(none_prefabs["none_prefabs"])

        for i in range(0, length):
            none_prefab_name = none_prefabs["none_prefabs"][i]["name"]
            prompt = self.__generate_prompt("None Prefab Constructure.txt")
            prompt = prompt.replace("{NONE_PREFAB_NAME}", none_prefab_name)

            result = self.__send_message(prompt)

            with open(RESULT_PATH + "None Prefabs/" + none_prefab_name + ".txt", 'w', encoding="utf-8") as file:
                file.write(result)


game_developer = GameDeveloper()
game_developer.generate_game_pitching()
game_developer.generate_object_list()
game_developer.generate_prefabs()
game_developer.generate_prefab_constructure()
game_developer.generate_none_prefab_constructure()