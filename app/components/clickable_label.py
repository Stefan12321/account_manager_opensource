from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import CaptionLabel, LineEdit, PushButton


class ClickableLabel(QWidget):
    name_changed = pyqtSignal(str, str)

    def __init__(self, text, parent=None):
        super(ClickableLabel, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = CaptionLabel(text)
        self.edit = LineEdit()
        self.edit.setPlaceholderText("Enter new text")
        self.ok_button = PushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.ok_button)
        self.edit.hide()
        self.ok_button.hide()
        self.is_editing = False

    def mousePressEvent(self, event):
        if not self.is_editing:
            self.label.hide()
            self.edit.setText(self.label.text())
            self.edit.show()
            self.ok_button.show()
            self.is_editing = True

    def on_ok_clicked(self):
        new_text = self.edit.text()
        old_text = self.label.text()
        if new_text != old_text:
            self.label.setText(new_text)
            self.name_changed.emit(old_text, new_text)
        self.edit.hide()
        self.ok_button.hide()
        self.label.show()
        self.is_editing = False

    def setText(self, text: str):
        self.label.setText(text)
