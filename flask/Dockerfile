FROM python:stretch
RUN pip install flask flask-restful redis rq gunicorn
WORKDIR /code
COPY ./app.py /code
COPY ./qu.py /code
COPY ./index.html /code
COPY ./my_yolo.py /code

