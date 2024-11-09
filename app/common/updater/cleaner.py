import os
import shutil
import tempfile
from pathlib import Path

from tqdm import tqdm

from app.common.updater.base import run_main_app


def clean_temp_files():
    temp = Path(tempfile.gettempdir())
    temp_folder = f"{temp}/account_manager"
    # Get the list of files and directories to delete
    directories_to_remove = [temp_folder]
    files_to_remove = []

    # Calculate the total number of items to delete (for the progress bar)
    total_items = len(directories_to_remove) + len(files_to_remove)

    # Create a tqdm progress bar with the total number of items
    with tqdm(total=total_items, desc="Cleaning temporary files", unit="item") as pbar:
        # Remove directories
        for directory in directories_to_remove:
            shutil.rmtree(directory)
            pbar.update(1)  # Update progress bar for each directory removed

        # Remove files
        for file_path in files_to_remove:
            os.remove(file_path)
            pbar.update(1)  # Update progress bar for each file removed


if __name__ == '__main__':
    clean_temp_files()
    run_main_app()
