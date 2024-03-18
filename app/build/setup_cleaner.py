import shutil

from cx_Freeze import setup, Executable
def build():
    try:
        shutil.rmtree('../../build/accounts_manager/cleaner')
    except Exception as e:
        print(f"[ERROR] {e}")

    base = None

    cleaner_executables = [
        Executable("../common/updater/cleaner.py",
                   target_name='cleaner.exe',
                   base=base),
    ]
    excludes_cleaner = ["aiohttp", "aiosignal", "async-generator", "async-timeout", "attrs", "beautifulsoup4",
                        "cachetools", "cffi", "charset-normalizer", "click", "colorama", "colour", "cx-Freeze",
                        "cx-Logging", "dnspython", "frozenlist", "google-api-core", "google-api-python-client",
                        "google-auth", "google-auth-httplib2", "google-auth-oauthlib", "googleapis-common-protos", "google",
                        "google_services", "googleapiclien", "accounts_manager_main", "undetected-chromedriver",
                        "user_agents",
                        "guidata", "guiqwt", "h11", "importlib-metadata", "Jinja2", "krakenex", "lief",
                        "MarkupSafe", "multidict", "numpy", "oauth2client", "oauthlib", "openai", "outcome", "packaging",
                        "pandas", "peewee", "Pillow", "pip-check-reqs", "protobuf", "pyasn1", "pyasn1-modules",
                        "pycparser", "pycryptodomex", "pykrakenapi", "pyparsing", "pyqt-tools", "PyQt5", "PyQt5-Qt5",
                        "PyQt5-sip", "PyQt5-stubs", "pyqt6-plugins", "pyqt6-tools", "PySocks", "python-dateutil",
                        "python-dotenv", "PythonQwt", "pytz", "pywin32", "PyYAML", "qt-material", "qt6-applications",
                        "qt6-tools", "QtPy", "rarfile", "requests-oauthlib", "rsa", "scipy", "selenium", "six",
                        "sniffio", "sortedcontainers", "soupsieve", "trio", "trio-websocket",
                        "uritemplate", "user-agent", "websockets", "wsproto", "yarl", "zipp"]
    cleaner_options = {
        'build_exe': {
            'build_exe': './build/accounts_manager/cleaner',
            'excludes': excludes_cleaner

        }
    }

    setup(
        name="cleaner",
        options=cleaner_options,
        version=1.0,
        executables=cleaner_executables

    )
