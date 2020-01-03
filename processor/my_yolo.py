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
    def detect_img(self, img_stream):
        # image = cv2.imread(image, cv2.IMREAD_COLOR)
        # https://stackoverflow.com/a/54162776/2052575
        
        image = cv2.imdecode(numpy.fromstring(img_stream, numpy.uint8), 1)

        original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_image_color = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        r_image, ObjectsList = self.detect_image(original_image_color)
        return r_image, ObjectsList
yolo = custom_yolo()
#yolo = custom_yolo()
import time
def process(image_stream):
     
     start_time = time.time()
     r_image, ObjectList = yolo.detect_img(image_stream)
     is_success, output_stream  = cv2.imencode(".jpg", r_image)
     io_buf = io.BytesIO(output_stream)
#    return is_success, io_buf.read(), ObjectList
     print("--- %s seconds ---" % (time.time() - start_time))
     return is_success, io_buf.read()   

