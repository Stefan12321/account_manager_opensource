import logging
import os
import shutil
import threading
import time
import zipfile
from typing import List, Callable, Union

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QIcon, QKeySequence
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QListWidget, QShortcut
from qfluentwidgets import TabBar, ListWidget, FluentIconBase, TabItem

from app.common.logger import setup_logger_for_thread
from app.common.password_decryptor import do_decrypt
from app.common.settings import MainConfig, Serializer
from app.common.user_agents import get_user_agent
from app.components.account_item import QWidgetOneAccountLine, QListAccountsWidgetItem
from app.components.accounts_list_tools_widget import AccountsListToolsWidget
from app.components.create_account_dialog import CreateAccountDialog
from app.components.progress_bar import FilesProgressBarDialog
from app.components.warning_dialog import WarningDialog


class TabItemWithDrops(TabItem):
    dropped_browser = QtCore.pyqtSignal(str)

    def _postInit(self):
        super()._postInit()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()

    def dragLeaveEvent(self, e):
        print("dragLeaveEvent")

    def dragMoveEvent(self, e):
        print("dragMoveEvent")

    def dropEvent(self, e):
        # print("dropEvent")
        if 'text/plain' in e.mimeData().formats():
            browser_name = e.mimeData().data('text/plain').data().decode('utf-8')
            self.dropped_browser.emit(browser_name)
            # if browser_name not in self.br


class BrowsersTabBar(TabBar):
    """ Title bar with icon and title """
    dropped_browser_to_tab = QtCore.pyqtSignal(str, TabItemWithDrops)

    def __init__(self, main_config: MainConfig, parent=None):
        super().__init__(parent)
        # self.setAcceptDrops(True)
        self.main_config = main_config
        self.setMovable(True)
        self.setTabMaximumWidth(220)
        self.setTabShadowEnabled(False)
        self.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))

        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(lambda i: print(self.tabText(i)))

        self.hBoxLayout.setStretch(6, 0)

        self.hBoxLayout.insertSpacing(8, 20)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.x())
        return not self.tabRegion().contains(pos)

    def addTab(self, routeKey: str, text: str, icon: Union[QIcon, str, FluentIconBase] = None, onClick=None,
               from_user=False):
        if from_user:
            if "tabs" in self.main_config.config_data:
                data = self.main_config.config_data
                data["tabs"]["values"].update({text: []})
            else:
                data = {"tabs": {
                    "type": "invisible",
                    "values": {
                        text: []
                    }
                }}
            self.main_config.update(data)
        return super().addTab(routeKey, text, icon, onClick)

    def removeTab(self, index: int):
        self.main_config.config_data["tabs"]["values"].pop(self.items[index]._routeKey)
        self.main_config.update(self.main_config.config_data)
        super().removeTab(index)

    def insertTab(self, index: int, routeKey: str, text: str, icon: Union[QIcon, str, FluentIconBase] = None,
                  onClick=None):
        """ insert tab

        Parameters
        ----------
        index: int
            the insert position of tab item

        routeKey: str
            the unique name of tab item

        text: str
            the text of tab item

        text: str
            the icon of tab item

        onClick: callable
            the slot connected to item clicked signal
        """
        if routeKey in self.itemMap:
            raise ValueError(f"The route key `{routeKey}` is duplicated.")

        if index == -1:
            index = len(self.items)

        # adjust current index
        if index <= self.currentIndex() and self.currentIndex() >= 0:
            self._currentIndex += 1

        item = TabItemWithDrops(text, self.view, icon)
        item.setRouteKey(routeKey)

        # set the size of tab
        w = self.tabMaximumWidth() if self.isScrollable() else self.tabMinimumWidth()
        item.setMinimumWidth(w)
        item.setMaximumWidth(self.tabMaximumWidth())

        item.setShadowEnabled(self.isTabShadowEnabled())
        item.setCloseButtonDisplayMode(self.closeButtonDisplayMode)
        item.setSelectedBackgroundColor(
            self.lightSelectedBackgroundColor, self.darkSelectedBackgroundColor)

        item.pressed.connect(self._onItemPressed)
        item.closed.connect(lambda: self.tabCloseRequested.emit(self.items.index(item)))
        item.dropped_browser.connect(self._on_item_dropped)
        if onClick:
            item.pressed.connect(onClick)

        self.itemLayout.insertWidget(index, item, 1)
        self.items.insert(index, item)
        self.itemMap[routeKey] = item

        if len(self.items) == 1:
            self.setCurrentIndex(0)

        return item

    def _on_item_dropped(self, browser_name: str):
        self.dropped_browser_to_tab.emit(browser_name, self.sender())


