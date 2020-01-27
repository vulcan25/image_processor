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

#
# Redis functionality for an object counter

from redis import StrictRedis
r = StrictRedis(host='redis', charset="utf-8", decode_responses=True)

def incr_item(object, counter_id = 'default'):
    """ maitains a count of objects in redis.

    object: something like 'hydrant'
    counter_id: in future you could create a separate counter
                based on, for example, a string provided from the frontend

    """
    hash_name = 'obj_cnt:%s' % counter_id
    r.hincrby(hash_name, object, 1)


#
# Some utility functions to help prepare the info dict

import time
from collections import Counter

def get_object_string(l):
    # https://stackoverflow.com/a/44418966/2052575
    new_vals = Counter(l).most_common()
    new_vals = new_vals[::-1] #this sorts the list in ascending order
    for a, b in new_vals:
        yield '%s:%s, ' % (str(a), str(b))

def score_objects(l):
    # Translate the object list from image_detect.py
    # TODO: decied if image_detect should actually return this dict instead of 
    # a list.
    # [top, left, bottom, right, mid_v, mid_h, label, scores]
    return {'object': l[6], 'score':  l[7],
            'top': l[0].item(),
            'left': l[1].item(),
            'bottom': l[2].item(),
            'right': l[3].item(),
            'mid_v': l[4].item(),
            'mid_h': l[5].item(),
            }

def time_since(start):
    return round(time.time() - start, 3)
#
# Main processing function
from os import environ

def process(input_stream):
     
     timings = ''
     start_time = time.time()

     is_success, output_stream, ObjectsList  = yolo.detect_img(input_stream)
     io_buf = io.BytesIO(output_stream)
     
     timings += 'detect_img: %ss, ' % (time_since(start_time))
     processing_finished = time.time()

     objects = [d[6] for d in ObjectsList]
     scored_objects = [score_objects(d) for d in ObjectsList]
     
     # Update redis count
     count_threshold = environ.get('COUNT_THRESHOLD', 0) # default's to 0 if env var not set

     for item in scored_objects:
         if float(item['score']) > count_threshold:
             incr_item(item['object'])

     info = {'success': is_success,
             'objects': objects,
             'object_string': ' '.join(get_object_string(objects)),
             'scored_objects': scored_objects,
             }

     timings += 'meta: %ss, ' % (time_since(processing_finished))

     info['timings'] = timings

     return info, io_buf.read()   

