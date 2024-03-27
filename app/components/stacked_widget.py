from typing import List

from PyQt5.QtWidgets import QStackedWidget

from app.components.browser_tabs import BrowsersTab


class StackedWidget(QStackedWidget):
    def get_widgets(self) -> List[BrowsersTab]:
        return [self.widget(index) for index in range(self.count())]
