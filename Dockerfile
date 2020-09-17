# pull official base image
FROM python:3.8.5

# set work directory
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# move models.py
RUN mv models.py /usr/local/lib/python3.8/site-packages/django/contrib/auth

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "python_webapp_django.wsgi", "-b", "0.0.0.0:8000", "--timeout", "50000"]
