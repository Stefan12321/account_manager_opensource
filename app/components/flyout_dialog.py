import os
from ctypes.wintypes import MSG, LPRECT
from ctypes import cast

import win32con
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QCursor, QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout
from qfluentwidgets import PushButton, isDarkTheme, \
    PrimaryPushButton
from qframelesswindow import StandardTitleBar
from qframelesswindow.utils.win32_utils import Taskbar
from qframelesswindow.utils import win32_utils as win_utils
from qframelesswindow.windows import LPNCCALCSIZE_PARAMS, AcrylicWindow, WindowsWindowEffect
from app.components.style_sheet import StyleSheet


class BaseFlyoutDialog(QDialog):
    BORDER_WIDTH = 5

    def __init__(self, title: str, parent=None):

        super().__init__(parent)
        self.title = title
        self._isResizeEnabled = True
        self.windowEffect = WindowsWindowEffect(self)
        self.updateFrameless()
        self._init_layout()
        self._init_titlebar()
        self._setup_style()

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

    def updateFrameless(self):
        """ update frameless window """
        if not win_utils.isWin7():
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        elif self.parent():
            self.setWindowFlags(self.parent().windowFlags() | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)

        # add DWM shadow and window animation
        self.windowEffect.addWindowAnimation(self.winId())
        if not isinstance(self, AcrylicWindow):
            self.windowEffect.addShadowEffect(self.winId())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.title_bar.resize(self.width(), self.title_bar.height())

    def nativeEvent(self, eventType, message):
        """ Handle the Windows message """
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        if msg.message == win32con.WM_NCHITTEST and self._isResizeEnabled:
            pos = QCursor.pos()
            xPos = pos.x() - self.x()
            yPos = pos.y() - self.y()
            w = self.frameGeometry().width()
            h = self.frameGeometry().height()

            # fixes issue https://github.com/zhiyiYo/PyQt-Frameless-Window/issues/98
            bw = 0 if win_utils.isMaximized(msg.hWnd) or win_utils.isFullScreen(msg.hWnd) else self.BORDER_WIDTH
            lx = xPos < bw
            rx = xPos > w - bw
            ty = yPos < bw
            by = yPos > h - bw
            if lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif ty:
                return True, win32con.HTTOP
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif rx:
                return True, win32con.HTRIGHT
        elif msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            isMax = win_utils.isMaximized(msg.hWnd)
            isFull = win_utils.isFullScreen(msg.hWnd)

            # adjust the size of client rect
            if isMax and not isFull:
                ty = win_utils.getResizeBorderThickness(msg.hWnd, False)
                rect.top += ty
                rect.bottom -= ty

                tx = win_utils.getResizeBorderThickness(msg.hWnd, True)
                rect.left += tx
                rect.right -= tx

            # handle the situation that an auto-hide taskbar is enabled
            if (isMax or isFull) and Taskbar.isAutoHide():
                position = Taskbar.getPosition(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            result = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, result

        return super().nativeEvent(eventType, message)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawRoundedRect(self.rect(), 10, 10)


class FlyoutDialogWithButtons(BaseFlyoutDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self._init_control_buttons()

    def _init_control_buttons(self):
        self.control_buttons_horizontal_layout = QHBoxLayout()

        self.accept_button = PrimaryPushButton("OK")
        self.cancel_button = PushButton("Cancel")

        self.accept_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)

        self.control_buttons_horizontal_layout.addStretch(1)
        self.control_buttons_horizontal_layout.addWidget(self.accept_button)
        self.control_buttons_horizontal_layout.addWidget(self.cancel_button)

        self.vBoxLayout.addLayout(self.control_buttons_horizontal_layout)
        self.accept_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
