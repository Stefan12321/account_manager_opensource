import os
from pathlib import Path

import pytestqt.qtbot  # noqa
from PyQt5 import QtCore  # noqa
from PyQt5.QtCore import Qt

from tests.fixtures import main_window, open_main_tab_and_select_test_account  # noqa


def test_export_profile(
    qtbot: pytestqt.qtbot.QtBot, open_main_tab_and_select_test_account, monkeypatch
):
    main_tab, account_name = open_main_tab_and_select_test_account

    path_to_export = Path(f"{os.environ['ACCOUNT_MANAGER_BASE_DIR']}/export.zip")
    if path_to_export.exists():
        os.remove(path_to_export)
    blocker = qtbot.waitSignal(main_tab.progress_exit_signal)
    qtbot.mouseClick(main_tab.list_tools.export_button, Qt.LeftButton)
    blocker.wait()
    assert path_to_export.exists()


def test_export_profile_without_selected_profile(qtbot, main_window, monkeypatch):
    main_tab = main_window.browser_list_Interface.get_tab_with_name("All")
    qtbot.mouseClick(main_tab.list_tools.export_button, Qt.LeftButton)
    assert main_tab.isActiveWindow()
