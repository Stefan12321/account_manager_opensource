import sys

from PyQt5.QtWidgets import QHBoxLayout
from qfluentwidgets import PrimaryPushButton, PushButton

if sys.platform == 'win32':
    from app.components.flyout_dialog import BaseFlyoutDialog
else:
    from app.components.flyout_dialog_linux import BaseFlyoutDialog


class FlyoutDialogWithButtons(BaseFlyoutDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self._init_control_buttons()

    def _init_control_buttons(self):
        self.control_buttons_horizontal_layout = QHBoxLayout()

        self.accept_button = PrimaryPushButton("OK")
        self.cancel_button = PushButton("Cancel")

        self.accept_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)

        self.control_buttons_horizontal_layout.addStretch(1)
        self.control_buttons_horizontal_layout.addWidget(self.accept_button)
        self.control_buttons_horizontal_layout.addWidget(self.cancel_button)

        self.vBoxLayout.addLayout(self.control_buttons_horizontal_layout)
        self.accept_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
