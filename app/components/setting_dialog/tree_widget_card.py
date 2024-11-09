import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QTreeWidgetItem
from qfluentwidgets import CardWidget, BodyLabel, TreeWidget, InfoBar, InfoBarPosition


class TreeWidgetCard(CardWidget):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.vertical_view = QVBoxLayout(self)

        self.label = BodyLabel(label)
        self.tree_widget = TreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.vertical_view.addWidget(self.label)
        self.vertical_view.addWidget(self.tree_widget)


class TreeWidgetPasswordsCard(TreeWidgetCard):
    def __init__(self, label: str, parent=None):
        super().__init__(label, parent)

        self.tree_widget.itemClicked.connect(self.copy_item)

    def copy_item(self, item: QTreeWidgetItem):
        if item.parent():
            InfoBar.success(
                title=item.name,
                content=f"The {item.value} text is copied!",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            pyperclip.copy(item.value)

    def set_data(self, data: dict[str, dict[str, str]]):
        for key in data.keys():
            item = QTreeWidgetItem([key])
            item.name = key
            username = data[key]["username"]
            password = data[key]["password"]
            username_item = QTreeWidgetItem([f'Username: {username}'])
            username_item.name = "Username"
            username_item.value = username
            password_item = QTreeWidgetItem([f'Password: {password}'])
            password_item.name = "Password"
            password_item.value = password
            item.addChildren([
                username_item,
                password_item,
            ])
            self.tree_widget.addTopLevelItem(item)
