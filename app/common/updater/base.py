import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Sequence

import requests
from cryptography.fernet import Fernet
from tqdm import tqdm

BASE_DIR = os.environ["ACCOUNT_MANAGER_BASE_DIR"]
GITHUB_REPO_OWNER = "Stefan12321"
GITHUB_REPO_NAME = "account_manager_opensource"

try:
    with open(f"{BASE_DIR}/key", "rb") as key_file:
        with open(f"{BASE_DIR}/token", "rb") as token_file:
            encryption_key = key_file.read()
            token = token_file.read()
            cipher = Fernet(encryption_key)
            GITHUB_ACCESS_TOKEN = cipher.decrypt(token).decode()
except FileNotFoundError:
    pass


def download_release(folder, repo_id):
    release_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/assets/{repo_id}"
    download_path = f"{folder}/accounts_manager.zip"

    try:
        with requests.get(release_url, headers={
            "Accept": "application/octet-stream",
            "X-GitHub-Api-Version": "2022-11-28"},
                          stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            with open(download_path, "wb") as f, tqdm(
                    desc="Downloading", total=total_size, unit="B", unit_scale=True
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

        return True
    except requests.exceptions.RequestException as e:
        print("Error occurred while downloading the update:", e)
        return False


def get_latest_release() -> Sequence[str] or None:
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["tag_name"], response.json()["assets"][0]["id"]
    return None


def copy_folder(source_folder: Path, destination_folder: Path):
    if destination_folder.exists():
        shutil.rmtree(destination_folder)
    try:
        total_files = sum([len(files) for _, _, files in os.walk(source_folder)])
        with tqdm(total=total_files, unit="file", desc="Copy files", ) as pbar:
            shutil.copytree(source_folder, destination_folder, symlinks=False, copy_function=update_progress_bar(pbar))
        print(f"\nFolder '{source_folder}' copied to '{destination_folder}' successfully.")
    except FileExistsError:
        print(f"Error: The destination folder '{destination_folder}' already exists.")
    except Exception as e:
        print(f"Error: {e}")


def update_progress_bar(pbar):
    def inner(src, dst):
        pbar.update(1)
        return shutil.copy2(src, dst)

    return inner


def install_release(target_folder: str | Path):
    temp = Path(tempfile.gettempdir())
    temp_folder = f"{temp}/account_manager"
    with zipfile.ZipFile(f"{temp_folder}/elevator/accounts_manager.zip", 'r') as zip_ref:
        # Get the list of file names inside the ZIP archive
        file_list = zip_ref.namelist()

        # Use tqdm to create a progress bar
        progress_bar = tqdm(total=len(file_list), desc='Installing', unit='file')

        # Extract each file in the ZIP archive and update the progress bar
        for file in file_list:
            try:
                zip_ref.extract(file,
                                f"{target_folder}")
            except Exception as e:
                print(f"Error: {e}")
            progress_bar.update(1)

        progress_bar.close()


def find_path_to_file(file_in_base_folder) -> Path or None:
    if getattr(sys, 'frozen', False):
        base_folder = Path(sys.executable).parent
    else:
        base_folder = Path(__file__).parent
    for root, dirs, files in os.walk(base_folder):
        if file_in_base_folder in files:
            return Path(root, file_in_base_folder)
    return None


def run_main_app():
    path = find_path_to_file("Accounts manager.exe")
    subprocess.Popen([f'{path}/Accounts manager.exe'], shell=True)


if __name__ == '__main__':
    print(find_path_to_file("base.py"))
