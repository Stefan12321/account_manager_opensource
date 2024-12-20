import logging
import os
import queue
import sys

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from app.common.settings.serializer import Config, MainConfig
from app.components.flyout_dialog_with_buttons import FlyoutDialogWithButtons
from app.components.setting_dialog.line_edit_card import LineEditCard
from app.components.setting_dialog.line_edit_card_with_button import (
    LineEditCardWithButton,
)
from app.components.setting_dialog.list_widget_card import ListWidgetCard
from app.components.setting_dialog.python_console_card import PythonConsoleCard
from app.components.setting_dialog.tree_widget_card import TreeWidgetPasswordsCard

if sys.platform == "win32":
    from app.common.password_decryptor import do_decrypt_dict


class BaseSettingsDialog(FlyoutDialogWithButtons):
    def accept(self):
        self._update_config()
        super().accept()

    def _update_config(self):
        data = {
            "user-agent": self.user_agent_card.get_data(),
            "latitude": self.latitude_card.get_data(),
            "longitude": self.longitude_card.get_data(),
            "extensions": self.extensions_card.get_data(),
        }
        self.config.update(data)

    def _fill_fields(self):
        self.user_agent_card.set_data(
            self.config.config_data["user-agent"]
            if "user-agent" in self.config.config_data
            else ""
        )
        self.extensions_card.set_data(
            self.config.config_data["extensions"]
            if "extensions" in self.config.config_data
            else {}
        )
        self.open_in_new_tab_card.set_data(
            str(self.config.config_data["default_new_tab"])
            if "default_new_tab" in self.config.config_data
            else ""
        )
        if sys.platform == "win32":
            self.passwords_card.set_data(self.passwords if self.passwords else {})
        self.longitude_card.set_data(
            self.config.config_data["longitude"]
            if "longitude" in self.config.config_data
            else ""
        )
        self.latitude_card.set_data(
            self.config.config_data["latitude"]
            if "latitude" in self.config.config_data
            else ""
        )

    def _update_extensions(self):
        extensions = self.config.config_data["extensions"]
        keys = list(self.config.config_data["extensions"])
        for extension in os.listdir(
            rf'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/extension'
        ):
            if extension in keys:
                keys.remove(extension)
            else:
                extensions.update({extension: False})
        if len(keys) > 0:
            for key in keys:
                extensions.pop(key, None)
        self.config.update({"extensions": extensions})

    def open_new_tab_with_url(self):
        url = self.open_in_new_tab_card.get_data()
        self._queue.put(["open_in_new_tab", url])


class SettingsDialog(BaseSettingsDialog):
    def __init__(
        self,
        _queue: queue.Queue,
        logger: logging.Logger,
        main_config: MainConfig,
        account_name: str,
        browser_locals,
        parent=None,
    ):
        self.locals = browser_locals
        self.account_name = account_name
        self.logger = logger
        self._queue = _queue
        self.path = (
            f'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/profiles/{self.account_name}'
        )
        if sys.platform == "win32":
            self.passwords = do_decrypt_dict(self.path)
        self.config = Config(f"{self.path}/config.json")
        self.main_config = main_config
        super().__init__(f"Settings {self.account_name}", parent)
        self._update_extensions()
        self._fill_fields()

    def _init_layout(self):
        super()._init_layout()
        self.hBoxLayout = QHBoxLayout()
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self.user_agent_card = LineEditCard("User agent")

        self.extensions_card = ListWidgetCard("Extensions")
        self.open_in_new_tab_card = LineEditCardWithButton(
            "Open new tab with url", "OPEN"
        )
        self.open_in_new_tab_card.connect_button(self.open_new_tab_with_url)

        self.latitude_longitude_horizontal_view = QHBoxLayout()
        self.latitude_card = LineEditCard("Latitude")
        self.longitude_card = LineEditCard("Longitude")
        self.latitude_longitude_horizontal_view.addWidget(self.latitude_card)
        self.latitude_longitude_horizontal_view.addWidget(self.longitude_card)
        self.python_console_card = PythonConsoleCard(self.locals)

        self.left_column.addWidget(self.user_agent_card)
        self.left_column.addWidget(self.extensions_card)

        self.right_column.addLayout(self.latitude_longitude_horizontal_view)
        self.right_column.addWidget(self.open_in_new_tab_card)
        if self.main_config.config_data["python_console"]:
            self.right_column.addWidget(self.python_console_card)

        if sys.platform == "win32":
            self.passwords_card = TreeWidgetPasswordsCard("Passwords")
            self.left_column.addWidget(self.passwords_card)

        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.hBoxLayout.addLayout(self.left_column)
        self.hBoxLayout.addLayout(self.right_column)
        self.setGeometry(200, 200, 800, 600)


class AllSettingsDialog(BaseSettingsDialog):
    def __init__(
        self,
        main_config: MainConfig,
        account_names: list[str],
        parent=None,
    ):
        self.account_names = account_names
        self.paths = [
            f'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/profiles/{account_name}'
            for account_name in account_names
        ]
        self.configs = [Config(f"{path}/config.json") for path in self.paths]
        self.config = self.configs[0]
        self.main_config = main_config
        super().__init__(f"Settings {self.account_names}", parent)
        self._update_extensions()
        self._fill_fields()

    def _update_config(self):
        data = {
            "extensions": self.extensions_card.get_data(),
        }
        if self.user_agent_card.get_data() != self.config.config_data["user-agent"]:
            data.update({"user-agent": self.user_agent_card.get_data()})
        for config in self.configs:
            config.update(data)

    def _init_layout(self):
        super()._init_layout()
        self.hBoxLayout = QHBoxLayout()
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        self.user_agent_card = LineEditCard("User agent")

        self.extensions_card = ListWidgetCard("Extensions")

        self.left_column.addWidget(self.user_agent_card)
        self.left_column.addWidget(self.extensions_card)

        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.hBoxLayout.addLayout(self.left_column)
        self.hBoxLayout.addLayout(self.right_column)
        self.setGeometry(200, 200, 800, 600)

    def _fill_fields(self):
        self.user_agent_card.set_data(
            self.config.config_data["user-agent"]
            if "user-agent" in self.config.config_data
            else ""
        )
        self.extensions_card.set_data(
            self.config.config_data["extensions"]
            if "extensions" in self.config.config_data
            else {}
        )
