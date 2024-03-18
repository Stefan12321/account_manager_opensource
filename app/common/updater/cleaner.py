import os
import shutil

from tqdm import tqdm

from app.common.updater.base import find_path_to_file, run_main_app


def clean_temp_files():
    folder = find_path_to_file("accounts_manager.zip")

    # Get the list of files and directories to delete
    directories_to_remove = [f"{folder}/elevator", f"{folder}/saved_files"]
    files_to_remove = [f"{folder}/accounts_manager.zip"]

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
