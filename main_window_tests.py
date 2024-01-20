import os
import shutil

from PyQt5.QtCore import Qt

from main import MainWindow, CreateAccountDialog
from PyQt5 import QtWidgets, QtCore
import pytest
import os
import pytest
from PyQt5.QtWidgets import QPushButton, QDialog


# Assuming you have a fixture to set up your main window with the CreateAccountButton
@pytest.fixture
def main_window(qtbot):
    # Create and show your main window
    window = MainWindow()
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
        def __init__(self):
            self.result = True
            self.account_name = "TestAccount"
            self.lineEdit = MockLineEdit(self.account_name)

        def exec(self):
            return self.result

        def text(self):
            return self.account_name

        def show(self):
            pass

    # Monkeypatch the CreateAccountDialog class to use the mock
    # monkeypatch.setattr("main.CreateAccountDialog", MockCreateAccountDialog)
    monkeypatch.setattr("main.CreateAccountDialog", MockCreateAccountDialog)

    # Trigger the button click event
    qtbot.mouseClick(main_window.CreateAccountButton, Qt.LeftButton)
    # Now, you can assert the expected changes in the main window state or any other relevant checks
    assert "TestAccount" in main_window.browsers_names
    assert os.path.exists(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles\TestAccount")


def test_delete_profile(qtbot, main_window, monkeypatch):
    class MockMessageBox:
        Warning = 0
        Ok = 0
        Cancel = 0

        def __init__(self):
            self.result = 1024

        def setIcon(self, icon):
            pass

        def setText(self, text):
            pass

        def setWindowTitle(self, title):
            pass

        def setStandardButtons(self, buttons):
            pass

        def exec(self):
            return self.result

    def find_and_check_test_profile():
        for item in main_window.list_item_arr:
            if item.name == "TestAccount":
                widget = main_window.listWidget.itemWidget(item)
                widget.checkBox.setCheckState(QtCore.Qt.CheckState.Checked)

    find_and_check_test_profile()
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox", MockMessageBox)
    qtbot.mouseClick(main_window.pushButtonDeleteAccounts, Qt.LeftButton)

    assert "TestAccount" not in main_window.browsers_names
    assert not os.path.exists(fr"{os.path.dirname(os.path.realpath(__file__))}\profiles\TestAccount")
