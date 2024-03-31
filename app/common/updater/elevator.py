import subprocess
import sys
import tempfile
from pathlib import Path

from app.common.settings import Config
from app.common.updater.base import get_latest_release, find_path_to_file, download_release, install_release


def copy_settings(folder: str | Path, target_folder: str | Path) -> None:
    old_config = Config(f"{folder}/saved_files/settings.json")
    new_config = Config(f"{target_folder}/lib/app/config/settings.json")
    new_config.update(old_config.config_data)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_folder = Path(sys.argv[1])
        latest_version, asset_id = get_latest_release()
        temp = Path(tempfile.gettempdir())
        temp_folder = f"{temp}/account_manager"
        elevator_folder = Path(f"{temp_folder}/elevator")
        download_release(elevator_folder, asset_id)
        install_release(base_folder.parent)
        copy_settings(elevator_folder.parent, base_folder)
        print(f'{base_folder}/accounts_manager/cleaner/cleaner.exe')
        subprocess.Popen([f'{base_folder}/cleaner/cleaner.exe'], shell=True)
        sys.exit(1)
    else:
        print("There is no base folder path in elevator cli arguments")
