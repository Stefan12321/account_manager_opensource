import os
import shutil
from cx_Freeze import setup, Executable
from app.common.settings.serializer import Config


def build():
    APP_FOLDER = "app"
    BUILD_FOLDER = "build/accounts_manager"
    icon_path = f"{APP_FOLDER}/resource/logo.ico"
    try:
        shutil.rmtree('build')
        shutil.rmtree('dist')
    except Exception as e:
        print(f"[ERROR] {e}")
    base = None

    executables = [
        Executable("main.py",
                   target_name='Accounts manager.exe',
                   base=base,
                   icon=icon_path),
    ]

    includes = []

    packages = ["os", "threading", "time", "PyQt5", "selenium", "json", "undetected_chromedriver", "pycparser",
                "account_manager_private_part"]
    build_exe_options = {
        'build_exe': BUILD_FOLDER,
        'packages': packages,
        'include_files': includes,
    }
    options = {
        'build_exe': build_exe_options
    }

    setup(
        name="accounts_manager",
        options=options,
        version=1.0,
        description='',
        executables=executables,
    )

    os.makedirs(f'{BUILD_FOLDER}/profiles')
    os.makedirs(f'{BUILD_FOLDER}/extension')
    os.makedirs(f'{BUILD_FOLDER}/logs')
    os.makedirs(f'{BUILD_FOLDER}/logs/Main_log')
    conf = Config(f"{BUILD_FOLDER}/lib/app/config/settings.json")
    conf.update({"version": {
        "type": "dropdown",
        "values": {
            "opensource": True,
            "private": False
        }
    }, })


if __name__ == "__main__":
    build()
