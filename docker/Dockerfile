# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8

RUN apt-get update -y
RUN apt-get install git -y
RUN apt-get install sudo -y

RUN apt-get install postgresql -y

ENV TZ=Europe/Berlin
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install -r requirements.txt

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# File wsgi.py was not found in subfolder: 'django_webpage_form'. Please enter the Python path to wsgi file.
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pythonPath.to.wsgi"]
CMD [ "bash" ]
