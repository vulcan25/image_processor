from flask import jsonify, Flask, render_template, send_file, url_for
from flask_restful import Resource, Api, reqparse
import werkzeug, os
from werkzeug.utils import secure_filename

from redis import StrictRedis
r = StrictRedis(host='redis', charset="utf-8", decode_responses=True, db=2)

app = Flask(__name__, template_folder='.')
api = Api(app)

# Configurationg
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = ['jpg']

# Flask restful file upload
parser = reqparse.RequestParser()
parser.add_argument('file',
    type=werkzeug.datastructures.FileStorage,
    location='files')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from my_yolo import process

from uuid import uuid4

class FileUpload(Resource):
    def post(self):
        data = parser.parse_args()
        if data['file'] == None:
            return "no file", 400
        file = data['file']
                        
        if file and allowed_file(file.filename):
            # process the upload immediately
            input_data = file.read()
            complete, data = process(input_data)
            
            # Create a filename randomly:
            filename = uuid4().__str__()
            with open(os.path.join(UPLOAD_FOLDER, filename),'wb') as f:
                f.write(data)

            # Save filenames in redis set.  we can then access
            # this for validation in the other route.

            r.sadd('files', filename)

            return jsonify({'id': url_for('view', filename=filename)})
        else:
            return 'not allowed', 403

api.add_resource(FileUpload, '/upload')

from flask import stream_with_context, Response

@app.route('/view/<string:filename>')
def view(filename):
    if not r.sismember('files', filename):
        abort(404)
    else:
        return send_file(os.path.join(UPLOAD_FOLDER, filename), mimetype='image/jpeg')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
