
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic

class App(QWidget):
    def __init__(self):
        self.ui = uic.loadUi("gui_pirs.ui")
        self.ui.show()
    def set(self):
        self.ui.start.clicked.connect()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec()