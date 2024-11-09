import os
from pathlib import Path

saved_lines = []
BASE_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent
with open("install.iss", "r") as f:
    lines = f.readlines()
    for line in lines:
        if "#define AccountsManagerBaseDir" in line:
            line = f'#define AccountsManagerBaseDir "{BASE_PATH}"\n'
        saved_lines.append(line)
with open("install.iss", "w") as f:
    f.writelines(saved_lines)
