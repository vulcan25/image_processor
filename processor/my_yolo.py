from image_detect import YOLO as stock_yolo
stock_yolo._defaults['model_path']= 'model_data/yolo_weights.h5'
stock_yolo._defaults['anchors_path']= 'model_data/yolo_anchors.txt'
stock_yolo._defaults['classes_path']='model_data/coco_classes.txt'
import cv2
import io
import numpy
import logging
logging.basicConfig(level=logging.INFO)
class custom_yolo(stock_yolo):
    def detect_img(self, input_stream):
        # imdecode: https://stackoverflow.com/a/54162776/2052575
        # imencode: https://stackoverflow.com/a/52865864/205257

        image = cv2.imdecode(numpy.fromstring(input_stream, numpy.uint8), 1)

        original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_image_color = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        r_image, ObjectsList = self.detect_image(original_image_color)
        is_success, output_stream  = cv2.imencode(".jpg", r_image)

        return is_success, output_stream
        #ObjectsList

yolo = custom_yolo()

import time

def process(intput_stream):
     
     start_time = time.time()
     is_success, output_stream = yolo.detect_img(input_stream)
     io_buf = io.BytesIO(output_stream)
#    return is_success, io_buf.read(), ObjectList
     print("--- %s seconds ---" % (time.time() - start_time))
     return is_success, io_buf.read()   

