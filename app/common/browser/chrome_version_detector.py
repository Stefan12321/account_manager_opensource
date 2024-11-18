#
# Programmatically detect the version of the Chrome web browser installed on the PC.
# Compatible with Windows, Mac, Linux.
# Written in Python.
# Uses native OS detection. Does not require Selenium nor the Chrome web driver.
#

import os
import re
from sys import platform

class ChromeNotFoundError(Exception):
    
    def __init__(self):
        message = "Chrome not found, please install Google Chrome if you using windows or Chromium if you using Linux"
        super().__init__(message)

def extract_version_registry(output: str) -> str | None:
    try:
        google_version = ''
        for letter in output[output.rindex('DisplayVersion    REG_SZ') + 24:]:
            if letter != '\n':
                google_version += letter
            else:
                break
        return google_version.strip()
    except TypeError:
        return


def extract_version_folder() -> str | None:
    # Check if the Chrome folder exists in the x32 or x64 Program Files folders.
    for i in range(2):
        path = 'C:\\Program Files' + (' (x86)' if i else '') + '\\Google\\Chrome\\Application'
        if os.path.isdir(path):
            paths = [f.path for f in os.scandir(path) if f.is_dir()]
            for path in paths:
                filename = os.path.basename(path)
                pattern = '\d+\.\d+\.\d+\.\d+'
                match = re.search(pattern, filename)
                if match and match.group():
                    # Found a Chrome version.
                    return match.group(0)

    return None


def get_chrome_version() -> str:
    version = None
    install_path = None

    try:
        if platform == "linux" or platform == "linux2":
            # linux
            install_path = "chromium"
        elif platform == "darwin":
            # OS X
            install_path = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
        elif platform == "win32":
            # Windows...
            try:
                # Try registry key.
                stream = os.popen(
                    'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"')
                output = stream.read()
                version = extract_version_registry(output)
            except Exception as ex:
                # Try folder path.
                version = extract_version_folder()
    except Exception as ex:
        print(ex)
    if install_path:
        match = re.search(r"\d+.\d+.\d+.\d+",os.popen(f"{install_path} --version").read())
       
        if not match:
            print("match",match)
            raise ChromeNotFoundError()
        else:
            version = match[0]
        
    return version
