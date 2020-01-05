FROM python:stretch
RUN pip install -U pip && pip install yolov3 pillow matplotlib rq redis
RUN pip install flask flask-restful

WORKDIR /code

COPY ./model_data/ ./model_data
COPY ./yolov3.weights ./model_data/

RUN python ./model_data/convert.py ./model_data/yolov3.cfg ./model_data/yolov3.weights ./model_data/yolo_weights.h5

COPY ./src /code
