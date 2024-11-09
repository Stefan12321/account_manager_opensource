from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from main import Window
import sys

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
w = Window()
w.show()
app.exec_()
