from redis import Redis
from rq import Queue
from rq.job import Job
r = Redis(host='redis')
q = Queue(connection=r)
from my_yolo import process

def img_enqueue(img):
    j = q.enqueue(process, img)
    return j

def fetch(id):
    j = Job.fetch(str(id), connection=r)
    return j
