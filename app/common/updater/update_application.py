import os
import shutil
import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QDesktopWidget

from app.common.updater.base import find_path_to_file, copy_folder, get_latest_release

APP_VERSION = "0.3"
FILE_IN_BASE_FOLDER = "Accounts manager.exe"


class App(QWidget):

    def __init__(self, latest_version):
        super().__init__()
        self.title = 'Update'
        screen_geometry = QDesktopWidget().availableGeometry()

        self.width = 320
        self.height = 200
        self.left = (screen_geometry.width() - self.width) // 2
        self.top = (screen_geometry.height() - self.height) // 2
        self.latest_version = latest_version
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.buttonReply = QMessageBox.question(self, 'Update?',
                                                f"There is a new version available. Do you want to update?\nYour version: {APP_VERSION}\nNew version: {self.latest_version}",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


def user_want_to_update(latest_version) -> bool:
    QApplication(sys.argv)
    ex = App(latest_version)
    ex.show()
    if ex.buttonReply == QMessageBox.Yes:
        return True
    else:
        return False


def update_application():
    base_folder = find_path_to_file(FILE_IN_BASE_FOLDER)
    parent_base_folder = base_folder.parent
    latest_version, _ = get_latest_release()
    if latest_version and float(latest_version) > float(APP_VERSION):
        if user_want_to_update(latest_version):
            copy_folder(f"{base_folder}/elevator", f"{parent_base_folder}/elevator")
            os.makedirs(f'{parent_base_folder}/saved_files')
            shutil.copyfile(f"{base_folder}/settings.json", f"{parent_base_folder}/saved_files/settings.json")
            subprocess.Popen([f'{parent_base_folder}/elevator/elevator.exe'], shell=True)
            return True

    return False
