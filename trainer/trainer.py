import os, json, requests, uvicorn, uuid
import shutil, aiofiles, sqlite3
from os import environ, path
from loguru import logger
from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import UJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse


# from aiofiles import open
db_path='./db/images.db'
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
    logger.info("Validating file type")
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in "jpg,png,gif,bmp,jpeg"

def SaveImage(file, path):
    logger.info("Saving the image to the file system")
    try:
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        logger.info("File saved")
    except Exception as e:
        logger.error("Unable to save file " + str(e))
        raise Exception(str(e))

def convertToBinaryData(filename):
    logger.info("Converting To Binary Data: " + filename)
    # Convert digital data to binary format
    try:
        with open(filename, 'rb') as file:
            blobData = file.read()
            logger.info("Data loaded successfully")
            return blobData
    except Exception as e:
        logger.error("Unable to blob " + str(e))
        raise Exception(str(e))

def generate_file_name(file):
    try:
        logger.info("Renaming image name in order to avoid overwriting")
        file_name_without_ext=os.path.basename(file.rsplit('.', 1)[0])
        new_file_name = file.replace(file_name_without_ext, file_name_without_ext + "_" + str(uuid.uuid4()))
        return new_file_name
    except Exception as e:
        logger.error("Unable to rename " + str(e))
        return file

def insertBLOB(name, photo):
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        logger.info("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO images
                                  (name, photo) VALUES (?, ?)"""

        empPhoto = convertToBinaryData(photo)
        data_tuple = (name, empPhoto)
        cur.execute(sqlite_insert_blob_query, data_tuple)
        con.commit()
        logger.info("Image and file inserted successfully as a BLOB into a table")
        con.close()

    except Exception as error:
        logger.error("Failed to insert blob data into sqlite table " +  str(error))
    finally:
        if con:
            con.close()
            logger.info("the sqlite connection is closed")

def InitDB():
    if os.path.exists(db_path):
        return
    logger.info("Initializing Database")
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS images (name TEXT NOT NULL, photo BLOB NOT NULL);')
    con.commit()
    con.close()
    



logger.info("Configuring app")
app = FastAPI(title="Deepstack Trainer", description="Train your deepstack AI server", version="1.0.0")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/img", StaticFiles(directory="dist/img"), name="css")
templates = Jinja2Templates(directory="templates/")

@app.post('/teach')
def teach(person: str = Form(...) ,teach_file: UploadFile = File(...)):
    logger.info("Start learning new face for: " + person)
    try:
        InitDB()
        if teach_file and allowed_file(teach_file.filename):
            image_file = os.path.join('./photos', generate_file_name(teach_file.filename))
            SaveImage(teach_file.file, image_file)
            logger.info("Sending the image to deepstack server")
            response = teachme(person,image_file)
            success = str(response['success']).lower()
            if 'message' in str(response):
                message = response['message']
                logger.info("Saving image to Database")
                insertBLOB(person,image_file)
                return JSONResponse(content = '{"message":"'+message+'","success":"'+success+'"}')
            if 'error' in str(response):
                error = response['error']
                logger.error("Unable to learn " + error)
                return JSONResponse(content = '{"error":"'+error+'","success":"'+success+'"}')
            return response
    except Exception as e:
        error = "Aw Snap! something went wrong"
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')
    finally:
        if os.path.exists(image_file):
            os.remove(image_file)

@app.post('/who')
def who(who_file: UploadFile = File(...)):
    logger.info("Starting face detection")
    try:
        InitDB()
        if who_file and allowed_file(who_file.filename):
            filename = who_file.filename
            image_file = os.path.join('./photos', filename)
            SaveImage(who_file.file, image_file)
            logger.info("sending image to Deepstack server")
            response = getFaces(image_file)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The person in the picture is ' + str(response) + '","success":"true"}')
    except Exception as e:
        logger.error("Face Detection error " + str(e) )
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        logger.info("Deleting file to save space")
        if os.path.exists(image_file):
            os.remove(image_file)
 
@app.post('/detect')
def detect(detect_file: UploadFile = File(...)):
    logger.info("Starting object detection")
    try:
        InitDB()
        if detect_file and allowed_file(detect_file.filename):
            filename = detect_file.filename
            image_file = os.path.join('./photos', filename)
            logger.info("sending image to Deepstack server")
            SaveImage(detect_file.file, image_file)
            response = detection(image_file)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The objects in the picture are ' + str(response) + '","success":"true"}')
    except Exception as e:
        logger.error("Object Detection error " + str(e))
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        logger.info("Deleting file to save space")
        if os.path.exists(image_file):
            os.remove(image_file)

@app.post('/scene')
def scene(scene_file: UploadFile = File(...)):
    logger.info("Starting scene detection")
    try:
        InitDB()
        if scene_file and allowed_file(scene_file.filename):
            filename = scene_file.filename
            image_file = os.path.join('./photos', filename)
            logger.info("sending image to Deepstack server")
            SaveImage(scene_file.file, image_file)
            response = detect_scene(image_file)
            if response == '"" ,':
                response='unknown'
            return JSONResponse(content = '{"message":"The objects in the picture are ' + str(response) + '","success":"true"}')
    except Exception as e:
        logger.error("Object Detection error " + str(e))
        return JSONResponse(content = '{"error":"'+ str(e)  +'","success":"false"}')
    finally:
        logger.info("Deleting file to save space")
        if os.path.exists(image_file):
            os.remove(image_file)

@app.get("/")
def home(request: Request):
    InitDB()
    logger.info("loading default page")
    return templates.TemplateResponse('index.html', context={'request': request})



# Start Application
if __name__ == '__main__':
    InitDB()
    uvicorn.run(app, host="0.0.0.0", port=8080)
