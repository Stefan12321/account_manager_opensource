FROM python:3.11.7-windowsservercore AS base
WORKDIR /app
COPY . /app
RUN python -m venv venv
RUN .\venv\Scripts\activate
RUN pip install --no-cache-dir -r requirements.txt
ENV ACCOUNT_MANAGER_PATH_TO_CONFIG=/app/app/config
CMD ["python", "-m" ,"build_tools", "build"]
