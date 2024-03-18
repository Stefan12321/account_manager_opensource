import subprocess
import sys
from app.common.accounts_manager_main.serializer import Config
from app.common.updater.base import get_latest_release, find_path_to_file, download_release, install_release


def copy_settings():
    old_config = Config(f"{folder}/saved_files/settings.json")
    new_config = Config(f"{folder}/accounts_manager/settings.json")
    new_config.update(old_config.config_data)


if __name__ == "__main__":
    latest_version, asset_id = get_latest_release()
    folder = find_path_to_file("elevator.exe").parent
    download_release(folder, asset_id)
    install_release()
    copy_settings()
    subprocess.Popen([f'{folder}/accounts_manager/cleaner/cleaner.exe'], shell=True)
    sys.exit(1)
