import subprocess
from pathlib import Path
from build_tools import inno_installer
from .setup_main import build as build_main
from .setup_cleaner import build as build_cleaner
from .setup_elevator import build as build_elevator
import sys

PATH_TO_INNOSETUP = Path("D:\Inno Setup 6\ISCC.exe")
PATH_TO_ISS = Path("./install.iss")

def build():
    if len(sys.argv) < 2 or sys.argv[1] not in ["build", "build_main", "build_cleaner", "build_elevator", "build_msi"]:
        print(
            "Usage:\npython setup.py build #Build all\npython setup.py build_main #Build build_main\npython setup.py build_cleaner #Build build_cleaner\npython setup.py build_elevator #Build build_elevator")
        return
    cmd = sys.argv[1]
    sys.argv[1] = "build"
    if cmd == "build" or cmd == "build_main":
        build_main()
    if cmd == "build" or cmd == "build_cleaner":
        build_cleaner()
    if cmd == "build" or cmd == "build_elevator":
        build_elevator()
    if cmd in ["build", "build_msi"] and sys.platform == "win32":
        subprocess.run([PATH_TO_INNOSETUP, PATH_TO_ISS.absolute()])


if __name__ == '__main__':
    build()
