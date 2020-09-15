# pull official base image
FROM python:3.8.5

# set work directory
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class=eventlet", "main:app", "--timeout", "5000"]

# Incase using https for web server level
# CMD ["gunicorn", "--certfile", "certificates/server.crt","--keyfile","certificates/server.key", "--bind", "0.0.0.0:5000", "--worker-class=eventlet", "main:app", "--timeout", "5000"]
