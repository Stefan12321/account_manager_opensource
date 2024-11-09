from typing import Union

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy
from qfluentwidgets import SettingCard, FluentIconBase, ConfigItem, LineEdit, ToolButton, BodyLabel

from qfluentwidgets import FluentIcon

ONE_LINE_HEIGHT = 40


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
        self.push_button_remove_page = ToolButton(FluentIcon.REMOVE)
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
        self.parent().parent().parent().setFixedHeight(self.parent().parent().parent().height() - ONE_LINE_HEIGHT)
        # self.parent().parent().parent().parent().setFixedHeight(self.parent().parent().parent().parent().height() - ONE_LINE_HEIGHT)
        self.layout.removeItem(self)
        self.deleteLater()


class ListSettingsCard(SettingCard):
    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title,
                 field_data: list, pages_list: list, pages_dict: dict, content=None, parent=None):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        configItem: ConfigItem
            configuration item operated by the card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.pages_list = pages_list
        self.pages_dict = pages_dict
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.setObjectName("vertical_layout")
        self.widget_contents = QtWidgets.QFrame()
        self.widget_contents.setGeometry(QtCore.QRect(0, 0, 346, 67))
        self.widget_contents.setFixedWidth(350)
        self.widget_contents.setObjectName(title)
        self.widget_contents.setStyleSheet("""
         QFrame{
         border: 1px solid gray;
         border-radius: 10px;
         }
         """)
        vertical_layout_1 = QtWidgets.QVBoxLayout(self.widget_contents)
        vertical_layout_1.setObjectName("verticalLayout_1")

        horizontal_layout_2 = QtWidgets.QHBoxLayout()
        horizontal_layout_2.setObjectName("horizontalLayout_2")
        vertical_spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        horizontal_spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                       QtWidgets.QSizePolicy.Minimum)

        vertical_layout_1.addLayout(horizontal_layout_2)

        vertical_layout.addWidget(self.widget_contents)
        push_button_add_page = ToolButton(FluentIcon.ADD)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(push_button_add_page.sizePolicy().hasHeightForWidth())
        push_button_add_page.setSizePolicy(size_policy)
        push_button_add_page.setMaximumSize(QtCore.QSize(30, 30))
        push_button_add_page.setMinimumSize(QtCore.QSize(30, 30))
        push_button_add_page.setObjectName("pushButton_add_page")

        horizontal_layout_4 = QtWidgets.QHBoxLayout()
        horizontal_layout_4.setObjectName("horizontalLayout_4")

        horizontal_layout_4.addItem(horizontal_spacer_item)
        horizontal_layout_4.addWidget(push_button_add_page)

        self.hBoxLayout.addLayout(vertical_layout)
        self.hBoxLayout.addSpacing(16)
        for item in field_data:
            self.add_one_page_onload(item, vertical_layout_1)

        push_button_add_page.clicked.connect(
            lambda: self.add_one_page_onload("", vertical_layout_1))
        vertical_layout_1.addLayout(horizontal_layout_4)
        vertical_layout_1.addItem(vertical_spacer_item)

    def add_one_page_onload(self, page_url: str,
                            vertical_layout_2: QtWidgets.QVBoxLayout) -> QtWidgets.QLineEdit:
        try:
            one_page_onload = OnePageOnLoad(page_url, vertical_layout_2)
            self.setFixedHeight(self.height() + ONE_LINE_HEIGHT)
            self.pages_list.append(one_page_onload.line_edit_add_page)
            self.pages_dict.update({one_page_onload: one_page_onload.line_edit_add_page})

            return one_page_onload.line_edit_add_page


        except Exception as e:
            print(e)
