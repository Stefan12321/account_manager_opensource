import logging
import os
import shutil
import threading
import zipfile
from typing import Any, List, Callable

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem, QWidget, QVBoxLayout
from qfluentwidgets import ListWidget, CheckBox, FluentIcon

from accounts_manager_main.serializer import Config, MainConfig, Serializer
from accounts_manager_main.settings import SettingsDialog
from app.view.base_view import Widget
from app.components.one_accout_line_widget import Ui_Form
from app.components.accounts_list_tools_widget import Ui_Form as accounts_list_tools_ui
from dialogs.message_dialogs import open_error_dialog
from main import CreateAccountDialog, ProgressBarDialog
from password_decryptor.passwords_decryptor import do_decrypt
from user_agents.main import get_user_agent


class AccountsListToolsWidget(QWidget, accounts_list_tools_ui):
    def __init__(self, parent=None):
        super(AccountsListToolsWidget, self).__init__(parent)
        self.setupUi(self)


class QWidgetOneAccountLine(QWidget, Ui_Form):
    locals_signal = pyqtSignal(dict)

    def __init__(self, main_config: MainConfig, logger: logging.Logger, index: int, parent=None):
        super(QWidgetOneAccountLine, self).__init__(parent)

        self.index = index
        self.logger = logger
        self.main_config = main_config
        self.name = None
        self._queue = None
        self.locals = None
        self.locals_signal.connect(self.set_locals)

        self.setupUi(self)
        self.settings_button.setIcon(FluentIcon.SETTING)
        self.settings_button.clicked.connect(self.open_settings)
        self.running_ring.stop()
        self.browser_icon.setIcon(QIcon('app/resource/Google_Chrome_icon.svg'))

    def open_settings(self):
        show_console = self.main_config.config_data["python_console"]
        dlg = SettingsDialog(account_name=self.name,
                             _queue=self._queue,
                             logger=self.logger,
                             _locals=self.locals,
                             show_console=show_console
                             )
        dlg.show()
        dlg.exec()

    def set_account_name(self, name: str):
        self.name = name
        self.account_name_label.setText(name)

    def set_locals(self, _locals: dict[str, Any]):
        self.locals = _locals

    def enterEvent(self, event):
        self.parent().parent()._setHoverRow(self.index)


class QListAccountsWidgetItem(QListWidgetItem):
    def __init__(self, name: str, widget: QWidgetOneAccountLine, main_config: MainConfig, parent=None, ):
        super(QListAccountsWidgetItem, self).__init__(parent)
        self.name = name
        self.main_config = main_config
        self.status: bool = False
        self.thread: threading.Thread or None = None
        self.widget = widget
        self.setSizeHint(self.widget.sizeHint())
        if main_config.config_data["accounts_tooltips"]:
            self.setToolTips()

    def setToolTips(self):
        self.path = fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\profiles\{self.name}'
        config = Config(fr"{self.path}\config.json")
        self.setToolTip(str(config))


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

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.listWidget = ListWidget()

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
        logger = self.setup_logger_for_thread(path, name)
        one_account_line_widget = QWidgetOneAccountLine(self.main_config, logger, index)
        one_account_line_widget.set_account_name(name)

        qlist_item_one_account = QListAccountsWidgetItem(name,
                                                         one_account_line_widget,
                                                         self.main_config,
                                                         self.listWidget)
        qlist_item_one_account.setIcon(QIcon("app/resources/Google_icon.svg"))
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
        progress_bar = ProgressBarDialog()
        progress_bar.show()
        progress_bar.setWindowTitle(title)
        self.progress_signal.connect(progress_bar.progress)
        self.progress_exit_signal.connect(progress_bar.exit)
        self.progress_filename_signal.connect(progress_bar.filename)
        t = threading.Thread(target=target, args=args)
        t.start()
        progress_bar.exec()

    def on_create_profile_btn_click(self):
        dlg = CreateAccountDialog()
        dlg.show()
        result = dlg.exec()
        account_name = dlg.lineEdit.text()
        if result and account_name not in self.browsers_names:
            self.create_profile(account_name)
        elif account_name in self.browsers_names:
            open_error_dialog(f"Account with name {account_name} is already exist. Try different name")

    def create_profile(self, profile_name: str):
        path = fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\{profile_name}"
        os.makedirs(path)
        user_agent_ = get_user_agent(os=("win"), navigator=("chrome"), device_type=("desktop"))
        data = {
            'user-agent': user_agent_
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
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText(f"Are y sure you want to import accounts: {imported_accounts}")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                retval = msg.exec()
                if retval == 1024:
                    same_items = [item for item in profile_names if item in imported_accounts]

                    if len(same_items) > 0:
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Warning)
                        msg.setText(f"Accounts {same_items} is already exist. Overwrite?")
                        msg.setWindowTitle("Warning")
                        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                        retval = msg.exec()
                        if retval == 1024:
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
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)

            msg.setText(f"Are y sure you want to delete accounts: {[i.name for i in checked_items]}")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            retval = msg.exec()
            if retval == 1024:
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

    @staticmethod
    def setup_logger_for_thread(path, thread_name) -> logging.Logger:
        # Create a logger for the thread
        logger = logging.getLogger(thread_name)
        logger.setLevel(logging.INFO)

        # Create a file handler to write log messages to a file
        log_file = fr"{path}\logs\{thread_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create a stream handler that displays logs in the terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # Create a formatter to specify the log message format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        # Set the logger as the default logger for the thread
        # logging.root = logger
        return logger
