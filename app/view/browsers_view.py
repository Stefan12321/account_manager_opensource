from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem
from qfluentwidgets import ListWidget

from app.view.base_view import Widget


class BrowserListWidget(Widget):
    def __init__(self, parent=None):
        super().__init__("browser-list", parent=parent)
        self.setObjectName("BrowserListWidget")
        self.hBoxLayout = QHBoxLayout(self)
        self.listWidget = ListWidget()
        stands = [
            'Star Platinum', 'Green Emperor', "Heaven's Door", "King Crimson",
            'Silver Chariot', 'Crazy Diamond', "Killer Queen", "Dirty Deeds Done Dirt Cheap",
            "Hermit Purple", "Gold Experience", "The World", "King Nothing",
            "Scary Monsters", "Man's World", "Love Deluxe", "Tusk Act 4",
            "Ball Breaker", "Sex Pistols", 'D4C • Love Train', "Made in Heaven",
            "Soft & Wet", "Paisley Park", "Hey Ya!", "Walking Heart",
            "Frost Traveler", "November Rain", "Flirting Master", "Wait a Moment"
        ]

        # Add list items
        for stand in stands:
            item = QListWidgetItem(stand)
            item.setIcon(QIcon('app/resource/Google_Chrome_icon.svg'))
            self.listWidget.addItem(item)
        self.hBoxLayout.addWidget(self.listWidget, 1)
