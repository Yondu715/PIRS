import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt
from Assistant import *
from subprocess import call

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi(r"gui\gui_pirs.ui")
        self.ui.show()

        self.thread = QtCore.QThread()
        self.Pirs = Assistant()
        self.Pirs.moveToThread(self.thread)
        self.ui.start.clicked.connect(self.Pirs.voice_activation)
        self.ui.start.clicked.connect(self.fix_label)
        self.thread.start()

        self.settings = uic.loadUi(r"gui\settings.ui")
        self.ui.pushButton.clicked.connect(self.show_settings)

        self.settings.dinamic.setMinimum(0)
        self.settings.dinamic.setMaximum(100)
        self.settings.dinamic.setSingleStep(1)
        self.settings.dinamic.setValue(50)
        self.settings.dinamic.valueChanged.connect(self.sliderValue_dinamic)
        self.settings.progressBar_2.setValue(50)

        self.settings.micro.setMinimum(0)
        self.settings.micro.setMaximum(100)
        self.settings.micro.setSingleStep(1)
        self.settings.micro.setValue(50)
        self.settings.micro.valueChanged.connect(self.sliderValue_micro)
        self.settings.progressBar.setValue(50)

        self.settings.ok.clicked.connect(self.ok_settings)

    def sliderValue_dinamic(self):
        self.settings.progressBar_2.setValue(self.settings.dinamic.value())

    def sliderValue_micro(self):
        self.settings.progressBar.setValue(self.settings.micro.value())

    def ok_settings(self):
        self.settings.micro.valueChanged[int].connect(self.func)

    def func(self, value):
        print(value)

    def show_settings(self):
        self.settings.show()

    def fix_label(self):
        self.ui.label_2.setText("Pirs на связи")
        self.ui.label_2.setAlignment(Qt.AlignCenter)
        self.ui.label_2.setFont(QtGui.QFont("MS Shell Dlg 2", 24))
        self.ui.frame.setStyleSheet("background-color: rgb(152, 251, 152)")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    Assistant.greeting()
    app.exec()
