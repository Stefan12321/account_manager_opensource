import datetime
import queue
from multiprocessing import freeze_support
from typing import List, Callable, Any

import requests
from PyQt5.QtWidgets import QMessageBox

freeze_support()
import os
from accounts_manager_main.serializer import serialize, deserialize, Config, MainConfig

os.environ["ACCOUNT_MANAGER_BASE_DIR"] = os.path.dirname(os.path.realpath(__file__))
os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"] = f"{os.path.dirname(os.path.realpath(__file__))}/settings.json"

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])
os.environ["DEBUG_ACCOUNT_MANAGER"] = str(main_config.config_data["debug"])
import time
import threading
import shutil
import zipfile
import logging

from GUI import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui, QtCore
from user_agents.main import get_user_agent
from list_widget import Ui_Form as Ui_Custom_widget
from dialogs.create_account_dialog import Ui_Dialog as Ui_create_account_dialog
from dialogs.about_dialog import Ui_Dialog as Ui_about_dialog
from dialogs.progress_bar import Ui_Dialog as Ui_progress_bar
from dialogs.message_dialogs import open_error_dialog
from password_decryptor.passwords_decryptor import do_decrypt
from zipfile import ZipFile
from accounts_manager_main.settings import MainSettings

APP_VERSION = "0.65"
if main_config.config_data["version"] == "opensource":
    from accounts_manager_main.web_browser import WebBrowser
    from accounts_manager_main.settings import SettingsDialog

    APP_VERSION += " opensource"

elif main_config.config_data["version"] == "private":
    try:
        from account_manager_private_part.private_web_browser import WebBrowserPrivate as WebBrowser
        from account_manager_private_part.private_settings_dialog import SettingsDialogPrivate as SettingsDialog

        APP_VERSION += " private"
    except PermissionError:
        logging.error("You can't use this version of app")
        raise PermissionError
else:
    open_error_dialog('Invalid version, set value "version" to "private" or "opensource" in main settings')
    logging.error('Invalid version, set value "version" to "private" or "opensource" in main settings')
from updater.update_application import update_application

DEBUG = (os.getenv("DEBUG_ACCOUNT_MANAGER", default='False') == 'True')

os.makedirs("logs/Main_log", exist_ok=True)
os.makedirs("extension", exist_ok=True)
os.makedirs("profiles", exist_ok=True)


class QListCustomWidgetNew(QtWidgets.QWidget, Ui_Custom_widget):
    def __init__(self, parent=None):
        super(QListCustomWidgetNew, self).__init__(parent)
        self.setupUi(parent)


class QWidgetOneAccountLine(QtWidgets.QWidget):
    def __init__(self, logger, parent=None):
        super(QWidgetOneAccountLine, self).__init__(parent)
        self.logger = logger
        self.name = None
        self._queue = None

        self.textQVBoxLayout = QtWidgets.QHBoxLayout()
        self.account_name_label = QtWidgets.QLabel()
        self.running_status_label = QtWidgets.QLabel()
        self.pushButtonSettings = QtWidgets.QPushButton()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.pushButtonSettings.sizePolicy().hasHeightForWidth())
        self.pushButtonSettings.setSizePolicy(size_policy)
        self.pushButtonSettings.setMaximumSize(32, 32)
        self.pushButtonSettings.setIcon(QtGui.QIcon("./icons/settings-icon.svg"))
        self.pushButtonSettings.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonSettings.clicked.connect(lambda: self.open_settings())

        self.checkBox = QtWidgets.QCheckBox()

        self.textQVBoxLayout.addWidget(self.checkBox)
        self.textQVBoxLayout.addWidget(self.account_name_label)
        self.textQVBoxLayout.addWidget(self.running_status_label)
        self.textQVBoxLayout.addWidget(self.pushButtonSettings)
        self.allQHBoxLayout = QtWidgets.QHBoxLayout()
        self.iconQLabel = QtWidgets.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        self.account_name_label.setStyleSheet('''
            color: rgb(0, 0, 255);
        ''')
        self.running_status_label.setStyleSheet('''
            color: rgb(255, 0, 0);
        ''')

    def open_settings(self):
        path = fr'{os.path.dirname(os.path.realpath(__file__))}\profiles\{self.name}'

        dlg = SettingsDialog(account_name=self.name, _queue=self._queue, logger=self.logger)
        dlg.show()
        dlg.exec()

    def setTextUp(self, text):
        self.account_name_label.setText(text)


class QListAccountsWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, name: str, widget: QWidgetOneAccountLine, parent=None, ):
        super(QListAccountsWidgetItem, self).__init__(parent)
        self.name = name
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


class CreateAccountDialog(Ui_create_account_dialog, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateAccountDialog, self).__init__(parent)
        self.setupUi(self)


class AboutDlg(Ui_about_dialog, QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.label_bild_number.setText(APP_VERSION)


class ProgressBarDialog(Ui_progress_bar, QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

    @QtCore.pyqtSlot(int)
    def progress(self, value: int):
        self.progressBar.setValue(value)

    @QtCore.pyqtSlot(str)
    def filename(self, name: str):
        self.label_file.setText(name)

    @QtCore.pyqtSlot()
    def exit(self):
        self.close()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    progress_signal = QtCore.pyqtSignal(int)
    progress_exit_signal = QtCore.pyqtSignal()
    progress_filename_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.base_path = fr"{os.path.dirname(os.path.realpath(__file__))}"
        self.profiles_path = fr"{os.path.dirname(os.path.realpath(__file__))}\profiles"
        try:
            self.browsers_names = [item for item in
                                   os.listdir(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles")
                                   if os.path.isdir(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles\{item}")]
        except FileNotFoundError:
            os.makedirs(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles")
            self.browsers_names = []
        self.list_item_arr: List[QListAccountsWidgetItem] = []
        for i in self.browsers_names:
            self.create_list_item(i)

        self.add_functions()
        self.start_threads_watcher()

    def add_functions(self):
        self.listWidget.itemClicked.connect(self.item_click)
        self.CreateAccountButton.clicked.connect(self.on_create_profile_btn_click)
        self.pushButtonDeleteAccounts.clicked.connect(self.delete_profiles)
        self.exportProfileButton.clicked.connect(self.export_profiles)
        self.importProfileButton.clicked.connect(self.import_profiles)
        self.checkBoxCkeckAll.stateChanged.connect(self.set_all_checkbox)
        self.actionAbout.triggered.connect(self.open_about)
        self.actionSettings.triggered.connect(self.open_main_settings)

    def set_all_checkbox(self, state: int):
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            item_state = widget.checkBox.checkState()
            if item_state != 2 and state == 2:
                widget.checkBox.setCheckState(QtCore.Qt.Checked)

            elif item_state != 0 and state == 0:
                widget.checkBox.setCheckState(QtCore.Qt.Unchecked)

    def create_list_item(self, name: str):
        path = os.path.dirname(os.path.realpath(__file__))
        logger = self.setup_logger_for_thread(path, name)

        one_account_line_widget = QWidgetOneAccountLine(logger)
        one_account_line_widget.setTextUp(name)
        one_account_line_widget.name = name
        qlist_item_one_account = QListAccountsWidgetItem(name,
                                                         one_account_line_widget,
                                                         self.listWidget)
        # Set size hint
        # Add QListWidgetItem into QListWidget
        self.listWidget.addItem(qlist_item_one_account)
        self.listWidget.setItemWidget(qlist_item_one_account, one_account_line_widget)
        self.list_item_arr.append(qlist_item_one_account)

    def extract_zip(self, path: str, forbidden=None):

        if forbidden is None:
            forbidden = []
        with ZipFile(path, 'r') as zipObj:
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
        profile_names = os.listdir(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles")
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

    def get_checked_items(self) -> List[QListAccountsWidgetItem]:
        checked_items = []
        for item in self.list_item_arr:
            widget = self.listWidget.itemWidget(item)
            if widget.checkBox.checkState() == 2:
                checked_items.append(item)
        return checked_items

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

    def update_item_list(self):
        self.browsers_names = [item for item in os.listdir(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles")
                               if os.path.isdir(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles\{item}")]
        self.list_item_arr = []
        self.listWidget.clear()
        for i in self.browsers_names:
            self.create_list_item(i)

    def open_progress_bar(self):
        dlg = ProgressBarDialog()
        self.progressbar_signal = dlg.signal
        dlg.show()
        dlg.exec()

    @staticmethod
    def open_about():
        dlg = AboutDlg()
        dlg.show()
        dlg.exec()

    @staticmethod
    def open_main_settings():
        settings_main = main_config.config_data

        dlg = MainSettings()
        dlg.add_settings_fields(settings_main)
        dlg.add_box_buttons()
        dlg.show()
        result = dlg.exec()
        if result:
            settings_main = dlg.update_settings(settings_main)
            main_config.update(settings_main)

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
        self.create_list_item(profile_name)
        self.browsers_names.append(profile_name)
        path = fr"{os.path.dirname(os.path.realpath(__file__))}\profiles\{profile_name}"
        os.makedirs(path)
        user_agent_ = get_user_agent(os=("win"), navigator=("chrome"), device_type=("desktop"))
        data = {
            'user-agent': user_agent_
        }
        serialize(fr'{path}\config.json', data)

    def item_click(self, item: QListAccountsWidgetItem):
        item_widget = self.listWidget.itemWidget(item)
        account_name = item_widget.name
        logger = item_widget.logger

        if item.status is not True:
            _queue = queue.Queue()
            t = threading.Thread(target=self.run_browser, args=(account_name, _queue, logger))
            item.thread = t
            item.widget._queue = _queue
            t.start()
            logging.info("Thread created")
        else:
            self.show_warning("This browser is already running")

    @staticmethod
    def run_browser(name: str, _queue: queue.Queue, logger: logging.Logger):
        path = os.path.dirname(os.path.realpath(__file__))
        logger.info(f"Log file created for {name}")
        try:
            do_decrypt(fr"{path}\profiles\{name}")
        except Exception as e:
            logging.error(f"Passwords decrypt error: {e}")

        logger.info(f"Browser {name} started")
        WebBrowser(base_path=path, account_name=name, logger=logger, _queue=_queue, main_config=main_config)

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

    def start_threads_watcher(self):
        t = threading.Thread(target=self.threads_watcher)
        t.start()

    def threads_watcher(self):
        while True:
            for i in self.list_item_arr:
                try:
                    widget = self.listWidget.itemWidget(i)
                    if i.thread.is_alive():

                        widget.running_status_label.setText('running...')
                        # search account_widget_item with widget = current widget. WARNING! Work only if accounts names are not repeated
                        account_widget_item = [item for item in self.list_item_arr if item.name == widget.name][0]
                        account_widget_item.status = True
                    else:
                        widget.running_status_label.setText('')
                        # search account_widget_item with widget = current widget. WARNING! Work only if accounts names are not repeated
                        account_widget_item = [item for item in self.list_item_arr if item.name == widget.name][0]
                        account_widget_item.status = False

                except AttributeError:
                    pass
            time.sleep(1)

    def show_warning(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def show_info(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


if __name__ == '__main__':

    import sys

    logging.basicConfig(
        filename=rf"{os.path.dirname(os.path.realpath(__file__))}\logs\Main_log\{datetime.date.today().strftime('%d_%m_%Y')}.log",
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    update_application.APP_VERSION = APP_VERSION
    try:
        if main_config.config_data["check_for_updates"] and update_application():
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        logging.error("Failed to check for update")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec_())
