from setup_main import build as build_main
from setup_cleaner import build as build_cleaner
from setup_elevator import build as build_elevator
import sys


def build():
    if len(sys.argv) < 2 or sys.argv[1] not in ["build", "build_main", "build_cleaner", "build_elevator"]:
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


if __name__ == '__main__':
    build()
