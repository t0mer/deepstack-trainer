import os, json
from os import environ
from os import path
import requests
from loguru import logger
import uvicorn
from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import UJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import shutil, aiofiles

# from aiofiles import open

deepstack_host_address = os.getenv("DEEPSTACK_HOST_ADDRESS")
deepstack_api_key = os.getenv("DEEPSTACK_API_KEY")
min_confidence = os.getenv("MIN_CONFIDANCE")

if not min_confidence:
    min_confidence=0.70
else:
    min_confidence=float(min_confidence)

def teachme(person,image_file):
    user_image = open(image_file,"rb").read()
    response=""
    if not deepstack_api_key:
        response = requests.post("{}/v1/vision/face/register".format(deepstack_host_address), files={"image1":user_image},data={"userid":person}).json()
    else:
        response = requests.post("{}/v1/vision/face/register".format(deepstack_host_address), files={"image1":user_image},data={"userid":person,"admin_key":"{}}".format(deepstack_api_key)}).json()
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


def SaveImage(file, path):
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)



# app = FastAPI(docs_url="/swagger", openapi_tags=tags_metadata)
app = FastAPI(title="Deepstack Trainer", description="Train your deepstack AI server", version="1.0.0")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/img", StaticFiles(directory="dist/img"), name="css")
# app.mount("/plugins", StaticFiles(directory="plugins"), name="plugins")
templates = Jinja2Templates(directory="templates/")



@app.post('/teach')
def teach(person: str = Form(...) ,teach_file: UploadFile = File(...)):
    try:
        if teach_file and allowed_file(teach_file.filename):
            image_file = os.path.join('./photos', teach_file.filename)
            SaveImage(teach_file.file, image_file)
            response = teachme(person,image_file)
            success = str(response['success']).lower()
            if os.path.exists(image_file) and success.lower() == 'false':
                os.remove(image_file)
            if 'message' in str(response):
                message = response['message']
                return JSONResponse(content = '{"message":"'+message+'","success":"'+success+'"}')
            if 'error' in str(response):
                error = response['error']
                return JSONResponse(content = '{"error":"'+error+'","success":"'+success+'"}')
            return response
    except Exception as e:
        error = "Aw Snap! something went wrong"
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')



@app.post('/who')
def who(who_file: UploadFile = File(...)):
    try:
        if who_file and allowed_file(who_file.filename):
            filename = who_file.filename
            image_file = os.path.join('./photos', filename)
            SaveImage(who_file.file, image_file)
            response = getFaces(image_file)
            logger.info(response)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The person in the picture is ' + str(response) + '","success":"true"}')
    except Exception as e:
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        if os.path.exists(image_file):
            os.remove(image_file)

 
@app.post('/detect')
def detect(detect_file: UploadFile = File(...)):
    try:
        if detect_file and allowed_file(detect_file.filename):
            filename = detect_file.filename
            image_file = os.path.join('./photos', filename)
            SaveImage(detect_file.file, image_file)
            response = detection(image_file)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The objects in the picture are ' + str(response) + '","success":"true"}')
    except Exception as e:
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        if os.path.exists(image_file):
            os.remove(image_file)


@app.post('/scene')
def scene(scene_file: UploadFile = File(...)):
    try:
        if scene_file and allowed_file(scene_file.filename):
            filename = scene_file.filename
            image_file = os.path.join('./photos', filename)
            SaveImage(scene_file.file, image_file)
            response = detect_scene(image_file)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The objects in the picture are ' + str(response) + '","success":"true"}')
    except Exception as e:
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        if os.path.exists(image_file):
            os.remove(image_file)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})



# Start Application
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
