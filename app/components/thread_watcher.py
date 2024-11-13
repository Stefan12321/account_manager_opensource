import threading
import time
from typing import List, Callable

from app.components.account_item import QListAccountsWidgetItem


def terminate_thread_watchers():
    for index, th in enumerate(threading.enumerate()):
        if isinstance(th, ThreadWatcher):
            th.stop_thread()
            th.join()


class ThreadWatcher(threading.Thread):
    def __init__(self, list_item_arr: List[QListAccountsWidgetItem], manage_animation_status: Callable):
        self.stop_event = False
        self.manage_animation_status = manage_animation_status
        self.list_item_arr = list_item_arr
        super(ThreadWatcher, self).__init__(target=self.thread_watcher)

    def thread_watcher(self):
        while not self.stop_event:
            for item in self.list_item_arr:
                try:
                    self.manage_animation_status(item)
                except AttributeError:
                    pass
            time.sleep(1)

    def stop_thread(self):
        self.stop_event = True
