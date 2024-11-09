from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit


class CreateAccountDialog(MessageBoxBase):
    """ Custom message box """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Create new account')
        self.new_account_line_edit = LineEdit()

        self.new_account_line_edit.setPlaceholderText('Enter account name')
        self.new_account_line_edit.setClearButtonEnabled(True)

        # Add components to the layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.new_account_line_edit)

        # Set the minimum width of the dialog box
        self.widget.setMinimumWidth(350)
