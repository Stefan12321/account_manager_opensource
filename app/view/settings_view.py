# coding:utf-8
import csv

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLayout

from qfluentwidgets import (SettingCardGroup, SwitchSettingCard,NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, qrouter, FluentWindow, NavigationAvatarWidget,
                            ListWidget, CheckBox, LineEdit, BodyLabel, SingleDirectionScrollArea, ToolButton,
                            PrimaryPushButton)
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from accounts_manager_main.serializer import MainConfig
from app.view.base_view import Widget

base_dir = "./"


class OnePageOnLoad(QtWidgets.QHBoxLayout):
    def __init__(self, page_url: str,
                 layout: QtWidgets.QVBoxLayout):
        super().__init__()
        self.layout = layout
        self.setObjectName("horizontalLayout_2")
        self.line_edit_add_page = LineEdit()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.line_edit_add_page.sizePolicy().hasHeightForWidth())
        self.line_edit_add_page.setSizePolicy(size_policy)
        self.line_edit_add_page.setObjectName("lineEditAddPage")
        self.addWidget(self.line_edit_add_page)
        self.push_button_remove_page = ToolButton(FIF.REMOVE)
        self.push_button_remove_page.setEnabled(True)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.push_button_remove_page.sizePolicy().hasHeightForWidth())
        self.push_button_remove_page.setSizePolicy(size_policy)
        self.push_button_remove_page.setMaximumSize(QtCore.QSize(30, 30))
        self.push_button_remove_page.setObjectName("pushButton_remove_page")
        self.push_button_remove_page.clicked.connect(self.deleteItem)
        self.addWidget(self.push_button_remove_page)
        self.layout.insertLayout(len(self.layout.children()) - 1, self)
        if page_url:
            self.line_edit_add_page.setText(page_url)

    def deleteItem(self):
        self.removeWidget(self.push_button_remove_page)
        self.removeWidget(self.line_edit_add_page)
        self.push_button_remove_page.deleteLater()
        self.line_edit_add_page.deleteLater()
        self.layout.removeItem(self)
        self.deleteLater()


