import json
import logging
import os
from typing import List


class Serializer:

    def serialize(self, data: dict, path: str) -> None:
        """
        :param path: path to config.json
        :param data: dict of settings
        :return: None
        """

        with open(path, 'w') as f:
            try:
                json.dump(data, f)
                print(f"Serialized data: {data}")
            except Exception as e:
                print(e)

    def deserialize(self, path: str) -> dict:
        """
        :return: list of deserialized data from config.json
        """
        with open(path, 'r') as f:
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

    def update(self, data: dict) -> bool:
        for path in self.paths:
            data_to_update = {}
            for key in data.keys():
                if key in self.config_paths[path]:
                    data_to_update[key] = data[key]
            resp = super().update(data_to_update, path)
            if resp:
                self.config_paths[path] = self.deserialize(path)
            else:
                return resp
        return resp


def serialize(path, data: dict):
    """

    :param path: path to config.json
    :param data: dict of settings
    :return: None
    """
    with open(path, 'w') as f:
        try:
            json.dump(data, f)
            print(f"Serialized data: {data}")
        except Exception as e:
            print(e)


def deserialize(path) -> dict:
    """

    :param path: path to config.json
    :return: list of deserialized data from config.json
    """
    with open(path, 'r') as f:
        data = json.load(f)

    return data
