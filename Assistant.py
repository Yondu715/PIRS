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
from PyQt5 import QtCore

# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
TIMEOUT_LENGTH = 3
SAMPLE_WIDTH = 2
SHORT_NORMALIZE = 1.0 / 32768.0
Energy_speech = 10
key_word = 'пирс'

# Phrases and ignored programs
phrases_for_executing = ["Doing.mp3", "Will_be_done.mp3", "How_say_sir.mp3"]
phrases_for_web_search = ["Finding_information 1.mp3", "Finding_information 2.mp3", "Request_accepted.mp3"]
ignored_pr = ["Share", "NVIDIA", "TextInputHost", "Explorer", "explorer"]


""" ---> Voice Assistant <--- """

class Assistant(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.Threshold = 20
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
        count = len(frame) / SAMPLE_WIDTH
        form = "%dh" % count
        shorts = struct.unpack(form, frame)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = sqrt(sum_squares / count)
        return rms * 1000

    # Automatically adjusts microphone level to the environment
    def adjustment_to_noise(self, duration=1):
        seconds_per_buffer = FPB/RATE
        end_time = 0
        while True:
            end_time += seconds_per_buffer
            if end_time > duration:
                break
            data = self.stream.read(FPB)
            rms = self.rms(data)

            damping = 0.15 ** seconds_per_buffer
            target_rms = rms * 1.5
            self.Threshold = Energy_speech * damping * target_rms * (1 - damping)

    def speech_to_text(self):
        self.adjustment_to_noise()
        task = ''
        now = time.time()
        end = time.time() + TIMEOUT_LENGTH
        while now <= end:
            data = self.stream.read(FPB)
            # checking the ambient volume
            if self.rms(data) >= self.Threshold:
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
                    playsound("audio/Listen_to_you.mp3")
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
            ("закрой все", "закрой все приложения"): self.close_all,
            ("пока", "заверши работу"): self.bye
        }

        max_similar = 0  # the coefficient of similarity
        cmd = ''         # command
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
            playsound("audio/Repeat_please.mp3")
            new_task = self.speech_to_text()
            if new_task != "":
                self.cmd(new_task)

    # Choosing random phrase for executing command
    @staticmethod
    def random_phrase(pr_phrase=None):
        phrase = choice([choice(phrases_for_executing), pr_phrase])
        audio_file = f"audio/{phrase}"
        playsound(audio_file, block=False)

    @staticmethod
    def random_phrase_web():
        phrase = choice(phrases_for_web_search)
        audio_file = f"audio/{phrase}"
        playsound(audio_file, block=False)

    # Functions
    def youtube(self):
        self.random_phrase("Youtube.mp3")
        return wb.open("https://www.youtube.com/")

    def vk(self):
        self.random_phrase("Vk.mp3")
        return wb.open("https://vk.com/")

    def web_search(self, task):
        self.random_phrase_web()
        return wb.open(f"https://www.google.com/search?q={task}&sourceid=chrome&ie=UTF-8".replace(" ", "+"))

    def taskmgr(self):
        self.random_phrase("Opening.mp3")
        return system("taskmgr")

    def control(self):
        self.random_phrase("Control_panel.mp3")
        return system("control")

    def explorer(self):
        self.random_phrase("Opening.mp3")
        return system("explorer")

    def calc(self):
        self.random_phrase("Launching_Calculator.mp3")
        return system("start calc")

    def params(self):
        self.random_phrase("Opening.mp3")
        return system("dpiscaling")

    def turn_off(self):
        playsound("audio/Confirm_action.mp3")
        if self.speech_to_text() == "подтверждаю":
            self.random_phrase()
            return system("shutdown /s /t 0")
        else:
            return playsound("audio/How_say_sir.mp3")

    def refresh(self):
        playsound("audio/Confirm_action.mp3")
        if self.speech_to_text() == "подтверждаю":
            self.random_phrase()
            return system("shutdown /r /t 0")
        else:
            return playsound("audio/How_say_sir.mp3")

    def close_all(self):
        import subprocess
        command = 'powershell "Get-Process | Where-Object {$_.mainWindowTitle} | Format-Table ProcessName"'
        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        text = str(p.stdout.read()).replace('b', '')\
                                .replace("\\r", " ")\
                                .replace("\\n", " ")\
                                .replace("-----------", "")\
                                .replace("ProcessName", "")\
                                .replace("'", "").split()
        for task in text:
            if task not in ignored_pr:
                self.random_phrase(None)
                system(f"taskkill /IM {task}.exe /f")

    @staticmethod
    def greeting():
        current_time = datetime.now()
        if (current_time.hour > 6) and (current_time.hour < 12):
            playsound(r"audio\Good_morning.mp3")
        elif (current_time.hour > 12) and (current_time.hour < 18):
            playsound(r"audio\Good_evening.mp3")
        elif (current_time.hour > 19) and (current_time.hour < 23):
            playsound(r"audio\Good_afternoon.mp3")
        else:
            playsound(r"audio\Greetings_at_night.mp3")

    @staticmethod
    def bye():
        playsound("audio/Goodbye.mp3")
        exit(0)
