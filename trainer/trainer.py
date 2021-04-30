
from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify
from flask_restful import Resource, Api
import os, json
from os import environ
from os import path
from flask import flash
import requests
from loguru import logger


deepstack_host_address = os.getenv("DEEPSTACK_HOST_ADDRESS")
deepstack_api_key = os.getenv("DEEPSTACK_API_KEY")
min_confidence = os.getenv("MIN_CONFIDANCE")

if not min_confidence:
    min_confidence=0.70
else:
    min_confidence=float(min_confidence)

logger.info("#########################################")
logger.info("Deepstack Host Address set to: " + str(deepstack_host_address))
logger.info("Minimum Confidence value set to: " + str(min_confidence))
logger.info("Deepstack api key set to: " + str(deepstack_api_key))

logger.info("#########################################")


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./"
api = Api(app)


def teachme(person,image_file):
    user_image = open(image_file,"rb").read()
    response=""
    if not deepstack_api_key:
        response = requests.post("{}/v1/vision/face/register".format(deepstack_host_address), files={"image1":user_image},data={"userid":person}).json()
    else:
        response = requests.post("{}/v1/vision/face/register".format(deepstack_host_address), files={"image1":user_image},data={"userid":person,"admin_key":"{}}".format(deepstack_api_key)}).json()
    # os.remove(image_file)
    return response

def detection(photo_path):
    image_data = open(photo_path,"rb").read()
    response = requests.post("{}/v1/vision/detection".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":0.70}).json()
    objects = ""
    for object in response["predictions"]:
        objects = objects + object["label"] + " ,"
    return objects

def detect_scene(photo_path):
    image_data = open(photo_path,"rb").read()
    response = requests.post("{}/v1/vision/scene".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":0.70}).json()
    return str(response['label'])


def getFaces(photo_path):
    try:
        image_data = open(photo_path,"rb").read()
        response = requests.post("{}/v1/vision/face/recognize".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":0.70}).json()
        users = ""
        for user in response["predictions"]:
            users = users + user["userid"] + " ,"
        return users
    except Exception as e:
        return str(e)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "jpg,png,gif,bmp,jpeg"

@app.route('/teach', methods=['POST'])
def teach():
    if request.method == 'POST':
        # check if the post request has the file part
        person = str(request.form['teach-name'])
        if 'teach-file' not in request.files:
            return jsonify('{"error":"No file found in posted data","success":"false"}')
        file = request.files['teach-file']
        if file.filename == '':
            return jsonify('{"error":"File can not be empty","success":"false"}')
        if not allowed_file(file.filename):
            return jsonify('{"error":"File type not supported","success":"false"}')
        if not person:
            return jsonify('{"error":"Pleas enter person name","success":"false"}')


        if file and allowed_file(file.filename):
            filename = file.filename
            image_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_file)
            response = teachme(person,image_file)
            success = str(response['success']).lower()
            if os.path.exists(image_file):
                os.remove(image_file)
            if 'message' in str(response):
                message = response['message']
                return jsonify('{"message":"'+message+'","success":"'+success+'"}')
            if 'error' in str(response):
                error = response['error']
                return jsonify('{"error":"'+error+'","success":"'+success+'"}')
            return response



@app.route('/who', methods=['POST'])
def who():
    image_file = ""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'who-file' not in request.files:
            return jsonify('{"error":"No file found in posted data","success":"false"}')
        file = request.files['who-file']
        if file.filename == '':
            return jsonify('{"error":"File can not be empty","success":"false"}')
        if not allowed_file(file.filename):
            return jsonify('{"error":"File type not supported","success":"false"}')
        try:
            if file and allowed_file(file.filename):
                filename = file.filename
                image_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_file)
                response = getFaces(image_file)
                return jsonify('{"message":"The person in the picture is ' + response + '","success":"true"}')
        except Exception as e:
            return jsonify('{"error":"'+ str(e)  +'","success":"false"}')
        finally:
            if os.path.exists(image_file):
                os.remove(image_file)


@app.route('/detect', methods=['POST'])
def detect():
    image_file = ""
    if request.method == 'POST':
        if 'detect-file' not in request.files:
            return jsonify('{"error":"No file found in posted data","success":"false"}')
        file = request.files['detect-file']
        if file.filename == '':
            return jsonify('{"error":"File can not be empty","success":"false"}')
        if not allowed_file(file.filename):
            return jsonify('{"error":"File type not supported","success":"false"}')
        try:
            if file and allowed_file(file.filename):
                filename = file.filename
                image_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_file)
                response = detection(image_file)
                return jsonify('{"message":"The objects in the picture are ' + response + '","success":"true"}')
        except Exception as e:
            return jsonify('{"error":"'+ str(e)  +'","success":"false"}')
        finally:
            if os.path.exists(image_file):
                os.remove(image_file)

@app.route('/scene', methods=['POST'])
def scene():
    image_file = ""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'scene-file' not in request.files:
            return jsonify('{"error":"No file found in posted data","success":"false"}')
        file = request.files['scene-file']
        if file.filename == '':
            return jsonify('{"error":"File can not be empty","success":"false"}')
        if not allowed_file(file.filename):
            return jsonify('{"error":"File type not supported","success":"false"}')
        try:
            if file and allowed_file(file.filename):
                filename = file.filename
                image_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_file)
                response = detect_scene(image_file)
                return jsonify('{"message":"The objects in the picture are ' + response + '","success":"true"}')
        except Exception as e:
            return jsonify('{"error":"'+ str(e)  +'","success":"false"}')
        finally:
            if os.path.exists(image_file):
                os.remove(image_file)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')



# region Serving Static Files

# Serve Javascript
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('dist/js', path)

# Serve CSS
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('dist/css', path)

# Serve Images
@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('dist/img', path)

# Serve Fonts
@app.route('/webfonts/<path:path>')
def send_webfonts(path):
    return send_from_directory('dist/webfonts', path)

# endregion


# Start Application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)