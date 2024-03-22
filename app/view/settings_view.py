# coding:utf-8
import csv
import os
from typing import Dict

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLayout, QWidget, QLabel

from qfluentwidgets import (MessageBox,
                            SingleDirectionScrollArea, Dialog)
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, PrimaryPushSettingCard, ExpandLayout)
from qfluentwidgets import FluentIcon

from app.common.updater.base import get_latest_release
from app.common.updater.update_application import update_application
from app.components.options_settings_card import OptionsSettingCard

from app.common.settings.serializer import MainConfig
from app.components.line_edit_setting_card import LineEditSettingCard
from app.components.list_setting_card import ListSettingsCard
from app.view.base_view import Widget

base_dir = "./"


class MainSettings(Widget):
    def __init__(self, app_version: str, main_config: MainConfig, parent=None):
        super().__init__("Settings", parent=parent)
        self.app_version = app_version
        self.main_config = main_config
        self._init_layout()

    def _init_layout(self):
        self.settingLabel = QLabel("Settings", self)
        self.settingLabel.setObjectName('settingLabel')
        self.settingLabel.move(60, 30)
        self.settingLabel.setFixedWidth(200)
        self.settingLabel.setFixedHeight(50)
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName('scrollWidget')
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = SingleDirectionScrollArea(self, orient=Qt.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 100, 0, 20)
        self.verticalLayout.addWidget(self.scrollArea)
        self.pages_list = []
        self.pages_dict = {}
        self.fields = []
        self.checkbox_group = SettingCardGroup(
            self.tr(""), self.scrollWidget)
        self.lines_group = SettingCardGroup(
            self.tr(""), self.scrollWidget)
        self.lists_group = SettingCardGroup(
            self.tr(""), self.scrollWidget)
        self.about_group = SettingCardGroup(
            self.tr("About"), self.scrollWidget)
        self.add_settings_fields(self.main_config.config_data)
        self.expandLayout.addWidget(self.lists_group)
        self.expandLayout.addWidget(self.lines_group)
        self.expandLayout.addWidget(self.checkbox_group)
        self.expandLayout.addWidget(self.about_group)

        self.save_card = PrimaryPushSettingCard(
            self.tr('Save'),
            FluentIcon.SAVE,
            self.tr('Save settings'),
            "",
            self.about_group
        )
        self.save_card.button.clicked.connect(lambda: self.update_settings(self.main_config.config_data))
        self.about_card = PrimaryPushSettingCard(
            self.tr('Check for updates'),
            FluentIcon.INFO,
            self.tr('About'),
            f"@ Copyrighting 2024, Stefan. Version: {self.app_version}",
            self.about_group
        )
        self.about_card.button.clicked.connect(self.check_for_updates)
        self.about_group.addSettingCard(self.about_card)
        self.verticalLayout.addWidget(self.save_card)

    def add_to_scroll_layout(self, layout: QLayout):
        self.scrollLayout.addLayout(layout)

    def update_settings(self, settings: dict) -> None:
        for field in self.fields:
            match field:
                case LineEditSettingCard():
                    settings.update({field.objectName(): field.line_edit.text()})
                case SwitchSettingCard():
                    settings.update({field.objectName(): field.isChecked()})
                case ListSettingsCard():
                    settings.update({field.objectName(): [child.text() for child in field.widget_contents.children() if
                                                          isinstance(child, QtWidgets.QLineEdit)]})
                case OptionsSettingCard():
                    settings.update({field.objectName(): field.properties_dict})
        resp = self.main_config.update(settings)
        self.show_message_save_settings(resp)

    def read_tooltips(self, path=f"{os.environ['ACCOUNT_MANAGER_PATH_TO_RESOURCES']}/tooltips.csv") -> dict:
        print(self.main_config.config_data["version"]["values"]["private"])
        with open(path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            tooltips = {}
            for row in csvreader:
                tooltips.update({row['Setting']: (row['ToolTip'], row['Icon'])})
        if self.main_config.config_data["version"]["values"]["private"] is True:
            with open(f"{base_dir}/account_manager_private_part/tooltips.csv", 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    tooltips.update({row['Setting']: (row['ToolTip'], row['Icon'])})
        return tooltips

    def add_settings_fields(self, settings: dict):
        def sort_key_by_value_type(item):
            value = settings[item]
            type_order = {
                bool: 2,
                int: 1,
                list: 0,
                str: 1,
            }
            return type_order.get(type(value), 3)

        sorted_keys = sorted(settings, key=sort_key_by_value_type)
        tooltips = self.read_tooltips()
        for key in sorted_keys:
            key_data = settings[key]
            try:
                tooltip, icon = tooltips[key]
            except KeyError:
                tooltip = ""
                icon = ""
            match key_data:
                case str():
                    self.add_string_field(key, key_data, tooltip, icon)
                case bool():
                    self.add_bool_field(key, key_data, tooltip, icon)
                case int():
                    self.add_string_field(key, str(key_data), tooltip, icon)
                case list():
                    self.add_list_field(key, key_data, tooltip, icon)
                case dict():
                    if "type" in key_data and key_data["type"] == "dropdown":
                        self.add_dropdown_field(key, key_data, tooltip, icon)

    def add_list_field(self, field_name: str, field_data: list, tooltip="", icon=""):
        list_field = ListSettingsCard(
            FluentIcon[icon] if icon else FluentIcon.TRANSPARENT,
            self.tr(field_name.replace("_", " ")),
            field_data,
            self.pages_list,
            self.pages_dict,
            self.tr(tooltip),
            self.lists_group
        )
        list_field.setObjectName(field_name)
        self.lists_group.addSettingCard(list_field)
        self.fields.append(list_field)

    def add_string_field(self, field_name: str, field_data: str, tooltip="", icon=""):
        line_edit = LineEditSettingCard(
            FluentIcon[icon] if icon else FluentIcon.TRANSPARENT,
            self.tr(field_name.replace("_", " ")),
            self.tr(tooltip),
            self.lines_group
        )
        line_edit.setObjectName(field_name)
        line_edit.line_edit.setText(field_data)
        self.lines_group.addSettingCard(line_edit)
        self.fields.append(line_edit)

    def add_bool_field(self, field_name: str, field_data: str, tooltip="", icon=""):
        check_box = SwitchSettingCard(
            FluentIcon[icon] if icon else FluentIcon.TRANSPARENT,
            self.tr(field_name.replace("_", " ")),
            self.tr(tooltip),
            None,
            self.checkbox_group
        )
        check_box.setObjectName(field_name)
        check_box.setChecked(True if field_data else False)
        self.fields.append(check_box)
        self.checkbox_group.addSettingCard(check_box)

    def add_dropdown_field(self, field_name: str, field_data: Dict[str, Dict[str, dict[str, bool] | str]], tooltip="",
                           icon=""):
        drop_down = OptionsSettingCard(
            FluentIcon[icon] if icon else FluentIcon.TRANSPARENT,
            self.tr(field_name.replace("_", " ")),
            content=self.tr(tooltip),
            properties_dict=field_data,
            parent=self.lines_group
        )
        drop_down.setObjectName(field_name)
        self.lines_group.addSettingCard(drop_down)
        self.fields.append(drop_down)

    def show_message_save_settings(self, saving_status: bool):
        message = 'Main setting updated' if saving_status else 'Main setting update fail'
        w = MessageBox(
            message,
            '',
            self
        )
        w.yesButton.setText('OK')
        w.cancelButton.hide()
        w.contentLabel.hide()
        w.buttonLayout.insertStretch(1)
        w.exec()

    def check_for_updates(self):
        # TODO  Finish this after build release
        update_application()
        # latest_version, _ = get_latest_release()
        # print(latest_version)
        # w = Dialog("Title", "This is a message notification", self)
        #
        # if w.exec():
        #     print('Confirmed')
        # else:
        #     print('Canceled')
