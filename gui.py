import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic
from Assistant import *

class App(QWidget):
    def __init__(self):
        self.Pirs = Assistant()
        self.ui = uic.loadUi("gui_pirs.ui")
        self.ui.show()

        self.ui.start.clicked.connect(self.Pirs.voice_activation())


if __name__ == '__main__':
    Assistant.greeting()
    app = QApplication(sys.argv)
    ex = App()
    app.exec()