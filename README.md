# Description
This is small app for managing GoogleChrome browser instances.
# Build
### Build in docker


Switch docker to use Windows Containers

`& $Env:ProgramFiles\Docker\Docker\DockerCli.exe -SwitchDaemon`

Build with docker compose

`docker-compose up`

Built application will be in folder build
### Build manually
Create and activate virtual environment
```
python -m venv venv
./venv/Scripts/activate
```
Install requirements
```
pip install --no-cache-dir -r requirements.txt
```
Build application

`python ./custom_setup.py build`

Or You can use it without build

`python main.py`

## Features

- Creating multiple browser instance
- Connecting precompiled extensions
- Display all browser-stored passwords
- Setup on browser load pages 
- Randomizing browser window size
- Faked useragent
- Faked browser geolocation
- Export/Import profiles
- Python console for every browser


## Future Features

### Platforms support
- [x] Windows support
- [ ] Linux support

### Other
- [ ] Auto updates (on testing stage)
- [ ] Visual scripting for browser automation (at the concept stage)


