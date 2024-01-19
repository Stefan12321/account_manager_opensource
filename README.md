# Description

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
