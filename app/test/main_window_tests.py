from PyQt5.QtCore import Qt

from main import Window
from PyQt5 import QtCore
import os
import pytest

# Assuming you have a fixture to set up your main window with the CreateAccountButton
@pytest.fixture
def main_window(qtbot):
    # Create and show your main window
    window = Window()
    window.show()
    qtbot.addWidget(window)
    return window


# Test case for the create_profile method
def test_create_profile(qtbot, main_window, monkeypatch):
    # Mock the CreateAccountDialog to simulate user interaction
    class MockLineEdit:
        def __init__(self, text):
            self.text_data = text

        def text(self):
            return self.text_data

    class MockCreateAccountDialog:
        def __init__(self, parent=None):
            self.result = True
            self.account_name = "TestAccount"
            self.new_account_line_edit = MockLineEdit(self.account_name)

        def exec(self):
            return self.result

        def text(self):
            return self.account_name

        def show(self):
            pass

    # monkeypatch.setattr("app.components.create_account_dialog.CreateAccountDialog", MockCreateAccountDialog)
    monkeypatch.setattr("app.components.browser_tabs.CreateAccountDialog", MockCreateAccountDialog)

    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)


    assert "TestAccount" in main_tab.browsers_names
    assert os.path.exists(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\TestAccount")


def test_delete_profile(qtbot, main_window, monkeypatch):
    class MockWarningDialog:
        def __init__(self, text: str, parent=None):
            self.result = 1

        def exec(self):
            return self.result

    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")

    def find_and_check_test_profile():
        for item in main_tab.list_item_arr:
            if item.name == "TestAccount":
                widget = main_tab.listWidget.itemWidget(item)
                widget.CheckBox.setCheckState(QtCore.Qt.CheckState.Checked)

    find_and_check_test_profile()
    monkeypatch.setattr("app.components.browser_tabs.WarningDialog", MockWarningDialog)
    qtbot.mouseClick(main_tab.list_tools.delete_button, Qt.LeftButton)

    assert "TestAccount" not in main_tab.browsers_names
    assert not os.path.exists(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\TestAccount")
