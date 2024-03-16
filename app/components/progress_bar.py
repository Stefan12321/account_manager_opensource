from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget
from qfluentwidgets import ProgressBar, BodyLabel

from app.components.flyout_dialog import BaseFlyoutDialog


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
        self.setGeometry(600, 300, 300, 100)

    @QtCore.pyqtSlot(str)
    def filename(self, name: str):
        self.label_file.setText(name)
