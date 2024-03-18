from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import CardWidget, BodyLabel

from app.common.pyqtconsole import PythonConsole


class PythonConsoleCard(CardWidget):
    def __init__(self, browser_locals, parent=None):
        super().__init__(parent)
        self.locals = browser_locals
        self.vertical_view = QVBoxLayout(self)
        self.console_label = BodyLabel(" Python Console")
        console = PythonConsole(locals=self.locals)
        console.eval_in_thread()
        self.vertical_view.addWidget(self.console_label)
        self.vertical_view.addWidget(console)
