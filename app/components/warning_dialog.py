from qfluentwidgets import MessageBoxBase, SubtitleLabel

from app.components.account_item import QListAccountsWidgetItem


class WarningDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(text)
        self.viewLayout.addWidget(self.titleLabel)