class MainSettings(Widget):
    def __init__(self, main_config: MainConfig, parent=None):
        super().__init__("Settings", parent=parent)
        self.main_config = main_config
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = SingleDirectionScrollArea(self, orient=Qt.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()

        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 204))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollLayout.setObjectName("scrollLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        # QToolTip.setFont(QFont('Arial', 10))
        self.col = 0
        self.row = 0
        self.pages_list = []
        self.pages_dict = {}
        self.fields = []
        self.add_settings_fields(self.main_config.config_data)

        self.scrollAreaWidgetContents.setStyleSheet("QWidget{background: transparent}")
        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")

        self.save_button = PrimaryPushButton("Save")
        self.save_button.clicked.connect(lambda: self.update_settings(self.main_config.config_data))
        self.scrollLayout.addWidget(self.save_button)

    def add_to_scroll_layout(self, layout: QLayout):
        self.scrollLayout.addLayout(layout)

    def update_settings(self, settings: dict) -> None:
        for field in self.fields:
            match field:
                case QtWidgets.QLineEdit():
                    settings.update({field.objectName(): field.text()})
                case QtWidgets.QCheckBox():
                    settings.update({field.objectName(): field.isChecked()})
                case QtWidgets.QWidget():
                    settings.update({field.objectName(): [child.text() for child in field.children() if
                                                          isinstance(child, QtWidgets.QLineEdit)]})
        self.main_config.update(settings)
        self.showMessageBox()

    @staticmethod
    def read_tooltips(path=f"{base_dir}/tooltips.csv") -> dict:
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
        label = BodyLabel(field_name.replace("_", " "))
        label.setObjectName(f"{field_name}_label")
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.setObjectName(f"horizontalLayout_{self.col}")
        vertical_layout.addWidget(label)
        widget_contents = QtWidgets.QFrame()
        widget_contents.setGeometry(QtCore.QRect(0, 0, 346, 67))
        widget_contents.setObjectName(field_name)
        widget_contents.setStyleSheet("""
        QFrame{
        border: 1px solid gray;
        border-radius: 10px;
        }
        """)
        vertical_layout_1 = QtWidgets.QVBoxLayout(widget_contents)
        vertical_layout_1.setObjectName(f"verticalLayout_{self.row}")

        horizontal_layout_2 = QtWidgets.QHBoxLayout()
        horizontal_layout_2.setObjectName(f"horizontalLayout_2_{self.row}")
        vertical_spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        horizontal_spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                       QtWidgets.QSizePolicy.Minimum)

        vertical_layout_1.addLayout(horizontal_layout_2)

        vertical_layout.addWidget(widget_contents)
        push_button_add_page = ToolButton(FIF.ADD)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(push_button_add_page.sizePolicy().hasHeightForWidth())
        push_button_add_page.setSizePolicy(size_policy)
        push_button_add_page.setMaximumSize(QtCore.QSize(30, 30))
        push_button_add_page.setMinimumSize(QtCore.QSize(30, 30))
        push_button_add_page.setObjectName("pushButton_add_page")

        horizontal_layout_4 = QtWidgets.QHBoxLayout()
        horizontal_layout_4.setObjectName(f"horizontalLayout_4_{self.row}")

        horizontal_layout_4.addItem(horizontal_spacer_item)
        horizontal_layout_4.addWidget(push_button_add_page)

        self.add_to_scroll_layout(vertical_layout)
        for item in field_data:
            self.add_one_page_onload(item, vertical_layout_1)

        push_button_add_page.clicked.connect(
            lambda: self.add_one_page_onload("", vertical_layout_1))
        self.fields.append(widget_contents)
        vertical_layout_1.addLayout(horizontal_layout_4)
        vertical_layout_1.addItem(vertical_spacer_item)

    def add_string_field(self, field_name: str, field_data: str, tooltip=""):
        label = BodyLabel(field_name.replace("_", " "))
        label.setObjectName(f"{field_name}_label")
        line_edit = LineEdit()
        line_edit.setPlaceholderText(field_name.replace("_", " "))
        line_edit.setObjectName(field_name)
        line_edit.setText(field_data)
        line_edit.setToolTip(tooltip)

        self.fields.append(line_edit)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(line_edit)
        self.add_to_scroll_layout(vertical_layout)

    def add_bool_field(self, field_name: str, field_data: str, tooltip=""):

        check_box = CheckBox(field_name.replace("_", " "))
        check_box.setObjectName(field_name)
        check_box.setChecked(True if field_data else False)
        check_box.setToolTip(tooltip)
        self.fields.append(check_box)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(check_box)
        self.add_to_scroll_layout(vertical_layout)

    def add_int_field(self, field_name: str, field_data: str, tooltip=""):
        label = QtWidgets.QLabel(self)
        label.setObjectName(f"{field_name}_label")
        label.setText(field_name.replace("_", " "))
        spin_box = QtWidgets.QSpinBox(self)
        spin_box.setObjectName(field_name)
        spin_box.setValue(field_data)
        spin_box.setToolTip(tooltip)
        self.fields.append(spin_box)
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(label)
        vertical_layout.addWidget(spin_box)
        self.add_to_scroll_layout(vertical_layout)

    def add_one_page_onload(self, page_url: str,
                            vertical_layout_2: QtWidgets.QVBoxLayout) -> QtWidgets.QLineEdit:
        try:
            one_page_onload = OnePageOnLoad(page_url, vertical_layout_2)

            self.pages_list.append(one_page_onload.line_edit_add_page)
            self.pages_dict.update({one_page_onload: one_page_onload.line_edit_add_page})
            return one_page_onload.line_edit_add_page


        except Exception as e:
            print(e)

    def showMessageBox(self):
        w = MessageBox(
            'Main setting updated',
            '',
            self
        )
        w.yesButton.setText('OK')
        w.cancelButton.hide()
        w.contentLabel.hide()
        w.buttonLayout.insertStretch(1)
        w.exec()
