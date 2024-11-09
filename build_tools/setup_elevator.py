import shutil

from cx_Freeze import setup, Executable


def build():
    try:
        shutil.rmtree('build/accounts_manager/elevator')
    except Exception as e:
        print(f"[ERROR] {e}")

    base = None
    elevator_executables = [
        Executable("app/common/updater/elevator.py",
                   target_name='elevator.exe',
                   base=base),
    ]
    excludes_elevator = ["aiohttp", "aiosignal", "async-generator", "async-timeout", "attrs", "beautifulsoup4",
                         "cachetools", "cffi", "charset-normalizer", "click", "colorama", "colour", "cx-Freeze",
                         "cx-Logging", "dnspython", "frozenlist", "google-api-core", "google-api-python-client",
                         "google-auth", "google-auth-httplib2", "google-auth-oauthlib", "googleapis-common-protos",
                         "google",
                         "google_services", "googleapiclien", "accounts_manager_main", "undetected-chromedriver",
                         "user_agents",
                         "guidata", "guiqwt", "h11", "importlib-metadata", "Jinja2", "krakenex", "lief",
                         "MarkupSafe", "multidict", "numpy", "oauth2client", "oauthlib", "openai", "outcome",
                         "packaging",
                         "pandas", "peewee", "Pillow", "pip-check-reqs", "protobuf", "pyasn1", "pyasn1-modules",
                         "pycparser", "pycryptodomex", "pykrakenapi", "pyparsing", "pyqt-tools", "PyQt5", "PyQt5-Qt5",
                         "PyQt5-sip", "PyQt5-stubs", "pyqt6-plugins", "pyqt6-tools", "PySocks", "python-dateutil",
                         "python-dotenv", "PythonQwt", "pytz", "pywin32", "PyYAML", "qt-material", "qt6-applications",
                         "qt6-tools", "QtPy", "rarfile", "requests-oauthlib", "rsa", "scipy", "six",
                         "sniffio", "sortedcontainers", "soupsieve", "trio", "trio-websocket",
                         "uritemplate", "user-agent", "websockets", "wsproto", "yarl", "zipp"]
    elevator_options = {
        'build_exe': {
            'build_exe': 'build/accounts_manager/elevator',
            'excludes': excludes_elevator
        }
    }

    setup(
        name="elevator",
        options=elevator_options,
        version=1.0,
        description='',
        executables=elevator_executables
    )
