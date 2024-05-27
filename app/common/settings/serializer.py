import json
import logging
import os
import pathlib
import shutil
from typing import List

APP_VERSION = "0.6.8"


class Serializer:

    def serialize(self, data: dict, path: str) -> None:
        """
        :param path: path to config.json
        :param data: dict of settings
        :return: None
        """

        with open(path, 'w', encoding='utf-8') as f:
            try:
                json.dump(data, f)
                print(f"Serialized data: {data}")
            except Exception as e:
                print(e)

    def deserialize(self, path: str) -> dict:
        """
        :return: list of deserialized data from config.json
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def update(self, data: dict, path: str) -> bool:
        try:
            old_data = self.deserialize(path)
            old_data.update(data)
            self.serialize(old_data, path)
            return True
        except Exception as e:
            logging.error(e)
            return False


class Config(Serializer):
    def __init__(self, path: str):
        self.path = path
        self.config_data = {}
        self._read_config()

    def _read_config(self):
        try:
            self.config_data.update(self.deserialize(self.path))
        except FileNotFoundError:
            os.makedirs(self.path)
            self.serialize({}, self.path)
        except PermissionError:
            path = pathlib.Path(self.path)
            if path.is_dir():
                shutil.rmtree(path)
            self.serialize({}, self.path)

    def update(self, data: dict, path=None) -> bool:
        resp = super().update(data, self.path)
        if resp:
            self.config_data = self.deserialize(self.path)
        return resp

    def get_data_by_key(self, key: str, default_value=None):
        if key in self.config_data:
            return self.config_data[key]
        else:
            logging.warning(f"There is no {key} in config file")
            self.update({key: default_value})
            return default_value

    def __str__(self):
        res = ""
        for key, value in self.config_data.items():
            res += f"{key}: {value}\n"
        return res


class MainConfig(Serializer):
    def __init__(self, path: str or List[str]):
        if isinstance(path, str):
            self.paths = [path]
        elif isinstance(path, list):
            self.paths = path
        else:
            raise TypeError()
        self.config_paths = {}
        self.config_data = {}
        self._read_configs()
        self._try_to_read_private_config()

    def _read_configs(self):
        for path in self.paths:
            try:
                self.config_data.update(self.deserialize(path))
                self.config_paths[path] = self.deserialize(path)
            except FileNotFoundError:
                os.makedirs(path)
                self.serialize({}, path)
            except PermissionError:
                self.serialize({}, path)

    def _try_to_read_private_config(self):
        if self.config_data["version"]["values"]["private"] is True:
            try:
                self.paths.append(
                    f'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/account_manager_private_part/settings.json')
                self._read_configs()
            except (FileNotFoundError, PermissionError):
                logging.error("You can't use this version of app")
                self.update({"version": {
                    "type": "dropdown",
                    "values": {
                        "opensource": True,
                        "private": False
                    }
                }, })
                shutil.rmtree(f'{os.environ["ACCOUNT_MANAGER_BASE_DIR"]}/account_manager_private_part')

    def update(self, data: dict, path=None) -> bool:
        for _path in self.paths:
            data_to_update = {}
            for key in data.keys():
                if key in self.config_paths[_path]:
                    data_to_update[key] = data[key]
            resp = super().update(data_to_update, _path)
            if resp:
                self.config_paths[_path] = self.deserialize(_path)

        return resp

    def get_data_by_key(self, key: str, default_value=None):
        if key in self.config_data:
            return self.config_data[key]
        else:
            logging.warning(f"There is no {key} in config file")
            self.update({key: default_value})
            return default_value
