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

FONT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'NotoSansKR-Regular.ttf'))

class Recorder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.fs = 44100  # 샘플링 주파수
        self.recording = False
        self.audio_data = None
        self.stream = None
        self.status_label = Label(text='녹음 대기 중', font_name=FONT_PATH)
        self.add_widget(self.status_label)
        self.record_btn = Button(text='녹음 시작', font_name=FONT_PATH)
        self.record_btn.bind(on_press=self.toggle_recording)
        self.add_widget(self.record_btn)

    def toggle_recording(self, instance):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.status_label.text = '녹음 중...'
        self.record_btn.text = '녹음 완료'
        self.recording = True
        self.audio_data = []
        # 녹음은 별도 스레드에서 진행
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, dtype='int16', callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_data.append(indata.copy())

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
            self.status_label.text = f'저장 완료: {save_path}'
        else:
            self.status_label.text = '녹음 데이터 없음'
        self.record_btn.text = '녹음 시작'

class RecorderApp(App):
    def build(self):
        Window.size = (360, 640)
        return Recorder()

if __name__ == '__main__':
    RecorderApp().run() 