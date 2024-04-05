import pytest
from PyQt5.QtCore import Qt

from app.test.fixtures import main_window, create_account
import os


def test_create_profile(qtbot, create_account, monkeypatch):
    main_tab, _, _ = create_account
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)

    assert "TestAccount" in main_tab.browsers_names
    assert os.path.exists(fr"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}\profiles\TestAccount")


def test_create_account_with_same_account_name(qtbot, create_account, monkeypatch):
    main_tab, MockWarningDialog, _ = create_account
    account_name = "TestAccount"
    if account_name not in os.listdir(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/profiles"):
        main_tab.create_profile(account_name)
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)
    assert MockWarningDialog.was_called()
    assert MockWarningDialog._called_text == "Account with name TestAccount is already exist. Try different name"


@pytest.mark.parametrize("symbol", r'[\\/:*?"<>|]')
def test_create_account_with_forbidden_symbols(qtbot, symbol, create_account, monkeypatch):
    main_tab, MockWarningDialog, MockCreateAccountDialog = create_account
    account_name = f"Test{symbol}Account"
    MockCreateAccountDialog.account_name = account_name
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)
    assert MockWarningDialog.was_called()
    assert MockWarningDialog._called_text == rf'Used a forbidden symbol {symbol} at position 4. Do not use [\\/:*?"<>|[\]] characters'


def test_create_account_with_too_long_name(qtbot, create_account, monkeypatch):
    main_tab, MockWarningDialog, MockCreateAccountDialog = create_account
    account_name = ''.join(["a" for i in range(61)])
    MockCreateAccountDialog.account_name = account_name
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)
    assert MockWarningDialog.was_called()
    assert MockWarningDialog._called_text == "The name is too long, use less than 60 characters"


def test_create_account_with_empty_name(qtbot, create_account, monkeypatch):
    main_tab, MockWarningDialog, MockCreateAccountDialog = create_account
    account_name = ''
    MockCreateAccountDialog.account_name = account_name
    qtbot.mouseClick(main_tab.list_tools.create_profile_button, Qt.LeftButton)
    assert MockWarningDialog.was_called()
    assert MockWarningDialog._called_text == "The name can't be empty"
