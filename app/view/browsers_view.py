import logging
import os
import queue
from typing import List

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import TabItem

import app.common.settings.app_version
from app.common.settings.serializer import MainConfig
from app.components.account_item import QListAccountsWidgetItem
from app.components.browser_tabs import BrowsersTabBar, BrowsersTab
from app.components.create_new_tab_dialog import CreateTabDialog
from app.components.stacked_widget import StackedWidget
from app.view.base_view import Widget
from app.components.warning_dialog import WarningDialog
from app.common.browser.browser_thread import BrowserThread

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])

if main_config.config_data["version"]["values"]["opensource"] is True:
    app.common.settings.app_version.APP_VERSION += " opensource"

elif main_config.config_data["version"]["values"]["private"] is True:
    try:
        app.common.settings.app_version.APP_VERSION += " private"
    except PermissionError:
        logging.error("You can't use this version of app")
        raise PermissionError
else:
    WarningDialog(
        'Invalid version, set value "version" to "private" or "opensource" in main settings',
        hide_cancel_button=True,
    ).exec()
    logging.error(
        'Invalid version, set value "version" to "private" or "opensource" in main settings'
    )


class BrowserListWidget(Widget):
    progress_signal = QtCore.pyqtSignal(int)
    progress_exit_signal = QtCore.pyqtSignal()
    progress_filename_signal = QtCore.pyqtSignal(str)
    thread_exception_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_config: MainConfig, parent=None):
        super().__init__("browser-list", parent=parent)
        self.parent = parent
        self.main_config = main_config
        self.browser_tab_all_accounts = None
        self.base_path = rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}"
        self.profiles_path = rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles"
        try:
            self.browsers_names = [
                item
                for item in os.listdir(
                    rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles"
                )
                if os.path.isdir(
                    rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles/{item}"
                )
            ]
        except FileNotFoundError:
            os.makedirs(rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles")
            self.browsers_names = []
        self.list_item_arr: List[QListAccountsWidgetItem] = []

        self.setObjectName("BrowserListWidget")

        self.__init_layout()

        self.thread_exception_signal.connect(self.on_thread_exception)

    def __init_layout(self):
        self.vBoxLayout = QVBoxLayout(self)

        self.browser_list_stacked_widget = StackedWidget(
            self, objectName="browser_list_stacked_widget"
        )

        self.tabBar = BrowsersTabBar(self.main_config, self)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)
        self.tabBar.currentChanged.connect(self.onTabChanged)

        # init base tab
        logo_svg = f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/logo.svg'
        self.browser_tab_all_accounts, tab = self.addTab(
            [
                item
                for item in os.listdir(
                    rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles"
                )
                if os.path.isdir(
                    rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles/{item}"
                )
            ],
            "All",
            "All",
            logo_svg,
        )
        tab.closeButton.hide()

        # init tabs from main_config
        if "tabs" in self.main_config.config_data:
            for tab_name in self.main_config.config_data["tabs"]["values"].keys():
                self.addTab(
                    self.main_config.config_data["tabs"]["values"][tab_name],
                    tab_name,
                    tab_name,
                    logo_svg,
                )

        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.browser_list_stacked_widget)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        self.browser_list_stacked_widget.setCurrentWidget(
            self.findChild(BrowsersTab, objectName)
        )

    def onTabAddRequested(self):
        dlg = CreateTabDialog(self)
        if dlg.exec():
            text = dlg.new_account_line_edit.text()
            self.addTab(
                [],
                text,
                text,
                f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/logo.svg',
                True,
            )

    def addTab(
        self, browser_names: List[str], routeKey, text, icon, from_user=False
    ) -> tuple[BrowsersTab, TabItem]:
        tab = self.tabBar.addTab(routeKey, text, icon, None, from_user)
        browser_tab = BrowsersTab(self.main_config, browser_names, routeKey, self)
        browser_tab.listWidget.itemClicked.connect(self.item_click)
        if self.browser_tab_all_accounts:
            browser_tab.item_list_updated.connect(
                self.browser_tab_all_accounts.update_item_list_for_all_browsers
            )
        tab.dropped_browser.connect(browser_tab.on_tab_dropped_account)
        self.browser_list_stacked_widget.addWidget(browser_tab)
        return browser_tab, tab

    def get_tab_with_name(self, tab_name: str) -> BrowsersTab | None:
        return next(
            (
                item
                for item in self.browser_list_stacked_widget.get_widgets()
                if item.get_route_key() == tab_name
            ),
            None,
        )

    def item_click(self, item: QListAccountsWidgetItem):
        item_widget = (
            self.browser_list_stacked_widget.currentWidget().listWidget.itemWidget(item)
        )
        account_name = item_widget.name
        logger = item_widget.logger
        if item.status is not True:
            _queue = queue.Queue()
            locals_signal = item.widget.locals_signal
            t = BrowserThread(
                account_name,
                _queue,
                logger,
                locals_signal,
                self.base_path,
                self.main_config,
                self.thread_exception_signal,
            )
            item.thread = t
            item.widget._queue = _queue
            t.start()
            logging.info("Thread created")
        else:
            WarningDialog(
                "This browser is already running", parent=self, hide_cancel_button=True
            ).exec()

    def on_thread_exception(self, exception_text: str):
        WarningDialog(exception_text, parent=self, hide_cancel_button=True).exec()
