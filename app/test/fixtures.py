import os

import pytest
import pytestqt.qtbot
from PyQt5.QtCore import qWarning, Qt

from main import Window


@pytest.fixture
def main_window(qtbot):
    # Create and show your main window
    window = Window()
    window.show()
    qtbot.addWidget(window)
    return window


@pytest.fixture
def create_account(main_window, qtbot: pytestqt.qtbot.QtBot, monkeypatch):
    # Mock the CreateAccountDialog to simulate user interaction
    class MockLineEdit:
        def __init__(self, text):
            self.text_data = text

        def text(self):
            return self.text_data

    class MockCreateAccountDialog:
        account_name = "TestAccount"

        def __init__(self, parent=None):
            self.result = True
            self.new_account_line_edit = MockLineEdit(self.account_name)

        def exec(self):
            return self.result

        def text(self):
            return self.account_name

        def show(self):
            pass  # virtual method that must do nothing in that test case

    class MockWarningDialog:
        _called = False
        _called_text = None

        def __init__(self, *args, **kwargs):
            qWarning('this is a WARNING message')

        @classmethod
        def was_called(cls):
            return cls._called

        def __new__(cls, *args, **kwargs):
            cls._called = True
            cls._called_text = args[0]
            return super().__new__(cls)

        def exec(self):
            self._called = True
            return True

    monkeypatch.setattr("app.components.browser_tabs.WarningDialog", MockWarningDialog)
    monkeypatch.setattr("app.components.browser_tabs.CreateAccountDialog", MockCreateAccountDialog)

    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")
    return main_tab, MockWarningDialog, MockCreateAccountDialog


@pytest.fixture
def open_main_tab_and_select_test_account(main_window: Window, qtbot: pytestqt.qtbot.QtBot, monkeypatch):
    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")
    account_name = "TestAccount"

    def find_and_check_test_profile():
        for item in main_tab.list_item_arr:
            if item.name == account_name:
                widget = main_tab.listWidget.itemWidget(item)
                widget.CheckBox.setCheckState(Qt.CheckState.Checked)
    if account_name not in os.listdir(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles"):
        main_tab.create_profile(account_name)
    find_and_check_test_profile()
    return main_tab, account_name
