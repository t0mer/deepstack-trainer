import os, json, requests, uvicorn, uuid
import shutil, aiofiles, sqlite3, base64
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
        response = requests.post("{}/v1/vision/face/register".format(deepstack_host_address), files={"image1":user_image},data={"userid":person,"api_key":deepstack_api_key}).json()
    if response.get('success') == False:
        raise Exception(response.get('error'))
    return response

def detection(photo_path):
    image_data = open(photo_path,"rb").read()
    objects = ""
    response = ""
    if not deepstack_api_key:
        response = requests.post("{}/v1/vision/detection".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence}).json()
    else:
        response = requests.post("{}/v1/vision/detection".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence,"api_key":deepstack_api_key}).json()
    logger.debug(min_confidence)
    if response.get('success') == False:
        raise Exception(response.get('error'))
    for object in response["predictions"]:
        objects = objects + object["label"] + " ,"
    return objects

def detect_scene(photo_path):
    image_data = open(photo_path,"rb").read()
    if not deepstack_api_key:
        response = requests.post("{}/v1/vision/scene".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence}).json()
    else:
        response = requests.post("{}/v1/vision/scene".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence,"api_key":deepstack_api_key}).json()
    if response.get('success') == False:
        raise Exception(response.get('error'))
    return str(response['label'])

def getFaces(photo_path):
    users = ""
    image_data = open(photo_path,"rb").read()
    if not deepstack_api_key:
        response = requests.post("{}/v1/vision/face/recognize".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence}).json()
    else:
        response = requests.post("{}/v1/vision/face/recognize".format(deepstack_host_address),files={"image":image_data}, data={"min_confidence":min_confidence,"api_key":deepstack_api_key}).json()
    if response.get('success') == False:
        raise Exception(response.get('error'))
    for user in response["predictions"]:
        users = users + user["userid"] + " ,"
    return users



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
        data_tuple = (name, os.path.basename(photo))
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
    cur.execute('CREATE TABLE IF NOT EXISTS images (name TEXT NOT NULL, photo TEXT NOT NULL, dt datetime default current_timestamp);')
    con.commit()
    con.close()
    


def delete_image(image_file):
    if os.path.exists(image_file):
        os.remove(image_file)
        return True
    else:
        return False


logger.info("Configuring app")
app = FastAPI(title="Deepstack Trainer", description="Train your deepstack AI server", version="1.0.0")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/img", StaticFiles(directory="dist/img"), name="img")
app.mount("/uploads", StaticFiles(directory="photos/uploads"), name="img")
templates = Jinja2Templates(directory="templates/")

@app.post('/teach')
def teach(person: str = Form(...) ,teach_file: UploadFile = File(...)):
    logger.info("Start learning new face for: " + person)
    try:
        InitDB()
        if teach_file and allowed_file(teach_file.filename):
            image_file = os.path.join('./photos/uploads', generate_file_name(teach_file.filename))
            SaveImage(teach_file.file, image_file)
            logger.info("Sending the image to deepstack server")
            response = teachme(person,image_file)
            success = str(response['success']).lower()
            if 'message' in str(response):
                message = response['message']
                logger.info("Saving image to Database")
                if success=='true':
                    insertBLOB(person,image_file)
                else:
                    delete_image(image_file)
                return JSONResponse(content = '{"message":"'+message+'","success":"'+success+'"}')
            if 'error' in str(response):
                delete_image(image_file)
                error = response['error']
                logger.error("Unable to learn " + error)
                return JSONResponse(content = '{"error":"'+error+'","success":"'+success+'"}')
            return response
    except Exception as e:
        delete_image(image_file)
        error = "Aw Snap! something went wrong - " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


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
        delete_image(image_file)
 
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
        delete_image(image_file)

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
        delete_image(image_file)


@app.post('/api/rename')
async def rename(request: Request ):
    data = await request.json()
    try:
        InitDB()
        conn = sqlite3.connect(db_path)
        sql = ''' UPDATE images
              SET name = ? 
               WHERE photo = ?'''
        cur = conn.cursor()
        cur.execute(sql, (data['text'], data['img']))
        conn.commit()
        return JSONResponse(content = '{"message":"Person renamed","success":"true"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


@app.post('/api/delete')
async def delete(request: Request):
    logger.info("Deleting")
    data = await request.json()
    try:
        image_file = os.path.join('./photos/uploads', data['img'])
        logger.debug('########## ' + image_file)
        if delete_image(image_file) == True:
            InitDB()
            conn = sqlite3.connect(db_path)
            sql = 'DELETE from images WHERE photo = "' + data['img'] + '"'
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            return JSONResponse(content = '{"message":"Image Deleted","success":"true"}')
        else:
            return JSONResponse(content = '{"error":"Unable to delete image","success":"false"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


@app.get("/")
def home(request: Request):
    InitDB()
    logger.info("loading default page")
    return templates.TemplateResponse('index.html', context={'request': request})

@app.get("/api/images")
def get_images(request: Request):
    try:
        with sqlite3.connect(db_path, check_same_thread=False) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM images order by dt')
            return templates.TemplateResponse('gallery.html', context={'request': request, 'images' : cur.fetchall()} )
    except Exception as e:
        logger.error("Error fetch images, " + str(e))
        return None


# Start Application
if __name__ == '__main__':
    InitDB()
    uvicorn.run(app, host="0.0.0.0", port=8080)
