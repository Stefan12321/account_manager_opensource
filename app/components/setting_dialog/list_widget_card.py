from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QListWidgetItem
from qfluentwidgets import CardWidget, BodyLabel, ListWidget


class ListWidgetCard(CardWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.vertical_view = QVBoxLayout(self)
        self.label = BodyLabel(name)
        self.list_widget = ListWidget()
        self.vertical_view.addWidget(self.label)
        self.vertical_view.addWidget(self.list_widget)

    def set_data(self, data: dict[str, bool]):
        for key in data.keys():
            item = QListWidgetItem(key)
            item.setCheckState(Qt.Checked if data[key] else Qt.Unchecked)
            self.list_widget.addItem(item)

    def get_data(self) -> dict[str, bool]:
        data = {}
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            data[item.text()] = True if item.checkState() == Qt.Checked else False
        return data

    def get_checked(self) -> list[QListWidgetItem]:
        item_list: list[QListWidgetItem] = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                item_list.append(item)

        return item_list
