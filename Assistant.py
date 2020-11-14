from vosk import Model, KaldiRecognizer
import pyaudio
import json
import struct
from math import sqrt
import time


# Settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FPB = 8000
swidth = 2
TIMEOUT_LENGTH = 3
SHORT_NORMALIZE = 1.0 / 32768.0
Threshold = 10
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
        count = len(frame) / swidth
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
                    self.speech_to_text()

    def cmd(self, task):
        pass
