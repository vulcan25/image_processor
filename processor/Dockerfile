FROM python:stretch
RUN pip install -U pip && pip install yolov3 pillow matplotlib rq redis
WORKDIR /code
RUN git clone https://github.com/pythonlessons/YOLOv3-object-detection-tutorial.git && wget https://pjreddie.com/media/files/yolov3.weights
COPY ./build.sh /code/build.sh
RUN sh /code/build.sh
WORKDIR /code/YOLOv3-object-detection-tutorial/YOLOv3-custom-training

COPY ./app.py ./
COPY ./index.html ./
COPY ./my_yolo.py ./
COPY ./index.html ./
COPY ./image_detect.py ./

RUN pip install flask flask-restful
