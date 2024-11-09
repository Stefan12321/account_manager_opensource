from PyQt5.QtWidgets import QTextBrowser, QVBoxLayout
from qfluentwidgets import CardWidget, BodyLabel


class TextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)


class TextBrowserCard(CardWidget):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.vertical_view = QVBoxLayout(self)

        self.label = BodyLabel(label)
        self.text_browser = TextBrowser()

        self.vertical_view.addWidget(self.label)
        self.vertical_view.addWidget(self.text_browser)

    def set_data(self, data: str):
        self.text_browser.setText(data)
