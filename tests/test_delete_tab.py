import pytest
from PyQt5.QtCore import Qt

from main import Window
from tests.fixtures import main_window, prepare_config  # noqa


@pytest.mark.parametrize(
    "prepare_config",
    [
        (
            {
                "version": {
                    "type": "dropdown",
                    "values": {"opensource": True, "private": False},
                },
                "theme": {"type": "dropdown", "values": {"Dark": True, "Light": False}},
                "tabs": {"type": "invisible", "values": {"test_tab": []}},
                "chrome_version": "120",
                "debug": False,
                "default_new_tab": "",
                "onload_pages": ["index"],
                "auto_set_chrome_version": True,
                "check_for_updates": False,
                "change_location": False,
                "set_random_window_size": False,
                "accounts_tooltips": False,
                "python_console": True,
            },
        )
    ],
)
def test_tab_delete(prepare_config, main_window: Window, qtbot):
    window = main_window
    qtbot.mouseClick(
        window.browser_list_Interface.tabBar.itemMap["test_tab"].closeButton,
        Qt.LeftButton,
    )
    assert "test_tab" not in window.browser_list_Interface.tabBar.itemMap
