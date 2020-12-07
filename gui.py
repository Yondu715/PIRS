import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt
from Assistant import *


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
        self.ui.pushButton.clicked.connect(self.dialog)

        self.settings.dinamic.setMinimum(0)
        self.settings.dinamic.setMaximum(100)
        self.settings.dinamic.setSingleStep(1)
        self.settings.dinamic.setValue(50)

    def dialog(self):
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
