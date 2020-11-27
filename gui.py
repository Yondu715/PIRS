import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QMainWindow
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
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
        self.ui.start.clicked.connect(self.fix_label)
        self.thread.start()
        self.ui.pushButton.clicked.connect(self.Dialog)

    def Dialog(self):
        self.ui = uic.loadUi("settings.ui")
        self.ui.show()
        self.thread = QtCore.QThread()

    def check_microfone(self):
        microphone_list = pyaudio.PyAudio().get_device_count()

        if microphone_list == []:
            description = 'Микрофоны не были обноружены в системе'
        else:
            description = 'Микрофон подключен'
        QMessageBox.about(self, 'Микрофоны в системе', str(description))

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
