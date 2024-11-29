from PyQt5.QtCore import Qt, QTimer

from app.components.create_new_tab_dialog import CreateTabDialog
from tests.fixtures import main_window, prepare_config_decorator  # noqa

from main import Window


def test_tab_create(prepare_config_decorator, main_window: Window, qtbot):
    window = main_window

    # Find the dialog window (exec() blocks, so we simulate the interaction using QTimer)
    def find_and_interact_with_dialog():
        nonlocal window
        nonlocal qtbot
        children = window.browser_list_Interface.children()
        dialog = None
        for child in children:
            if isinstance(child, CreateTabDialog):
                dialog = child
                break
        assert dialog is not None, "Dialog was not found."
        qtbot.keyClicks(dialog.new_account_line_edit, "test_tab")
        qtbot.mouseClick(dialog.yesButton, Qt.LeftButton)

    # Schedule interaction with the dialog
    QTimer.singleShot(5000, find_and_interact_with_dialog)
    # Simulate clicking the add tab button
    qtbot.mouseClick(window.browser_list_Interface.tabBar.addButton, Qt.LeftButton)

    # Allow the event loop to process
    qtbot.wait(10)
    assert "test_tab" in window.browser_list_Interface.tabBar.itemMap
