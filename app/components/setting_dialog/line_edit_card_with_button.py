from typing import Callable

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import CardWidget, BodyLabel, LineEdit, PushButton


class LineEditCardWithButton(CardWidget):
    def __init__(self, label: str, button_label: str, parent=None):
        super().__init__(parent)
        self.vertical_view = QVBoxLayout(self)
        self.horizontal_view = QHBoxLayout()
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self.horizontal_view.addLayout(self.left_column)
        self.horizontal_view.addLayout(self.right_column)

        self.label = BodyLabel(label)
        self.line_edit = LineEdit()
        self.button = PushButton()
        self.button.setText(button_label)

        self.vertical_view.addWidget(self.label)
        self.left_column.addWidget(self.line_edit)

        self.right_column.addWidget(self.button)

        self.vertical_view.addLayout(self.horizontal_view)

    def set_data(self, data: str):
        self.line_edit.setText(data)

    def get_data(self) -> str:
        return self.line_edit.text()

    def connect_button(self, func: Callable):
        self.button.clicked.connect(func)
