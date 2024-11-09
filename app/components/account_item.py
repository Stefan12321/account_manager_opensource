import logging
import os
import shutil
import threading
from pathlib import Path
from typing import Any, List

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData, QRect
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor, QKeySequence
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QAction, QShortcut
from qfluentwidgets import FluentIcon, ToolTipFilter, ToolTipPosition, RoundMenu, Action, MenuAnimationType

from app.common.settings.serializer import MainConfig, Config

main_config = MainConfig(os.environ["ACCOUNT_MANAGER_PATH_TO_SETTINGS"])
if main_config.config_data["version"]["values"]["private"] is True:
    from account_manager_private_part.app.components.settings_dialog import SettingsDialogPrivate as SettingsDialog
else:
    from app.components.settings_dialog import SettingsDialog
from app.components.one_accout_line_widget import Ui_Form


class QWidgetOneAccountLine(QWidget, Ui_Form):
    locals_signal = pyqtSignal(dict)

    def __init__(self, name: str, main_config: MainConfig, logger: logging.Logger, index: int, parent=None):
        super(QWidgetOneAccountLine, self).__init__(parent)
        self.is_animation_running = None
        self.parent_widget = parent
        self.index = index
        self.logger = logger
        self.name = name
        self.config_name = None
        self.path = fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/profiles/{self.name}'
        self.main_config = main_config
        self.config = Config(fr"{self.path}/config.json")
        self._queue = None
        self.locals = None
        self.locals_signal.connect(self.set_locals)

        self.setupUi(self)
        self.settings_button.setIcon(FluentIcon.SETTING)
        self.settings_button.clicked.connect(self.open_settings)
        self.account_name_label.name_changed.connect(self._update_name)
        self.stop_animation()
        self._init_icon()

        if main_config.config_data["accounts_tooltips"]:
            self.setToolTips()
            self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.TOP))

        if "name" in self.config.config_data:
            self.set_account_name(self.config.config_data["name"])
        else:
            self.set_account_name(self.name)

    def get_name(self) -> str:
        return self.name

    def _init_icon(self):
        if "icon" in self.config.config_data:
            if os.path.exists(self.config.config_data["icon"]):
                icon = QIcon(self.config.config_data["icon"])
            else:
                self.logger.error(f"icon {self.config.config_data['icon']} not found. Set default")
                icon = QIcon(f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/Google_Chrome_icon.svg')
        else:
            icon = QIcon(f'{os.environ["ACCOUNT_MANAGER_PATH_TO_RESOURCES"]}/Google_Chrome_icon.svg')

        self.browser_icon.setIcon(icon)
        self.browser_icon.icon_changed.connect(self._set_new_icon)

    def _set_new_icon(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setNameFilters(["Image Files (*.png *.jpg *.bmp *.svg)"])
        dlg.setWindowTitle("Choose new icon for profile")

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            file_path = Path(filenames[0])
            base_path = Path(os.environ["ACCOUNT_MANAGER_BASE_DIR"])
            new_file_path = Path(f"{self.path}/accounts_manager_icons/{file_path.name}")
            os.makedirs(f"{self.path}/accounts_manager_icons", exist_ok=True)
            shutil.copy(file_path, new_file_path)
            self.browser_icon.setIcon(QIcon(str(new_file_path.relative_to(base_path))))
            self.config.update({"icon": str(new_file_path.relative_to(base_path))})

    def _update_name(self, name: str):
        os.rename(Path(self.path), f"{Path(self.path).parent}/{name}")
        self.name = name
        self.path = fr'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}\profiles\{self.name}'

    def setToolTips(self):
        self.setToolTip(str(self.config))

    def open_settings(self):
        dlg = SettingsDialog(_queue=self._queue,
                             logger=self.logger,
                             main_config=self.main_config,
                             account_name=self.name,
                             browser_locals=self.locals)
        dlg.show()
        dlg.exec()

    def set_account_name(self, name: str):
        self.account_name_label.setText(name)

    def set_locals(self, _locals: dict[str, Any]):
        self.locals = _locals

    def enterEvent(self, event):
        self.parent().parent()._setHoverRow(self.index)

    def start_animation(self):
        self.running_ring.show()
        self.is_animation_running = True

    def stop_animation(self):
        self.running_ring.hide()
        self.is_animation_running = False

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.name)
            drag.setMimeData(mime)
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.transparent)  # Fill with transparent color
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)  # Enable anti-aliasing for smooth edges
            rounded_rect = QRect(0, 0, self.width(), self.height()).adjusted(1, 1, -1, -1)
            painter.setBrush(QColor(60, 60, 60, 100))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rounded_rect, 5, 5)  # Adjust the radius values for roundness
            painter.end()
            drag.setHotSpot(e.pos())
            drag.setPixmap(pixmap)
            drag.exec_(Qt.MoveAction)

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)
        # add sub menu
        submenu = RoundMenu("Send to tab", self)
        submenu.setIcon(FluentIcon.ADD)
        send_to_tab_actions_list: List[Action] = []
        for tab in self.parent_widget.parent_widget.tabBar.items:
            tab_name = tab.routeKey()
            if tab_name != "All":
                action = Action(FluentIcon.FOLDER, tab_name)
                action.triggered.connect(
                    lambda checked, tab_key=tab_name: self.parent_widget.add_account_to_tab(self.name, tab_key))
                send_to_tab_actions_list.append(action)
        submenu.addActions(send_to_tab_actions_list)

        menu.addMenu(submenu)
        current_tab_name = self.parent_widget.parent_widget.tabBar.currentTab().routeKey()
        if current_tab_name != "All":
            remove_from_tab_action = Action(FluentIcon.DELETE, f"Remove {self.get_name()} from current tab")
            remove_from_tab_action.triggered.connect(lambda: self.parent_widget.remove_account_from_tab(self.name))
            menu.addAction(remove_from_tab_action)

        settings_action = Action(FluentIcon.SETTING, "Settings")
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        # add separator
        menu.addSeparator()
        select_all_action = QAction('Select all', shortcut='Ctrl+A')
        select_all_action.triggered.connect(lambda: self.parent_widget.list_tools.CheckBox.nextCheckState())

        menu.addAction(select_all_action)

        # show menu
        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)


class QListAccountsWidgetItem(QListWidgetItem):

    def __init__(self, name: str, widget: QWidgetOneAccountLine, main_config: MainConfig, parent=None, ):
        super(QListAccountsWidgetItem, self).__init__(parent)
        self.name = name
        self.main_config = main_config
        self.status: bool = False
        self.thread: threading.Thread or None = None
        self.widget = widget
        self.widget.account_name_label.name_changed.connect(self.update_name)
        self.setSizeHint(self.widget.sizeHint())

    def update_name(self, old_name: str, name: str):
        self.name = name
