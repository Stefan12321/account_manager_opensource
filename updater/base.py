import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import requests
from cryptography.fernet import Fernet
from tqdm import tqdm

BASE_DIR = os.environ["ACCOUNT_MANAGER_BASE_DIR"]
GITHUB_REPO_OWNER = "Stefan12321"
GITHUB_REPO_NAME = "account_manager"
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
            "Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}",
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


def get_latest_release() -> (str, str):
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
    headers = {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return (response.json()["tag_name"], response.json()["assets"][0]["id"])
    return None


def copy_folder(source_folder, destination_folder):
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


def install_release():
    base_folder = find_path_to_file("accounts_manager.zip")
    with zipfile.ZipFile(f"{base_folder}/accounts_manager.zip", 'r') as zip_ref:
        # Get the list of file names inside the ZIP archive
        file_list = zip_ref.namelist()

        # Use tqdm to create a progress bar
        progress_bar = tqdm(total=len(file_list), desc='Installing', unit='file')

        # Extract each file in the ZIP archive and update the progress bar
        for file in file_list:
            try:
                zip_ref.extract(file,
                                f"{base_folder}/accounts_manager")  # This scary method just get the parent folder path
            except Exception as e:
                print(f"Error: {e}")
            progress_bar.update(1)

        progress_bar.close()


def find_path_to_file(file_in_base_folder) -> Path:
    base_folder = Path(sys.executable).parent
    while base_folder:
        folder_path = Path(base_folder)
        files = folder_path.glob("*")
        for file in files:
            if file.is_file() and file.name == file_in_base_folder:
                return base_folder
        if len(base_folder.parents) == 0:
            raise FileNotFoundError  # Exception("Could not find base folder")
        else:
            base_folder = base_folder.parent


def run_main_app():
    path = find_path_to_file("Accounts manager.exe")
    subprocess.Popen([f'{path}/Accounts manager.exe'], shell=True)
