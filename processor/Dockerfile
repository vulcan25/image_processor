FROM python:stretch
RUN pip install -U pip && pip install yolov3 pillow matplotlib rq redis
WORKDIR /code
COPY ./src /code
COPY ./yolov3.weights ./model_data/
RUN sh /code/build.sh


RUN pip install flask flask-restful
