from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import CardWidget, BodyLabel, LineEdit


class LineEditCard(CardWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.vertical_view = QVBoxLayout(self)
        self.label = BodyLabel(name)
        self.lineEdit = LineEdit()
        self.vertical_view.addWidget(self.label)
        self.vertical_view.addWidget(self.lineEdit)

    def set_data(self, data: str):
        self.lineEdit.setText(data)

    def get_data(self) -> str:
        return self.lineEdit.text()