class BrowsersTab(QFrame):
    progress_signal = QtCore.pyqtSignal(int)
    progress_exit_signal = QtCore.pyqtSignal()
    progress_filename_signal = QtCore.pyqtSignal(str)
    item_list_updated = QtCore.pyqtSignal()

    """ Tab interface """

    def __init__(self, main_config: MainConfig, browsers_names: List[str], objectName,
                 parent=None, is_for_all_profiles=False):
        super().__init__(parent=parent)
        self.parent_widget = parent
        self.is_for_all_profiles = is_for_all_profiles
        self.main_config = main_config
        self.all_browser_names = os.listdir(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles")
        self.browsers_names = browsers_names
        self.list_item_arr: List[QListAccountsWidgetItem] = []
        self.base_path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}"
        self.profiles_path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles"
        self.setObjectName(objectName)
        self._init_layout()
        self.start_threads_watcher()

    def _init_layout(self):

        self.vBoxLayout = QVBoxLayout(self)
        self.listWidget = ListWidget()
        self.listWidget.setDragDropMode(QListWidget.DragOnly)
        self.list_tools = AccountsListToolsWidget()
        self.list_tools.setFixedHeight(60)
        self.list_tools.CheckBox.stateChanged.connect(self.set_all_checkbox)
        shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut.activated.connect(lambda: self.list_tools.CheckBox.nextCheckState())
        self.list_tools.create_profile_button.clicked.connect(self.on_create_profile_btn_click)
        self.list_tools.delete_button.clicked.connect(self.delete_profiles)
        if self.objectName() != "All":
            self.list_tools.export_button.hide()
            self.list_tools.import_button.hide()
            self.list_tools.horizontalLayout.addStretch(2)
        else:
            self.list_tools.export_button.clicked.connect(self.export_profiles)
            self.list_tools.import_button.clicked.connect(self.import_profiles)

        self.vBoxLayout.addWidget(self.list_tools, 1)
        self.vBoxLayout.addWidget(self.listWidget, 1)

        self.update_item_list()

    def get_route_key(self) -> str:
        return self.objectName()

    def update_item_list(self):
        self.list_item_arr = []
        self.listWidget.clear()
        for index, browser_name in enumerate(self.browsers_names):
            self.create_list_item(browser_name, index)

    def update_item_list_for_all_browsers(self):
        self.browsers_names = os.listdir("profiles")
        self.update_item_list()

    def create_list_item(self, name: str, index: int):
        path = os.environ['ACCOUNT_MANAGER_BASE_DIR']
        logger = setup_logger_for_thread(path, name)
        one_account_line_widget = QWidgetOneAccountLine(name, self.main_config, logger, index, self)
        one_account_line_widget.account_name_label.name_changed.connect(self.account_name_changed)

        qlist_item_one_account = QListAccountsWidgetItem(name,
                                                         one_account_line_widget,
                                                         self.main_config,
                                                         self.listWidget)
        qlist_item_one_account.setIcon(QIcon(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/app/resource/Google_icon.svg"))
        # Set size hint
        # Add QListWidgetItem into QListWidget
        self.listWidget.addItem(qlist_item_one_account)
        self.listWidget.setItemWidget(qlist_item_one_account, one_account_line_widget)
        self.list_item_arr.append(qlist_item_one_account)
        self.item_list_updated.emit()

    def account_name_changed(self, old_name: str, new_name: str):
        self.browsers_names.remove(old_name)
        self.browsers_names.append(new_name)

    def set_all_checkbox(self, state: int):
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            item_state = widget.CheckBox.isChecked()
            if not item_state and state == 2:
                widget.CheckBox.setChecked(True)

            elif item_state and state == 0:
                widget.CheckBox.setChecked(False)

    def on_create_profile_btn_click(self):
        dlg = CreateAccountDialog(self)
        dlg.show()
        result = dlg.exec()
        account_name = dlg.new_account_line_edit.text()

        if result and account_name not in self.all_browser_names:
            self.create_profile(account_name)
        elif account_name in self.all_browser_names:
            WarningDialog(f"Account with name {account_name} is already exist. Try different name", self).exec()

    def create_profile(self, profile_name: str):
        path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\{profile_name}"
        os.makedirs(path)
        user_agent_ = get_user_agent(os=("win"), navigator=("chrome"), device_type=("desktop"))
        extension_list = os.listdir(fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\extension')
        data = {
            'user-agent': user_agent_,
            "line_number": "",
            "proxy": "",
            "latitude": "",
            "longitude": "",
            "extensions": {key: False for key in extension_list},
            "default_new_tab": self.main_config.config_data["default_new_tab"]
        }
        s = Serializer()
        s.serialize(data, fr'{path}\config.json')
        self.create_list_item(profile_name, self.listWidget.count())
        self.browsers_names.append(profile_name)
        if self.objectName() != "All":
            self.main_config.update(self.main_config.config_data)

    def export_profiles(self):
        checked_items = self.get_checked_items()
        export_path = fr"{self.base_path}\export.zip"
        if os.path.isfile(export_path):
            os.remove(export_path)
        if len(checked_items) > 0:
            for profile in checked_items:
                passwords = do_decrypt(fr"{self.profiles_path}\{profile.name}")
                logging.info(passwords)
            self.progress_bar_thread(self.zip_directory, "Exporting",
                                     [fr'{self.profiles_path}\{profile.name}' for profile in checked_items],
                                     export_path)

    def import_profiles(self):
        dlg = QtWidgets.QFileDialog()
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) == 1:
                pth = zipfile.Path(filenames[0])
                profiles = list(pth.iterdir())
                imported_accounts = [folder.name for folder in profiles]

                if self.confirm_import(imported_accounts) == 1:
                    self.handle_existing_accounts(imported_accounts, filenames[0])
                    self.update_item_list()

    def confirm_import(self, imported_accounts: List[str]) -> int:
        msg = WarningDialog(f"Are y sure you want to import accounts: {imported_accounts}", self)
        msg.setWindowTitle("Warning")
        return msg.exec()

    def handle_existing_accounts(self, imported_accounts: List[str], filename):
        profile_names = os.listdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
        same_items = [item for item in profile_names if item in imported_accounts]
        not_same_items = [item for item in imported_accounts if item not in same_items]
        self.browsers_names += not_same_items
        if len(same_items) > 0:
            msg = WarningDialog(f"Accounts {same_items} is already exist. Overwrite?", self)
            retval = msg.exec()
            if retval == 1:
                self.progress_bar_thread(self.extract_zip, "Importing", filename)
            else:
                self.progress_bar_thread(self.extract_zip, "Importing", filename, same_items)
        else:
            self.progress_bar_thread(self.extract_zip, "Importing", filename)

    def zip_directory(self, folders_path: list, zip_path: str):
        counter = 1
        with zipfile.ZipFile(zip_path, mode='w') as zipf:
            length = len(folders_path)
            for folder_path in folders_path:
                base_folder = folder_path.split('\\')[-1]
                self.progress_signal.emit(int(counter / (length / 100)))
                self.progress_filename_signal.emit(base_folder)
                len_dir_path = len(folder_path)
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, f'{base_folder}/{file_path[len_dir_path:]}')
                counter += 1
        self.progress_exit_signal.emit()

    def extract_zip(self, path: str, forbidden=None):

        if forbidden is None:
            forbidden = []
        with zipfile.ZipFile(path, 'r') as zipObj:
            counter = 0
            length = len(zipObj.filelist)
            # TODO if forbidden is not empty then length should be shorter
            for file in zipObj.filelist:
                if file.filename.split('/')[0] not in forbidden:
                    zipObj.extract(file, './profiles')
                    counter += 1
                    self.progress_signal.emit(int(counter / (length / 100)))
                    self.progress_filename_signal.emit(file.filename)
        self.progress_exit_signal.emit()

    def delete_profiles(self):
        checked_items = self.get_checked_items()

        if len(checked_items) > 0:
            dlg = WarningDialog(f"Are y sure you want to delete accounts: {[i.name for i in checked_items]}", self)
            retval = dlg.exec()
            if retval == 1:
                self.progress_bar_thread(self.delete_profiles_thread, "Deleting", checked_items)
                for i in checked_items:
                    if i.name in self.browsers_names:
                        self.browsers_names.remove(i.name)
                self.update_item_list()

    def delete_profiles_thread(self, checked_items: List[QListAccountsWidgetItem]):
        counter = 1
        length = len(checked_items)
        for profile in checked_items:
            shutil.rmtree(path=fr'{self.profiles_path}\{profile.name}')
            self.listWidget.removeItemWidget(profile)
            self.progress_signal.emit(int(counter / (length / 100)))
            self.progress_filename_signal.emit(profile.name)
            counter += 1

        self.progress_exit_signal.emit()

    def progress_bar_thread(self, target: Callable, title: str, *args):
        """

        :param target: target function
        :param title: title for progress window
        :param args: args for target function
        :return:
        """
        progress_bar = FilesProgressBarDialog(title)
        progress_bar.show()
        self.progress_signal.connect(progress_bar.progress)
        self.progress_exit_signal.connect(progress_bar.exit)
        self.progress_filename_signal.connect(progress_bar.filename)
        t = threading.Thread(target=target, args=args)
        t.start()
        progress_bar.exec()

    def get_checked_items(self) -> List[QListAccountsWidgetItem]:
        checked_items = []
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            if widget.CheckBox.isChecked():
                checked_items.append(item)
        return checked_items

    def on_tab_dropped_account(self, account_name: str):
        tab_name = self.sender().routeKey()
        self.add_account_to_tab(account_name, tab_name)

    def add_account_to_tab(self, account_name, tab_name):
        target_tab = self.parent_widget.get_tab_with_name(tab_name)
        if account_name not in self.main_config.config_data["tabs"]["values"][
            tab_name] and account_name not in target_tab.browsers_names:
            target_tab.browsers_names.append(account_name)
            target_tab.main_config.update(target_tab.main_config.config_data)
        target_tab.update_item_list()

    def remove_account_from_tab(self, account_name: str):
        self.browsers_names.remove(account_name)
        self.main_config.update(self.main_config.config_data)
        self.update_item_list()

    def start_threads_watcher(self):
        t = threading.Thread(target=self.threads_watcher)
        t.start()

    def threads_watcher(self):
        while True:
            for item in self.list_item_arr:
                try:
                    self.manage_animation_status(item)

                except AttributeError:
                    pass
            time.sleep(1)

    def manage_animation_status(self, item: QListAccountsWidgetItem):
        widget = self.listWidget.itemWidget(item)
        if item.thread.is_alive():
            if not widget.is_animation_running:
                widget.start_animation()

            # search account_widget_item with widget = current widget. WARNING! Work only if accounts names are not repeated
            account_widget_item = [item for item in self.list_item_arr if item.name == widget.name][0]
            account_widget_item.status = True
        else:
            if widget.is_animation_running:
                widget.stop_animation()

            # search account_widget_item with widget = current widget. WARNING! Work only if accounts names are not repeated
            account_widget_item = [item for item in self.list_item_arr if item.name == widget.name][0]
            account_widget_item.status = False
