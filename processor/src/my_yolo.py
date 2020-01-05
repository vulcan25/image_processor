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

        return is_success, output_stream, ObjectsList

yolo = custom_yolo()

import time
from collections import Counter

def get_object_string(l):
    # https://stackoverflow.com/a/44418966/2052575
    new_vals = Counter(l).most_common()
    new_vals = new_vals[::-1] #this sorts the list in ascending order
    for a, b in new_vals:
        yield '%s:%s, ' % (str(a), str(b))

def process(input_stream):
     
     start_time = time.time()
     is_success, output_stream, ObjectsList  = yolo.detect_img(input_stream)
     io_buf = io.BytesIO(output_stream)
     print("--- %s seconds ---" % (time.time() - start_time))
     
     objects = [d[6] for d in ObjectsList]

     info = {'success': is_success,
             'objects': objects,
             'object_string': ' '.join(get_object_string(objects)),
             }

     return info, io_buf.read()   

