An image proccessing service, for using [YOLOv3-object-detection-tutorial](https://github.com/pythonlessons/YOLOv3-object-detection-tutorial) and inspired by a [question on stackoverflow](https://stackoverflow.com/questions/59482473/python-keras-api-server-to-process-image-on-trained-custom-model#comment105328769_59482473).  This is mainly to utilise the `image_detect.py` script, and make this backend functionality available through Flask.

**Proceed with caution.  This is a prototype / development playground.**

This stack presents two ways of running:

1. As a Flask app in the `processor` container which contains all the heavy processing dependencies.
2. As a Flask app in its own lighter `flask` container which passes the processing to the `processor` container via `rq`

Initially I implemented mode (2), then I realised performance was very fast with mode (1):  `~1.6` seconds per image conversion on a CPU. However in mode (1) when a request comes in a UWSGI worker which handles the request will block.  This is a consideration when scaling, as if you want to handle bulk ingress of images, a CPU core is needed per request, and unavailable while the processing happens.  With mode (2) many images can be uploaded quickly, then processing capacity scaled for demand.  With the latter mode the endpoint returns a url for the image.  Until processing is complete it currently just returns a string 'processing'. 

# Usage:


Clone repo.

    git clone https://github.com/vulcan25/image_processor
    cd image_processor

Grab the weights.  You may have your own.  I used the file from  `pjreddie.com/media/files/yolov3.weights`.  Put this file in the subdirectory `processor/`.  When the `processor` container builds, it copies this in as it then runs the `convert.py` script on the models.  With this approach the converted models then become part of the docker image.

Build the containers:

    docker-compose -f docker-compose.yml -f with-rq-compose.yml build

## mode (1)...

Launch with mode (1) which will expose a Flask app in the `processor` service on `http://localhost:5001`.  This means the Flask app exists on the same container as the image processing dependencies.

    docker-compose up

When you connect to the web-interface it uses dropzone.js on the frontend for the "drop-here" interface, the proccessed image is then displayed on the page.  Be aware that dropzone is loaded from CDNJS. I have written some simple javascript to manipulate the page.

You can also upload a file with: 

    curl -H 'ContentType: multipart/form-data' -i -X POST -F 'file=@image.jpg' "http://localhost:5001/upload" 

This returns the processed image.

## mode (2)...

(Make sure you've killed the `docker-compose up` command, or are deploying to a separate environment.)

Launch with mode (2) which will aditionally expose a Flask app in the `flask` service on `http://localhost:5000/`:

	docker-compose -f docker-compose.yml -f with-rq-compose.yml up

Notice that in `with-rq-compose.yml` I replace the command for the processing container with `rqworker -u redis://redis` instead of `flask run -h 0.0.0.0` which makes it boot as a worker.  These rq workers connect to a queue on the `redis` service.  Within the `flask` service I can then use rq to enqueue a function: its possbible to have the command run on a separate worker, by simply defining the as function:

    def process(data): pass
 
 then passing that function to rq.enqeue:
 
    job = img_enqueue(input_data)

This is handled by the following code on the `flask` service:
```
from my_yolo import process

def img_enqueue(img):
    j = q.enqueue(process, img)
    return j 
```
Even thuogh this `process` function only returns `pass`, over in the `processor` service `from my_yolo import process` imports the actual code to be executed by the worker, allowing the `flask` service to be free of keras dependencies, etc.

The web-interface on port `5000` is much the same, however uploading in image with `curl` as before (except to the service on port `5000`):

    curl -H 'ContentType: multipart/form-data' -i -X POST -F 'file=@image.jpg' "http://localhost:5000/upload" 

Gives back a url string for the image page:

	{"url":"/view/cd4ba6a0-8149-4688-87ed-8ec78c5ac554"}

Viewing this URL will return the string "processing" unless the job is done, at which point it will return the image.

# Bug List

- `processor` container image too large at `~2.43GB`
- `flask/src/app.py` uses container fs storage (`/tmp`): probably should find a way around this.  Maybe S3 via boto3, or similar.
- `processor/src/app.py` doesn't support any storage; everything is handled in memory.  Code could be added to make this store in some manner.
- `app.py` and `index.html` are similar in the processing and flask service respectivly.  Find a better way to make these more modular.

# Timing snippet

The following can be run in the `processor` container:

You can get into a running container with: `docker exec -it image_processor_processor_1 /bin/bash`

```
import time

start = time.time()
from my_yolo import process
print("IMPORTED: --- %s seconds ---" % (time.time() - start))

def speed_test():
    with open('image.jpg', 'rb') as f:
        start = time.time()
        
        is_success, data = process(f.read())

        print("DONE: --- %s seconds ---" % (time.time() - start))

        with open('image_processed.jpg','wb') as f:
            f.write(data)

```
