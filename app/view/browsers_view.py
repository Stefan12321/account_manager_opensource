import logging
import os
import queue
import shutil
import threading
import time
import zipfile
from typing import List, Callable

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from qfluentwidgets import ListWidget, setCustomStyleSheet

from app.common.settings import serializer
from app.common.settings.serializer import MainConfig, Serializer
from app.common.logger import setup_logger_for_thread
from app.components.account_item import QWidgetOneAccountLine, QListAccountsWidgetItem
from app.components.warning_dialog import WarningDialog
from app.components.progress_bar import FilesProgressBarDialog
from app.components.style_sheet import StyleSheet
from app.view.base_view import Widget
from app.components.create_account_dialog import CreateAccountDialog
from app.components.accounts_list_tools_widget import Ui_Form as accounts_list_tools_ui
from app.components.warning_dialog import WarningDialog
from app.common.password_decryptor.passwords_decryptor import do_decrypt
from app.common.user_agents.main import get_user_agent

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


class AccountsListToolsWidget(QWidget, accounts_list_tools_ui):
    def __init__(self, parent=None):
        super(AccountsListToolsWidget, self).__init__(parent)
        self.setupUi(self)
        delete_button_style = StyleSheet(f"{os.environ['ACCOUNT_MANAGER_PATH_TO_RESOURCES']}/dark/delete_button.qss")
        setCustomStyleSheet(self.delete_button, str(delete_button_style), str(delete_button_style))


class BrowserListWidget(Widget):
    progress_signal = QtCore.pyqtSignal(int)
    progress_exit_signal = QtCore.pyqtSignal()
    progress_filename_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_config: MainConfig, parent=None):
        super().__init__("browser-list", parent=parent)
        self.main_config = main_config
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

        self.start_threads_watcher()

    def __init_layout(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.listWidget = ListWidget()
        self.listWidget.itemClicked.connect(self.item_click)

        self.list_tools = AccountsListToolsWidget()
        self.list_tools.CheckBox.stateChanged.connect(self.set_all_checkbox)
        self.list_tools.create_profile_button.clicked.connect(self.on_create_profile_btn_click)
        self.list_tools.delete_button.clicked.connect(self.delete_profiles)
        self.list_tools.import_button.clicked.connect(self.import_profiles)
        self.list_tools.export_button.clicked.connect(self.export_profiles)

        self.update_item_list()
        # self.hBoxLayout.addWidget(self.list_tools)
        self.hBoxLayout.addWidget(self.listWidget, 1)

        self.vBoxLayout.addWidget(self.list_tools)
        self.vBoxLayout.addLayout(self.hBoxLayout)

    def update_item_list(self):
        self.browsers_names = [item for item in os.listdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
                               if os.path.isdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\{item}")]
        self.list_item_arr = []
        self.listWidget.clear()
        for index, browser_name in enumerate(self.browsers_names):
            self.create_list_item(browser_name, index)

    def create_list_item(self, name: str, index: int):
        path = os.environ['ACCOUNT_MANAGER_BASE_DIR']
        logger = setup_logger_for_thread(path, name)
        one_account_line_widget = QWidgetOneAccountLine(name, self.main_config, logger, index)
        one_account_line_widget.set_account_name(name)

        qlist_item_one_account = QListAccountsWidgetItem(name,
                                                         one_account_line_widget,
                                                         self.main_config,
                                                         self.listWidget)
        qlist_item_one_account.setIcon(QIcon(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR'] }/app/resource/Google_icon.svg"))
        # Set size hint
        # Add QListWidgetItem into QListWidget
        self.listWidget.addItem(qlist_item_one_account)
        self.listWidget.setItemWidget(qlist_item_one_account, one_account_line_widget)
        self.list_item_arr.append(qlist_item_one_account)

    def set_all_checkbox(self, state: int):
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            item_state = widget.CheckBox.isChecked()
            if not item_state and state == 2:
                widget.CheckBox.setChecked(True)

            elif item_state and state == 0:
                widget.CheckBox.setChecked(False)

    def get_checked_items(self) -> List[QListAccountsWidgetItem]:
        checked_items = []
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            if widget.CheckBox.isChecked():
                checked_items.append(item)
        return checked_items

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

    def on_create_profile_btn_click(self):
        dlg = CreateAccountDialog(self)
        dlg.show()
        result = dlg.exec()
        account_name = dlg.new_account_line_edit.text()
        if result and account_name not in self.browsers_names:
            self.create_profile(account_name)
        elif account_name in self.browsers_names:
            WarningDialog(f"Account with name {account_name} is already exist. Try different name")

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
            "default_new_tab": main_config.config_data["default_new_tab"]
        }
        s = Serializer()
        s.serialize(data, fr'{path}\config.json')
        self.create_list_item(profile_name, self.listWidget.count())
        self.browsers_names.append(profile_name)

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
        print("EXPORTED")

    def import_profiles(self):
        profile_names = os.listdir(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles")
        dlg = QtWidgets.QFileDialog()
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            if len(filenames) == 1:
                pth = zipfile.Path(filenames[0])
                profiles = list(pth.iterdir())
                imported_accounts = [folder.name for folder in profiles]
                msg = WarningDialog(f"Are y sure you want to import accounts: {imported_accounts}", self)
                msg.setWindowTitle("Warning")
                retval = msg.exec()
                if retval == 1:
                    same_items = [item for item in profile_names if item in imported_accounts]

                    if len(same_items) > 0:
                        msg = WarningDialog(f"Accounts {same_items} is already exist. Overwrite?", self)
                        retval = msg.exec()
                        if retval == 1:
                            self.progress_bar_thread(self.extract_zip, "Importing", filenames[0])
                            self.update_item_list()
                            print("IMPORTED")
                        else:
                            self.progress_bar_thread(self.extract_zip, "Importing", filenames[0], same_items)
                            self.update_item_list()
                            print("IMPORTED")
                    else:
                        self.progress_bar_thread(self.extract_zip, "Importing", filenames[0])
                        self.update_item_list()
                        print("IMPORTED")

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
                    # print(f"{counter / (length / 100)}%")
        self.progress_exit_signal.emit()

    def delete_profiles(self):
        checked_items = self.get_checked_items()

        if len(checked_items) > 0:
            dlg = WarningDialog(f"Are y sure you want to delete accounts: {[i.name for i in checked_items]}", self)
            retval = dlg.exec()
            if retval == 1:
                self.progress_bar_thread(self.delete_profiles_thread, "Deleting", checked_items)
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

    def item_click(self, item: QListAccountsWidgetItem):
        item_widget = self.listWidget.itemWidget(item)
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

    def start_threads_watcher(self):
        t = threading.Thread(target=self.threads_watcher)
        t.start()

    def threads_watcher(self):
        while True:
            for i in self.list_item_arr:
                try:
                    widget = self.listWidget.itemWidget(i)
                    if i.thread.is_alive():
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

                except AttributeError:
                    pass
            time.sleep(1)
