import os
import queue
import random

import screeninfo
import selenium
import undetected_chromedriver
import undetected_chromedriver as uc
from PyQt5.QtCore import pyqtSignal
from selenium.common import WebDriverException

from html_editor.main import create_html
from user_agents.main import get_user_agent
from .serializer import Config, MainConfig


class WebBrowser:
    def __init__(self, base_path, account_name,
                 logger, _queue: queue.Queue, main_config: MainConfig, set_locals_signal: pyqtSignal, start_browser=True):
        self.set_locals_signal = set_locals_signal
        self.logger = logger
        self.base_dir = base_path
        self.path = fr"{self.base_dir}\profiles\{account_name}"
        self.logger.info(fr"PATH {self.path}")
        self.config_main = main_config
        self.config = Config(fr'{self.path}\config.json')
        self.account_name = account_name
        self._queue = _queue
        self.version_main = int(self.config_main.config_data["chrome_version"])
        self.onload_pages = self.config_main.config_data["onload_pages"]
        if start_browser:
            self.start_undetected_chrome()

    def _prepare_undetected_chrome(self) -> undetected_chromedriver.Chrome:
        options = self._set_up_options()
        try:
            driver = uc.Chrome(options=options, version_main=self.version_main)
            if self.config_main.config_data["set_random_window_size"]:
                self.set_random_window_size(driver)
            self.open_onload_pages(driver)
            return driver
        except Exception as e:
            self.logger.error(e)
            raise e

    def _set_up_options(self) -> undetected_chromedriver.ChromeOptions:
        if os.path.isdir(self.path):
            user_agent_ = self.prepare_user_agent()
        base_dir = os.environ["ACCOUNT_MANAGER_BASE_DIR"]
        self.logger.info(f"Base directory: {base_dir}")
        options = uc.ChromeOptions()
        options.add_argument(f'--user-data-dir={self.path}')
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-first-run")
        if "extensions" in self.config.config_data:
            extensions = ','.join(
                fr'{base_dir}\extension\{key}' for key in self.config.config_data["extensions"].keys() if
                self.config.config_data["extensions"][key] is True)
            options.add_argument(fr'--load-extension={extensions}')
        options.add_argument(f"--user-agent={user_agent_}")
        options.add_argument("--enable-features=PasswordImport")
        # TODO: disable UDP is a bad solution.
        #       Possible solution: Need to faked IP using
        #       STUN/TURN server?
        options.add_argument(
            "--webrtc-ip-handling-policy=disable_non_proxied_udp")
        return options

    def start_undetected_chrome(self):
        driver = self._prepare_undetected_chrome()

        self.set_locals_signal.emit(locals())
        try:
            while self.is_driver_alive(driver):
                try:
                    signal = self._queue.get(timeout=1)
                    command = signal[0]
                    data = signal[1]
                    self.logger.info(f"Signal received: {command}")
                    if command == "open_in_new_tab":
                        driver.execute_script(f"window.open('{data}', '_blank')")
                        if self.config_main.config_data[
                            "change_location"] and "location" in self.config.config_data and \
                                self.config.config_data["location"][0] != "" and \
                                self.config.config_data["location"][0] != "":
                            driver.switch_to.window(driver.window_handles[-1])
                            latitude = float(self.config.config_data["location"][0])
                            longitude = float(self.config.config_data["location"][1])
                            self.logger.info(f"Changing browser location to {latitude}, {longitude}")
                            self.setup_geolocation(driver, latitude, longitude)

                except queue.Empty:
                    pass
        except selenium.common.exceptions.WebDriverException:
            driver.quit()
            self.logger.info('driver quit')

    @staticmethod
    def is_driver_alive(driver: undetected_chromedriver.Chrome) -> bool:
        try:
            driver.title  # Accessing a property to check if the driver is responsive
            return True
        except WebDriverException:
            return False

    def prepare_user_agent(self) -> str:
        #  get user agent from config.json

        if "user-agent" not in self.config.config_data:
            user_agent_ = get_user_agent(os=("win"), navigator=("chrome"), device_type=("desktop"))
            self.config.update({'user-agent': user_agent_})

        user_agent_ = self.config.config_data["user-agent"]
        return user_agent_

    def open_onload_pages(self, driver: undetected_chromedriver.Chrome):
        index = f"{self.path}/init.html"
        for page in self.onload_pages:
            if page == "index":
                if os.path.exists(index):
                    driver.get(index)
                else:
                    create_html(index, self.account_name)
                    driver.get(index)
            else:
                try:
                    driver.execute_script(f"window.open('{page}', '_blank')")
                except Exception as e:
                    self.logger.error(e)

    @staticmethod
    def setup_geolocation(driver: uc.Chrome, latitude: float, longitude: float):
        map_coordinates = dict({
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": 100
        })
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", map_coordinates)

    @staticmethod
    def set_random_window_size(driver: uc.Chrome):
        screen_resolutions = [
            [800, 600],
            [1024, 768],
            [1280, 720],
            [1280, 800],
            [1366, 768],
            [1440, 900],
            [1600, 900],
            [1680, 1050],
            [1920, 1080],
            [1920, 1200],
            [2560, 1600],
            [2560, 1440],
            [3840, 2160],
            [4096, 2160],
            [5120, 2880],
            [7680, 4320]
        ]
        monitors = screeninfo.get_monitors()
        try:
            main_monitor = [monitor for monitor in monitors if monitor.is_primary][0]
            resolution_index = screen_resolutions.index([main_monitor.width, main_monitor.height])
            size = random.choice(screen_resolutions[:resolution_index])
        except ValueError:
            size = random.choice(screen_resolutions)
        width = size[0]
        height = size[1]
        driver.set_window_size(width, height)
