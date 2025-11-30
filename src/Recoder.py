import os
import threading
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import whisper

FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'resources', 'font', 'KR_Font.ttf')

class Recorder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.fs = 16000
        self.recording_state = 0
        self.audio_data = None
        self.stream = None
        self.record_btn = Button(text='녹음 시작', size_hint=(1, 0.2), font_name=FONT_PATH)
        self.record_btn.bind(on_press=self.toggle_recording)
        self.add_widget(self.record_btn)

    def toggle_recording(self, instance):
        if self.recording_state == 0:
            self.start_recording()
            self.recording_state = 1
        elif self.recording_state == 1:
            self.stop_recording()
            self.recording_state = 2
        else:
            pass

    def start_recording(self):
        self.record_btn.text = '녹음 중...'
        self.recording = True
        self.audio_data = []
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, dtype='int16', callback=self.audio_callback)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.audio_data:
            audio_np = np.concatenate(self.audio_data, axis=0)
            save_path = os.path.join(os.getcwd(), 'recorded_audio.wav')
            write(save_path, self.fs, audio_np)

        self.record_btn.text = '기록 시작'

        model = whisper.load_model('large')
        result = model.transcribe('recorded_audio.wav', language='ko')

        with open('recognized_text.txt', 'w', encoding='utf-8') as f:
            f.write(result['text'])

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_data.append(indata.copy())

class RecorderApp(App):
    def build(self):
        Window.size = (360, 640)
        return Recorder()

# if __name__ == '__main__':
#     RecorderApp().run()