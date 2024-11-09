from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtCore import Qt
import os

from qfluentwidgets import isDarkTheme
from qframelesswindow import StandardTitleBar

from app.components.style_sheet import StyleSheet


class BaseFlyoutDialog(QDialog):
    BORDER_WIDTH = 5

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._isResizeEnabled = True
        self._init_layout()
        self._init_titlebar()
        self._setup_style()
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def _init_layout(self):
        self.vBoxLayout = QVBoxLayout(self)

    def _init_titlebar(self):
        self.title_bar = StandardTitleBar(self)
        self.title_bar.setParent(self)
        self.title_bar.titleLabel.setText(self.title)
        self.setContentsMargins(0, 40, 0, 20)
        self.title_bar.raise_()

    def _setup_style(self):
        if isDarkTheme():
            style = StyleSheet(f"{os.environ['ACCOUNT_MANAGER_PATH_TO_RESOURCES']}/dark/settings_dialog.qss")
            self.bg_color = QColor(32, 32, 32)
            self.title_bar.closeBtn._normalColor = QColor(255, 255, 255)
            self.title_bar.maxBtn._normalColor = QColor(255, 255, 255)
            self.title_bar.maxBtn._hoverColor = QColor(255, 255, 255)
            self.title_bar.maxBtn._hoverBgColor = QColor(55, 55, 55)

            self.title_bar.minBtn._normalColor = QColor(255, 255, 255)
            self.title_bar.minBtn._hoverColor = QColor(255, 255, 255)
            self.title_bar.minBtn._hoverBgColor = QColor(55, 55, 55)

            self.title_bar.titleLabel.setStyleSheet("""
                QLabel{
                    background: transparent;
                    color: rgb(255, 255, 255);
                    font: 13px 'Segoe UI';
                    padding: 0 4px
                }
            """)
            self.title_bar.setIcon(QIcon(f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/logo.svg'))

        else:
            style = StyleSheet(f"{os.environ['ACCOUNT_MANAGER_PATH_TO_RESOURCES']}/light/settings_dialog.qss")
            self.bg_color = QColor(243, 243, 243)

            self.title_bar.minBtn._hoverBgColor = QColor(218, 218, 218)
            self.title_bar.maxBtn._hoverBgColor = QColor(218, 218, 218)

            self.title_bar.closeBtn._normalBgColor = QColor(243, 243, 243)
            self.title_bar.minBtn._normalBgColor = QColor(243, 243, 243)
            self.title_bar.maxBtn._normalBgColor = QColor(243, 243, 243)
        self.setStyleSheet(str(style))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.title_bar.resize(self.width(), self.title_bar.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawRoundedRect(self.rect(), 10, 10)