import csv
import logging
import os
import queue
import threading
from typing import List, Dict, Any

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QToolTip, QDesktopWidget, QLayout

from dialogs.settings_dialog import Ui_Dialog as Ui_settings_dialog
from dialogs.settings_main import Ui_Dialog as Ui_main_settings_dialog
from .serializer import Config, MainConfig

DEBUG = (os.getenv("DEBUG_ACCOUNT_MANAGER", default='False') == 'True')

settings_file = os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"]
base_dir = os.environ["ACCOUNT_MANAGER_BASE_DIR"]


class QlistExtensionsWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, parent=None):
        super(QlistExtensionsWidgetItem, self).__init__(parent)
        self.extension_name = None


class SettingsDialog(Ui_settings_dialog, QtWidgets.QDialog):
    def __init__(self, _queue: queue.Queue, logger: logging.Logger, parent=None, account_name=""):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self._queue = _queue
        self.logger = logger
        if DEBUG:
            self.CheckGSButton = QtWidgets.QPushButton(self)
            self.CheckGSButton.setStyleSheet("")
            self.CheckGSButton.setObjectName("CheckGSButton")
            self.verticalLayout.addWidget(self.CheckGSButton)
            self.CheckGSButton.setText("CheckGS")

        self.items = []
        self.name = account_name
        self.config = self.setup_config()
        self.main_config = self.setup_main_config()
        extension_list = os.listdir(fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\extension')
        for extension_name in extension_list:
            text = extension_name
            item = QlistExtensionsWidgetItem()
            item.setText(text)
            item.extension_name = extension_name
            item.setCheckState(QtCore.Qt.Unchecked)
            self.items.append(item)
            self.listWidgetExtensions.addItem(item)
        self.default_values = {
            "extensions": {},
            "line_number": "",
            "proxy": "",
            "latitude": "",
            "longitude": "",
            "default_new_tab": ""
        }
        self.private_fields = [self.search_clean_ip_pushButton,
                               self.lineEdit_line_number,
                               self.label_line_number,
                               self.proxy_id_label,
                               self.proxy_id_lineEdit]
        self.fields: List[Dict[str, Any]] = [
            {"name": "user-agent",
             "field": self.user_agent_line,
             "data_from_config": self.config.get_data_by_key("user-agent", "")
             },
            {"name": "line_number",
             "field": self.lineEdit_line_number,
             "data_from_config": self.config.get_data_by_key("line_number", self.default_values["line_number"])},
            {"name": "proxy",
             "field": self.proxy_id_lineEdit,
             "data_from_config": self.config.get_data_by_key("proxy", self.default_values["proxy"])},
            {"name": "latitude",
             "field": self.latitude_lineEdit,
             "data_from_config": self.config.get_data_by_key("latitude", self.default_values["latitude"])},
            {"name": "longitude",
             "field": self.longitude_lineEdit,
             "data_from_config": self.config.get_data_by_key("longitude", self.default_values["longitude"])},
            {"name": "default_new_tab",
             "field": self.new_tab_lineEdit,
             "data_from_config": self.main_config.get_data_by_key("default_new_tab",
                                                             self.default_values["default_new_tab"])},
        ]

        self._add_functions()
        self._private_buttons()
        self._fill_fields()

    def exec(self) -> int:
        res = super().exec()
        if res:
            self._update_config()
        return res

    def _add_functions(self):
        self.new_tab_pushButton.clicked.connect(self.open_new_tab_with_url)

    def _private_buttons(self):
        for field in self.private_fields:
            field.hide()

    def _fill_fields(self):
        for field in self.fields:
            field["field"].setText(field["data_from_config"])
        extensions = self.config.get_data_by_key("extensions", self.default_values["extensions"])
        for item in self.items:
            if item.extension_name in extensions and extensions[item.extension_name] is True:
                item.setCheckState(QtCore.Qt.Checked)

    def _update_config(self):
        config_update = {}
        for field in self.fields:
            new_data = field["field"].text()
            if new_data != field["data_from_config"]:
                config_update.update({field["name"]: new_data})
        config_update.update({item.extension_name: item.checkState() == QtCore.Qt.Checked for item in self.items})
        self.config.update(config_update)

    def setup_config(self) -> Config:
        self.path = fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\profiles\{self.name}'
        config = Config(fr"{self.path}\config.json")
        return config

    def setup_main_config(self) -> MainConfig:
        main_config = MainConfig(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\settings.json")
        return main_config

    @pyqtSlot(int)
    def handle_message_box_response(self, button):
        if button == QMessageBox.Ok:
            print("User clicked OK")
        else:
            print("User clicked Cancel")

    def open_new_tab_with_url(self):
        url = self.new_tab_lineEdit.text()
        print(url)
        self._queue.put(["open_in_new_tab", url])


class MainSettings(Ui_main_settings_dialog, QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        QToolTip.setFont(QFont('Arial', 10))
        self.col = 0
        self.row = 0
        screen_info = QDesktopWidget().screenGeometry()
        self.screen_height = screen_info.height()

        self.setupUi(self)
        self.pages_list = []
        self.pages_dict = {}
        self.fields = []

        self.resize(400,
                    int(self.screen_height * 0.8))  # TODO this is bad solution for minimize window onstart, need to refactor

    def add_to_scroll_layout(self, layout: QLayout):
        self.scrollLayout.addLayout(layout)

    def update_settings(self, settings: dict) -> dict:
        for field in self.fields:
            match field:
                case QtWidgets.QLineEdit():
                    settings.update({field.objectName(): field.text()})
                case QtWidgets.QCheckBox():
                    settings.update({field.objectName(): field.isChecked()})
                case QtWidgets.QWidget():
                    settings.update({field.objectName(): [child.text() for child in field.children() if
                                                          isinstance(child, QtWidgets.QLineEdit)]})
        return settings

    def read_tooltips(self, path=f"{base_dir}/tooltips.csv") -> dict:
        with open(path, 'r', encoding='utf-8') as csvfile:
            # Create a DictReader object
            csvreader = csv.DictReader(csvfile)
            tooltips = {}
            # Process each row
            for row in csvreader:
                tooltips.update({row['Setting']: row['ToolTip']})
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
                tooltip = tooltips[key]
            except KeyError:
                tooltip = ""
            match key_data:
                case str():
                    self.add_string_field(key, key_data, tooltip)
                case bool():
                    self.add_bool_field(key, key_data, tooltip)
                case int():
                    self.add_string_field(key, str(key_data), tooltip)
                case list():
                    self.add_list_field(key, key_data, tooltip)

    def add_list_field(self, field_name: str, field_data: list, tooltip=""):
        label = QtWidgets.QLabel(self.dialog)
        label.setObjectName(f"{field_name}_label")
        label.setText(field_name.replace("_", " "))
        label.setToolTip(tooltip)
        horizontal_layout_3 = QtWidgets.QHBoxLayout()
        horizontal_layout_3.setObjectName("horizontalLayout_3")
        scroll_area = QtWidgets.QScrollArea(self.dialog)
        scroll_area.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Ukraine))
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        scroll_area.setMinimumHeight(100)
        scroll_area_widget_contents = QtWidgets.QWidget()
        scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 346, 67))
        scroll_area_widget_contents.setObjectName(field_name)
        vertical_layout_2 = QtWidgets.QVBoxLayout(scroll_area_widget_contents)
        vertical_layout_2.setObjectName("verticalLayout_2")

        horizontal_layout_2 = QtWidgets.QHBoxLayout()
        horizontal_layout_2.setObjectName("horizontalLayout_2")
        vertical_layout_2.addLayout(horizontal_layout_2)

        scroll_area.setWidget(scroll_area_widget_contents)
        horizontal_layout_3.addWidget(scroll_area)
        push_button_add_page = QtWidgets.QPushButton(self.dialog)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(push_button_add_page.sizePolicy().hasHeightForWidth())
        push_button_add_page.setSizePolicy(size_policy)
        push_button_add_page.setMaximumSize(QtCore.QSize(30, 30))
        push_button_add_page.setObjectName("pushButton_add_page")
        horizontal_layout_3.addWidget(label)
        horizontal_layout_3.addWidget(push_button_add_page)
        push_button_add_page.setText("+")

        self.add_to_scroll_layout(horizontal_layout_3)
        for item in field_data:
            self.add_one_page_onload(item, scroll_area_widget_contents, vertical_layout_2)

        push_button_add_page.clicked.connect(
            lambda: self.add_one_page_onload("", scroll_area_widget_contents, vertical_layout_2))
        self.fields.append(scroll_area_widget_contents)

    def add_string_field(self, field_name: str, field_data: str, tooltip=""):
        label = QtWidgets.QLabel(self.dialog)
        label.setObjectName(f"{field_name}_label")
        label.setText(field_name.replace("_", " "))
        line_edit = QtWidgets.QLineEdit(self.dialog)
        line_edit.setObjectName(field_name)
        line_edit.setText(field_data)
        line_edit.setToolTip(tooltip)

        self.fields.append(line_edit)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(line_edit)
        self.add_to_scroll_layout(vertical_layout)

    def add_bool_field(self, field_name: str, field_data: str, tooltip=""):
        check_box = QtWidgets.QCheckBox(self.dialog)
        check_box.setObjectName(field_name)
        check_box.setText(field_name.replace("_", " "))
        check_box.setCheckState(Qt.CheckState.Checked if field_data else Qt.CheckState.Unchecked)
        check_box.setToolTip(tooltip)
        self.fields.append(check_box)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(check_box)
        self.add_to_scroll_layout(vertical_layout)

    def add_int_field(self, field_name: str, field_data: str, tooltip=""):
        label = QtWidgets.QLabel(self.dialog)
        label.setObjectName(f"{field_name}_label")
        label.setText(field_name.replace("_", " "))
        spin_box = QtWidgets.QSpinBox(self.dialog)
        spin_box.setObjectName(field_name)
        spin_box.setValue(field_data)
        spin_box.setToolTip(tooltip)
        self.fields.append(spin_box)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(spin_box)
        self.add_to_scroll_layout(vertical_layout)

    def add_box_buttons(self):
        button_box = QtWidgets.QDialogButtonBox(self.dialog)
        button_box.setOrientation(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        button_box.setObjectName("buttonBox")
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(button_box)
        self.verticalLayout.addLayout(vertical_layout)
        button_box.accepted.connect(self.dialog.accept)
        button_box.rejected.connect(self.dialog.reject)

    def add_one_page_onload(self, page_url: str, scroll_area_widget_contents: QtWidgets.QWidget,
                            vertical_layout_2: QtWidgets.QVBoxLayout) -> QtWidgets.QLineEdit:
        try:
            horizontal_layout_2 = QtWidgets.QHBoxLayout()
            horizontal_layout_2.setObjectName("horizontalLayout_2")
            line_edit_add_page = QtWidgets.QLineEdit(scroll_area_widget_contents)
            size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            size_policy.setHorizontalStretch(0)
            size_policy.setVerticalStretch(0)
            size_policy.setHeightForWidth(line_edit_add_page.sizePolicy().hasHeightForWidth())
            line_edit_add_page.setSizePolicy(size_policy)
            line_edit_add_page.setObjectName("lineEditAddPage")
            horizontal_layout_2.addWidget(line_edit_add_page)
            push_button_remove_page = QtWidgets.QPushButton(scroll_area_widget_contents)
            push_button_remove_page.setEnabled(True)
            size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
            size_policy.setHorizontalStretch(0)
            size_policy.setVerticalStretch(0)
            size_policy.setHeightForWidth(push_button_remove_page.sizePolicy().hasHeightForWidth())
            push_button_remove_page.setSizePolicy(size_policy)
            push_button_remove_page.setMaximumSize(QtCore.QSize(30, 30))
            push_button_remove_page.setObjectName("pushButton_remove_page")
            push_button_remove_page.setText("-")
            push_button_remove_page.clicked.connect(lambda: self.deleteItemsOfLayout(horizontal_layout_2))
            horizontal_layout_2.addWidget(push_button_remove_page)
            vertical_layout_2.addLayout(horizontal_layout_2)
            if page_url:
                line_edit_add_page.setText(page_url)

            self.pages_list.append(line_edit_add_page)
            self.pages_dict.update({horizontal_layout_2: line_edit_add_page})
            return line_edit_add_page


        except Exception as e:
            print(e)

    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)

                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())
            try:
                self.pages_dict.pop(layout)
            except Exception as e:
                print(e)
