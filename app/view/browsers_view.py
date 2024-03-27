import logging
import os
import queue
import threading
import time
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QStackedWidget
from qfluentwidgets import TabItem

from app.common.settings import serializer
from app.common.settings.serializer import MainConfig
from app.components.account_item import QListAccountsWidgetItem
from app.components.browser_tabs import BrowsersTabBar, BrowsersTab
from app.components.create_new_tab_dialog import CreateTabDialog
from app.components.stacked_widget import StackedWidget
from app.view.base_view import Widget
from app.components.warning_dialog import WarningDialog
from app.common.password_decryptor.passwords_decryptor import do_decrypt

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])

if main_config.config_data["version"]["values"]["opensource"] is True:
    from app.common.browser import WebBrowser

    serializer.APP_VERSION += " opensource"

elif main_config.config_data["version"]["values"]["private"] is True:
    try:
        from account_manager_private_part.private_web_browser import WebBrowserPrivate as WebBrowser
        from account_manager_private_part.app.components.settings_dialog import SettingsDialogPrivate as SettingsDialog

        serializer.APP_VERSION += " private"
    except PermissionError:
        logging.error("You can't use this version of app")
        raise PermissionError
else:
    WarningDialog('Invalid version, set value "version" to "private" or "opensource" in main settings')
    logging.error('Invalid version, set value "version" to "private" or "opensource" in main settings')


class BrowserListWidget(Widget):
    progress_signal = QtCore.pyqtSignal(int)
    progress_exit_signal = QtCore.pyqtSignal()
    progress_filename_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_config: MainConfig, parent=None):
        super().__init__("browser-list", parent=parent)
        self.main_config = main_config
        self.browser_tab_all_accounts = None
        self.base_path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}"
        self.profiles_path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles"
        try:
            self.browsers_names = [item for item in
                                   os.listdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
                                   if os.path.isdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\{item}")]
        except FileNotFoundError:
            os.makedirs(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
            self.browsers_names = []
        self.list_item_arr: List[QListAccountsWidgetItem] = []

        self.setObjectName("BrowserListWidget")

        self.__init_layout()

    def __init_layout(self):
        self.vBoxLayout = QVBoxLayout(self)

        self.browser_list_stacked_widget = StackedWidget(self, objectName='browser_list_stacked_widget')

        self.tabBar = BrowsersTabBar(self.main_config, self)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)
        self.tabBar.currentChanged.connect(self.onTabChanged)

        # init base tab
        logo_svg = 'app/resource/logo.svg'
        self.browser_tab_all_accounts, tab = self.addTab(
            [item for item in os.listdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
             if os.path.isdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\{item}")], "All", "All",
            logo_svg)
        tab.closeButton.hide()

        # init tabs from main_config
        if "tabs" in self.main_config.config_data:
            for tab_name in self.main_config.config_data["tabs"]["values"].keys():
                self.addTab(self.main_config.config_data["tabs"]["values"][tab_name], tab_name, tab_name,
                            logo_svg)

        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.browser_list_stacked_widget)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        self.browser_list_stacked_widget.setCurrentWidget(self.findChild(BrowsersTab, objectName))

    def onTabAddRequested(self):
        dlg = CreateTabDialog(self)
        if dlg.exec():
            text = dlg.new_account_line_edit.text()
            self.addTab([], text, text, 'app/resource/logo.svg', True)

    def addTab(self, browser_names: List[str], routeKey, text, icon, from_user=False) -> tuple[BrowsersTab, TabItem]:
        tab = self.tabBar.addTab(routeKey, text, icon, None, from_user)
        browser_tab = BrowsersTab(self.main_config, browser_names, routeKey, self)
        browser_tab.listWidget.itemClicked.connect(self.item_click)
        if self.browser_tab_all_accounts:
            browser_tab.item_list_updated.connect(self.browser_tab_all_accounts.update_item_list_for_all_browsers)
        tab.dropped_browser.connect(browser_tab.on_tab_dropped_account)
        self.browser_list_stacked_widget.addWidget(browser_tab)
        return browser_tab, tab

    def get_tab_with_name(self, tab_name: str) -> BrowsersTab | None:
        return next(
            (item for item in self.browser_list_stacked_widget.get_widgets() if
             item.get_route_key() == tab_name), None)

    def item_click(self, item: QListAccountsWidgetItem):
        item_widget = self.browser_list_stacked_widget.currentWidget().listWidget.itemWidget(item)
        account_name = item_widget.name
        logger = item_widget.logger
        if item.status is not True:
            _queue = queue.Queue()
            locals_signal = item.widget.locals_signal
            t = threading.Thread(target=self.run_browser, args=(account_name, _queue, logger, locals_signal))
            item.thread = t
            item.widget._queue = _queue
            t.start()
            logging.info("Thread created")
        else:
            self.show_warning("This browser is already running")

    def run_browser(self, name: str, _queue: queue.Queue, logger: logging.Logger, set_locals_signal: pyqtSignal):
        logger.info(f"Log file created for {name}")
        try:
            do_decrypt(fr"{self.base_path}\profiles\{name}")
        except Exception as e:
            logging.error(f"Passwords decrypt error: {e}")

        logger.info(f"Browser {name} started")
        WebBrowser(base_path=self.base_path, account_name=name, logger=logger, _queue=_queue,
                   main_config=self.main_config,
                   set_locals_signal=set_locals_signal)
