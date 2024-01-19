# Use an official Python runtime as a parent image
FROM python:3.11.7-windowsservercore AS base

# Set the working directory to /app
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
# Install any needed packages specified in requirements.txt
RUN python -m venv venv
RUN .\venv\Scripts\activate
RUN pip install --no-cache-dir -r requirements.txt

# Run custom setup script
#RUN python custom_setup.py build
#RUN xcopy C:\app\build\accounts_manager C:\volume_app /E /I /H /K
CMD ["python", "custom_setup.py", "build"]

# docker build -t "container" --target=base --build-arg WORKDIR="C:\app" .
#docker create -it --mount type=bind,source="D:\Projects\accounts_manager_opensource\build",target="C:\app\build\accounts_manager" --name "application_container" "container"
#docker start "application_container"