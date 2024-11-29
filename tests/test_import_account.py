import os
import shutil
import zipfile

import pytestqt.qtbot  # noqa
from PyQt5 import QtCore

from tests.fixtures import main_window, create_account  # noqa


class prepare_import_file:
    def __init__(self, account_name: str, file_data: str, settings_file_name: str):
        self.zip_path = rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\export_test.zip"
        self.test_account_path = (
            rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\{account_name}"
        )
        self.file_data = file_data
        self.settings_file_name = settings_file_name
        self.account_name = account_name

    def __enter__(self):
        self.clean_data()
        os.mkdir(self.test_account_path)
        with open(
            rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\{self.account_name}\{self.settings_file_name}",
            "w",
        ) as f:
            f.write(self.file_data)

        with zipfile.ZipFile(self.zip_path, mode="w") as zipf:
            zipf.write(
                rf"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\{self.account_name}\{self.settings_file_name}",
                rf"{self.account_name}\{self.settings_file_name}",
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_data()

    def clean_data(self):
        if os.path.isfile(self.zip_path):
            os.remove(self.zip_path)
        if os.path.isdir(self.test_account_path):
            shutil.rmtree(self.test_account_path)


def test_import_profile(qtbot: pytestqt.qtbot.QtBot, create_account, monkeypatch):
    class MockQFileDialog:
        def selectedFiles(self) -> list[str]:
            return [f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\export_test.zip"]

        def exec_(self):
            return True

    main_tab, MockWarningDialog, _ = create_account
    monkeypatch.setattr(
        "app.components.browser_tabs.QtWidgets.QFileDialog", MockQFileDialog
    )

    if "TestAccount" in main_tab.browsers_names:
        for item in main_tab.list_item_arr:
            if item.name == "TestAccount":
                main_tab.delete_profiles([item])
    blocker = qtbot.waitSignal(main_tab.progress_exit_signal)
    with prepare_import_file(
        "TestAccount",
        '{"user-agent": "Mozilla/5.0 (Windows NT 10.0.22; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36", "line_number": "", "proxy": "", "latitude": "", "longitude": "", "extensions": {"2captcha": false, "anticaptcha-plugin_v0.63": false, "chrome_extension_fcc-master": false, "FoxyProxy-Standard": false, "metamask": false, "node_modules": false, "Proxy-SwitchyOmega": false, "selfproxy": false, "selfproxyReact": false, "selfproxy_old": false}, "default_new_tab": ""}',
        "config.json",
    ):
        qtbot.mouseClick(main_tab.list_tools.import_button, QtCore.Qt.LeftButton)
        blocker.wait()

    assert "TestAccount" in main_tab.browsers_names
