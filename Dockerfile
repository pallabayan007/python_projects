# pull official base image
FROM python:3.8.5

# set work directory
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . .

# make virtual environment
RUN python -m venv venv
RUN . venv/bin/activate

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "neuralnetworkwebapp.wsgi", "-b", "0.0.0.0:8000", "--timeout", "50000"]
