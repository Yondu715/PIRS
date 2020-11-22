from vosk import Model, KaldiRecognizer
import pyaudio
import json
import struct
from math import sqrt
import time
import webbrowser as wb
from fuzzywuzzy import fuzz
from os import system

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
TIMEOUT_LENGTH = 3
SHORT_NORMALIZE = 1.0 / 32768.0
Threshold = 20
key_word = 'пирс'


# Voice Assistant

class Assistant:

    def __init__(self):
        # vosk
        self.model = Model("speech_model")
        self.rec = KaldiRecognizer(self.model, RATE)
        # pyaudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FPB
        )
        self.stream.start_stream()

    # rms(rated maximum sinusoidal) noise calculation
    @staticmethod
    def rms(frame):
        count = len(frame) / 2
        form = "%dh" % count
        shorts = struct.unpack(form, frame)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = sqrt(sum_squares / count)
        return rms * 1000

    def speech_to_text(self):
        task = ''
        now = time.time()
        end = time.time() + TIMEOUT_LENGTH
        print('speak')
        while now <= end:
            data = self.stream.read(FPB)
            # checking the ambient volume
            if self.rms(data) >= Threshold:
                end = time.time() + TIMEOUT_LENGTH / 1.2
            now = time.time()
            # vosk
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())
                task = text['text']
                print(task)
        return task

    def voice_activation(self):
        while True:
            data = self.stream.read(FPB)
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())
                task = text['text']
                if key_word in task:
                    self.cmd(self.speech_to_text())

    # commands execution
    def cmd(self, task):
        tasks = {
            # internet and social networks
            ("открой ютуб", "запусти ютуб"): self.youtube,
            ("открой вк", "запусти вк"): self.vk,
            # system commands and windows apps
            ("открой диспетчер задач", "запусти диспетчер задач"): self.taskmgr,
            ("открой панель управления", "запусти панель управления"): self.control,
            ("открой проводник", "запусти проводник", "открой мой компьютер", "запусти мой компьютер"): self.explorer,
            ("открой параметры", "запусти параметры"): self.params,
            ("выключи компьютер", "выключи пк"): self.turn_off,
            ("перезагрузи компьютер", "перезагрузи пк"): self.refresh,
            ("открой калькулятор", "запусти калькулятор"): self.calc,
            ("пока", "заверши работу"): exit
        }

        max_similar = 0  # the coefficient of similarity
        cmd = ''  # command

        # inaccurate search
        for ls in tasks:
            for i in ls:
                rate_similar = fuzz.ratio(task, i)
                if rate_similar > 75 and rate_similar > max_similar:
                    max_similar = rate_similar
                    cmd = ls
        try:
            tasks[cmd]()
        except KeyError:
            self.web_search(task)

    # Functions
    @staticmethod
    def youtube():
        return wb.open("https://www.youtube.com/")

    @staticmethod
    def vk():
        return wb.open("https://vk.com/")

    @staticmethod
    def web_search(task):
        return wb.open(f"https://yandex.ru/search/?lr=64&text={task}")

    @staticmethod
    def taskmgr():
        return system("taskmgr")

    @staticmethod
    def control():
        return system("control")

    @staticmethod
    def explorer():
        return system("explorer")

    @staticmethod
    def calc():
        return system("start calc")

    @staticmethod
    def params():
        return system("dpiscaling")

    @staticmethod
    def turn_off():
        return system("shutdown")

    @staticmethod
    def refresh():
        return system("shutdown -r")

    @staticmethod
    def greeting():
        pass
