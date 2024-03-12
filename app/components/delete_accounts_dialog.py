from qfluentwidgets import MessageBoxBase, SubtitleLabel

from app.components.account_item import QListAccountsWidgetItem


class DeleteAccountDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, accounts_names_to_delete: list[QListAccountsWidgetItem], parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(
            f"Are y sure you want to delete accounts: {[i.name for i in accounts_names_to_delete]}")
        self.viewLayout.addWidget(self.titleLabel)