import os
import shutil

from cx_Freeze import setup, Executable

from accounts_manager_main.serializer import Config


def build():
    BUILD_FOLDER = "./build/accounts_manager"
    try:
        shutil.rmtree('build')
        shutil.rmtree('dist')
    except Exception as e:
        print(f"[ERROR] {e}")
    base = None

    executables = [
        Executable("main.py",
                   target_name='Accounts manager.exe',
                   base=base),

    ]

    includes = ['extension', 'icons', './settings.json', './win_versions.json',
                'chrome_versions.json', "./tooltips.csv"]

    packages = ["os", "threading", "time", "PyQt5", "selenium", "json", "user_agents", "undetected_chromedriver",
                "html_editor", "accounts_manager_main", "pycparser", "account_manager_private_part"]

    options = {
        'build_exe': {
            'build_exe': BUILD_FOLDER,
            'packages': packages,
            'include_files': includes,
        }
    }

    setup(
        name="accounts_manager",
        options=options,
        version=1.0,
        description='',
        executables=executables,
    )

    os.makedirs(f'{BUILD_FOLDER}/profiles')
    os.makedirs(f'{BUILD_FOLDER}/logs')
    os.makedirs(f'{BUILD_FOLDER}/logs/Main_log')
    conf = Config(f"{BUILD_FOLDER}/settings.json")
    conf.update({"astroproxy_api": "", "spreadsheetId": ""})
