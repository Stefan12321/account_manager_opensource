# coding:utf-8
import os
import sys

# Check if it built app or not
if getattr(sys, "frozen", False):
    os.environ["ACCOUNT_MANAGER_BASE_DIR"] = os.path.dirname(sys.executable)
    os.environ["ACCOUNT_MANAGER_PATH_TO_CONFIG"] = (
        f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/lib/app/config"
    )
    os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"] = (
        f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/lib/app/resource"
    )
else:
    os.environ["ACCOUNT_MANAGER_BASE_DIR"] = os.path.dirname(os.path.realpath(__file__))
    os.environ["ACCOUNT_MANAGER_PATH_TO_CONFIG"] = (
        f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/app/config"
    )
    os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"] = (
        f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/app/resource"
    )
os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"] = (
    f"{os.environ['ACCOUNT_MANAGER_PATH_TO_CONFIG']}/settings.json"
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout

from qfluentwidgets import (
    NavigationInterface,
    NavigationItemPosition,
    isDarkTheme,
    setTheme,
    Theme,
    setThemeColor,
)
from qframelesswindow import StandardTitleBar
from qfluentwidgets import FluentIcon
from app.common.settings.serializer import MainConfig

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])

from app.view.browsers_view import BrowserListWidget
from app.view.settings_view import MainSettings
from app.common.settings.app_version import APP_VERSION

from app.components.thread_watcher import terminate_thread_watchers




def isWin():
    return sys.platform == "win32"

def isWin11():
    return isWin() and sys.getwindowsversion().build >= 22000


if isWin():
    from qframelesswindow import FramelessWindow as Window
else:
    from qframelesswindow import AcrylicWindow as Window

if isWin11():
    from qframelesswindow.windows import WindowsWindowEffect

class Window(Window):
    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        if isWin11():
            self.windowEffect = WindowsWindowEffect(self)
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        if main_config.config_data["theme"]["values"]["Dark"] is True:
            setTheme(Theme.DARK)
        if main_config.config_data["theme"]["values"]["Light"] is True:
            setTheme(Theme.LIGHT)

        # change the theme color
        setThemeColor("#8caaee")

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        # create sub interface
        self.browser_list_Interface = BrowserListWidget(main_config, self)
        self.settingInterface = MainSettings(APP_VERSION, main_config, self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

        self.addSubInterface(self.browser_list_Interface, FluentIcon.GLOBE, "Browsers")

        # self.addSubInterface(self.about, FIF.INFO, 'About', NavigationItemPosition.BOTTOM)
        self.addSubInterface(
            self.settingInterface,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

        # !IMPORTANT: don't forget to set the default route key if you enable the return button
        # qrouter.setDefaultRouteKey(self.stackWidget, self.musicInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        # set browsers page selected on app start
        self.navigationInterface.setCurrentItem(self.stackWidget.widget(0).objectName())

        # always expand
        # self.navigationInterface.setCollapsible(False)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(
            QIcon(f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/logo.svg')
        )
        self.setWindowTitle("Accounts manager")
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # NOTE: set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)

        self.setQss()

    def addSubInterface(
            self,
            interface,
            icon,
            text: str,
            position=NavigationItemPosition.TOP,
            parent=None,
    ):
        """add sub interface"""
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None,
        )

    def setQss(self):
        color = "dark" if isDarkTheme() else "light"
        with open(
                f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/{color}/style.qss',
                encoding="utf-8",
        ) as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

        # !IMPORTANT: This line of code needs to be uncommented if the return button is enabled
        # qrouter.push(self.stackWidget, widget.objectName())

    def close(self):
        terminate_thread_watchers()
        super().close()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
