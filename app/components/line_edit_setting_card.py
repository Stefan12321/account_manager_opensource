from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import SettingCardGroup, SettingCard, FluentIconBase, ConfigItem, LineEdit


class StretchLineEdit(LineEdit):
    def __init__(self):
        super().__init__()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.old_width = self.width()
        self.setFixedWidth(400)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.setFixedWidth(self.old_width)


class LineEditSettingCard(SettingCard):
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        configItem: ConfigItem
            configuration item operated by the card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.line_edit = StretchLineEdit()
        self.hBoxLayout.addWidget(self.line_edit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)