FROM python:stretch
RUN pip install flask flask-restful redis rq gunicorn
WORKDIR /code
COPY ./src /code
