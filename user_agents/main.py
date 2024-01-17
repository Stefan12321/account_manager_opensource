import os

import user_agent

from user_agent import generate_user_agent
from accounts_manager_main.serializer import Config
BASE_DIR = os.environ["ACCOUNT_MANAGER_BASE_DIR"]
chrome_builds = Config(f"{BASE_DIR}/chrome_versions.json")
win_versions = Config(f"{BASE_DIR}/win_versions.json")

CHROME_BUILDS = chrome_builds.config_data["chrome_versions"]
WINDOWS_VER = win_versions.config_data["win_versions"]

def get_user_agent(os=None, navigator=None, platform=None,
                   device_type=None):
    """
    Generates HTTP User-Agent header

    :param os: limit list of os for generation
    :type os: string or list/tuple or None
    :param navigator: limit list of browser engines for generation
    :type navigator: string or list/tuple or None
    :param device_type: limit possible oses by device type
    :type device_type: list/tuple or None, possible values:
        "desktop", "smartphone", "tablet", "all"
    :return: User-Agent string
    :rtype: string
    :raises InvalidOption: if could not generate user-agent for
        any combination of allowed oses and navigators
    :raise InvalidOption: if any of passed options is invalid
    """
    user_agent.base.CHROME_BUILD = CHROME_BUILDS
    user_agent.base.OS_PLATFORM.update({'win': WINDOWS_VER})
    return generate_user_agent(os=os, navigator=navigator, platform=platform,
                               device_type=device_type)


if __name__ == '__main__':
    print(get_user_agent(os=("win"), navigator=("chrome"), device_type=("desktop")))
