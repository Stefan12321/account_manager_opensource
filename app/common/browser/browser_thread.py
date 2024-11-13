import logging
import queue
import sys
import threading

from PyQt5.QtCore import pyqtSignal
from app.common.browser.chrome_version_detector import ChromeNotFoundError
from app.common.browser.web_browser import WebBrowser
from app.common.settings.serializer import Config
if sys.platform == 'win32':
    from app.common.password_decryptor.passwords_decryptor import do_decrypt
class BrowserThread(threading.Thread):
    def __init__(self, name: str, _queue: queue.Queue, logger: logging.Logger, set_locals_signal: pyqtSignal, base_path: str, main_config: Config, exception_signal: pyqtSignal):
        super().__init__(target=self.run_browser, args=(name, _queue, logger, set_locals_signal, base_path, main_config))
        self.exception_signal: pyqtSignal = exception_signal

    def run_browser(self, name: str, _queue: queue.Queue, logger: logging.Logger, set_locals_signal: pyqtSignal, base_path: str, main_config: Config):
        logger.info(f"Log file created for {name}")
        if sys.platform == "win32":
            try:
                do_decrypt(fr"{base_path}/profiles\{name}")
            except Exception as e:
                logger.error(f"Passwords decrypt error: {e}")

        logger.info(f"Browser {name} started")
        
        WebBrowser(base_path=base_path, account_name=name, logger=logger, _queue=_queue,
                main_config=main_config,
                set_locals_signal=set_locals_signal)


    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except ChromeNotFoundError:
            breakpoint()
            self.exception_signal.emit("Please install Chrome boser or Chromium, if you use linux")


    def get_exception(self):
        return self._exception