from vosk import Model, KaldiRecognizer
import pyaudio
import json
import struct
from math import sqrt
import time
from datetime import datetime
import webbrowser as wb
from fuzzywuzzy import fuzz
from os import system
from random import choice
from playsound import playsound

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
TIMEOUT_LENGTH = 3
SHORT_NORMALIZE = 1.0 / 32768.0
Threshold = 20
key_word = 'пирс'
phrases_for_speech = ["Doing", "Please repeat", "Listen to you"]


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
                    playsound("Pirs phrases/Listen to you.mp3")
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
            ("пока", "заверши работу"): self.bye
        }

        max_similar = 0  # the coefficient of similarity
        cmd = ''  # command
        search_tags = ("как", "кто такой", "кто такая", "что такое", "найди", "ищи", "найти")

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
            for tag in search_tags:
                if tag in task:
                    return self.web_search(task.replace(tag, ""))
            playsound("Pirs phrases/Please repeat.mp3")

    @staticmethod
    def random_phrase():
        phrase = choice(phrases_for_speech)
        audio_file = f"Pirs phrases/{phrase}.mp3"
        return audio_file

    # Functions
    def youtube(self):
        playsound(self.random_phrase())
        return wb.open("https://www.youtube.com/")

    def vk(self):
        playsound(self.random_phrase())
        return wb.open("https://vk.com/")

    @staticmethod
    def web_search(task):
        return wb.open(f"https://www.google.com/search?q={task}&sourceid=chrome&ie=UTF-8".replace(" ", "+"))

    def taskmgr(self):
        playsound(self.random_phrase())
        return system("taskmgr")

    def control(self):
        playsound(self.random_phrase())
        return system("control")

    def explorer(self):
        playsound(self.random_phrase())
        return system("explorer")

    def calc(self):
        playsound(self.random_phrase())
        return system("start calc")

    def params(self):
        playsound(self.random_phrase())
        return system("dpiscaling")

    def turn_off(self):
        playsound(self.random_phrase())
        return system("shutdown /s")

    def refresh(self):
        playsound(self.random_phrase())
        return system("shutdown /r")

    @staticmethod
    def greeting():
        current_time = datetime.now()
        if (current_time.hour > 6) and (current_time.hour < 12):
            playsound(r"Pirs phrases\Good morning.mp3")
        elif (current_time.hour > 12) and (current_time.hour < 18):
            playsound(r"Pirs phrases\Good morning.mp3")
        elif (current_time.hour > 19) and (current_time.hour < 23):
            playsound(r"Pirs phrases\Good morning.mp3")
        else:
            playsound(r"Pirs phrases\Good morning.mp3")

    @staticmethod
    def bye():
        playsound("Pirs phrases/Goodbye.mp3")
        exit(0)
