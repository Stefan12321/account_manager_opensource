import logging
import os
import threading
from typing import Any

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidgetItem
from qfluentwidgets import FluentIcon, ToolTipFilter, ToolTipPosition

from app.common.accounts_manager_main.serializer import MainConfig, Config

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])
if main_config.config_data["version"]["values"]["private"] is True:
    from account_manager_private_part.app.components.settings_dialog import SettingsDialogPrivate as SettingsDialog
else:
    from app.components.settings_dialog import SettingsDialog
from app.components.one_accout_line_widget import Ui_Form


class QWidgetOneAccountLine(QWidget, Ui_Form):
    locals_signal = pyqtSignal(dict)

    def __init__(self, name: str, main_config: MainConfig, logger: logging.Logger, index: int, parent=None):
        super(QWidgetOneAccountLine, self).__init__(parent)

        self.is_animation_running = None
        self.index = index
        self.logger = logger
        self.main_config = main_config
        self.name = name
        self.path = fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\profiles\{self.name}'
        self._queue = None
        self.locals = None
        self.locals_signal.connect(self.set_locals)

        self.setupUi(self)
        self.settings_button.setIcon(FluentIcon.SETTING)
        self.settings_button.clicked.connect(self.open_settings)
        self.stop_animation()
        self.browser_icon.setIcon(QIcon(f'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/app/resource/Google_Chrome_icon.svg'))
        if main_config.config_data["accounts_tooltips"]:
            self.setToolTips()
            self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))

    def setToolTips(self):
        config = Config(fr"{self.path}\config.json")
        self.setToolTip(str(config))

    def open_settings(self):
        dlg = SettingsDialog(_queue=self._queue,
                             logger=self.logger,
                             main_config=self.main_config,
                             account_name=self.name,
                             browser_locals=self.locals)
        dlg.show()
        dlg.exec()

    def set_account_name(self, name: str):
        self.name = name
        self.account_name_label.setText(name)

    def set_locals(self, _locals: dict[str, Any]):
        self.locals = _locals

    def enterEvent(self, event):
        self.parent().parent()._setHoverRow(self.index)

    def start_animation(self):
        self.running_ring.show()
        self.is_animation_running = True

    def stop_animation(self):
        self.running_ring.hide()
        self.is_animation_running = False


class QListAccountsWidgetItem(QListWidgetItem):
    def __init__(self, name: str, widget: QWidgetOneAccountLine, main_config: MainConfig, parent=None, ):
        super(QListAccountsWidgetItem, self).__init__(parent)
        self.name = name
        self.main_config = main_config
        self.status: bool = False
        self.thread: threading.Thread or None = None
        self.widget = widget
        self.setSizeHint(self.widget.sizeHint())
