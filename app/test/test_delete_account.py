import os
from app.test.fixtures import main_window, create_account

from PyQt5 import QtCore
from PyQt5.QtCore import Qt


def test_delete_profile(qtbot, open_main_tab_and_select_test_account, monkeypatch):
    class MockWarningDialog:
        def __init__(self, text: str, parent=None):
            self.result = 1

        def exec(self):
            return self.result

    main_tab, account_name = open_main_tab_and_select_test_account

    monkeypatch.setattr("app.components.browser_tabs.WarningDialog", MockWarningDialog)
    qtbot.mouseClick(main_tab.list_tools.delete_button, Qt.LeftButton)

    assert account_name not in main_tab.browsers_names
    assert not os.path.exists(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\TestAccount")


def test_delete_profile_without_selecting_any_accounts(qtbot, main_window, monkeypatch):
    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")
    qtbot.mouseClick(main_tab.list_tools.delete_button, Qt.LeftButton)
    assert main_tab.isActiveWindow()
