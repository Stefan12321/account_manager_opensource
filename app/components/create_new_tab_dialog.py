from app.components.create_account_dialog import CreateAccountDialog


class CreateTabDialog(CreateAccountDialog):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel.setText("Create new tab")
