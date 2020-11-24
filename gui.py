import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5 import uic, QtCore
from Assistant import *

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("gui_pirs.ui")
        self.ui.show()
        self.thread = QtCore.QThread()
        self.Pirs = Assistant()
        self.Pirs.moveToThread(self.thread)
        self.ui.start.clicked.connect(self.Pirs.voice_activation)
        self.thread.start()
        self.ui.pushButton.clicked.connect(self.check_microfone)

    def check_microfone(self):
        microphone_list = pyaudio.PyAudio().get_device_count()

        if microphone_list == []:
            description = 'Микрофоны не были обноружены в системе'
        else:
            descriprion = microphone_list
        QMessageBox.about(self,'Микрофоны в системе',str(descriprion))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    Assistant.greeting()
    app.exec()