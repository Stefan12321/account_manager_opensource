FROM python:3.11.7-windowsservercore AS base
WORKDIR /app
COPY . /app
RUN python -m venv venv
RUN .\venv\Scripts\activate
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "custom_setup.py", "build"]
