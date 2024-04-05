import os
from app.test.fixtures import main_window, create_account

from PyQt5 import QtCore
from PyQt5.QtCore import Qt


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
