from qfluentwidgets import MessageBoxBase, SubtitleLabel


class WarningDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(text)
        self.viewLayout.addWidget(self.titleLabel)
