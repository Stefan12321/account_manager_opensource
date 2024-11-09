import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import ProgressBar, BodyLabel

if sys.platform == 'win32':
    from app.components.flyout_dialog import BaseFlyoutDialog
else:
    from app.components.flyout_dialog_linux import BaseFlyoutDialog

class ProgressBarDialog(BaseFlyoutDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.progress_bar = ProgressBar()
        self.vBoxLayout.addWidget(self.progress_bar)

    @QtCore.pyqtSlot(int)
    def progress(self, value: int):
        self.progress_bar.setValue(value)

    @QtCore.pyqtSlot()
    def exit(self):
        self.close()


class FilesProgressBarDialog(ProgressBarDialog):
    def __init__(self, label: str, parent=None):
        super().__init__(label, parent)
        self.label_file = BodyLabel()
        self.vBoxLayout.insertWidget(0, self.label_file)

    def _init_layout(self):
        super()._init_layout()
        self.resize(300, 100)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    @QtCore.pyqtSlot(str)
    def filename(self, name: str):
        self.label_file.setText(name)
