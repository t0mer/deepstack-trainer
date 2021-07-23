*Please :star: this repo if you find it useful*

<p align="left"><br>
<a href="https://www.paypal.com/paypalme/techblogil?locale.x=he_IL" target="_blank"><img src="http://khrolenok.ru/support_paypal.png" alt="PayPal" width="250" height="48"></a>
</p>



# DeepStack Trainer
[DeepStack](https://deepstack.cc/) is an AI server that empowers every developer in the world to easily build state-of-the-art AI systems both on premise and in the cloud. The promises of Artificial Intelligence are huge but becoming a machine learning engineer is hard. DeepStack is device and language agnostic. You can run it on Windows, Mac OS, Linux, Raspberry PI and use it with any programming language.

DeepStack’s source code is available on GitHub via [https://github.com/johnolafenwa/DeepStack](https://github.com/johnolafenwa/DeepStack/)

[DeepStack Trainer](https://github.com/t0mer/deepstack-trainer) is a [FastAPI](https://fastapi.tiangolo.co) powerd web application that helps us train and test Deepstack AI easelly as possible.

## Features
- Face Registring.
- Test face recognition.
- Test scene recognition.
- Test object detection.
- Gallery page, display all uploaded images (For traning only).

## Components used in Deepstack Trainer
- [FastAPI](https://fastapi.tiangolo.com/) - For running web server
- [materializecss](https://materializecss.com/) - For web forms
- [sweetalert2](https://sweetalert2.github.io/) - For alerts and messages

# Installation
#### Deepstack Installation
In order to use Deepstack Trainer we need to install Deepstack.
We can do that by running the following command:

```docker run -e VISION-FACE=True -v localstorage:/datastore -p 80:5000 deepquestai/deepstack```

Basic Parameters:
* -e VISION-FACE=True This enables the face recognition APIs.
* -v localstorage:/datastore This specifies the local volume where deepstack will store all data.
* -p 80:5000 This makes deepstack accessible via port 80 of the machine.

We can also install Deepstack using docker-compose:
```
version: "3.7"
services:
  deepstack:
    image: deepquestai/deepstack:latest
    restart: unless-stopped
    container_name: deepstack
    ports:
      - "80:5000"
    environment:
      - TZ=Asia/Jerusalem
      - VISION-FACE=True
      - VISION-DETECTION=True
      - VISION-SCENE=True
    volumes:
      - ./deepstack:/datastore
```

#### Deepstack Trainer Installation
Deepstack Trainer installation is very easy using docker-compose:
```
version: "3.7"
services:
  deepstack_trainer:
    image: techblog/deepstack-trainer
    container_name: deepstack_trainer
    privileged: true
    restart: always
    environment:
      - DEEPSTACK_HOST_ADDRESS=
      - DEEPSTACK_API_KEY=
      - MIN_CONFIDANCE=
    ports:
      - "8080:8080" 
    volumes:
      - ./deepstack-trainer/db:/opt/trainer/db #Database storing the uploaded photos data (Filename, Person name, Date).
      - ./deepstack-trainer/uploads:/opt/trainer/photos/uploads #Phisical path for storing the images
      
```

Basic Parameters:
* DEEPSTACK_HOST_ADDRESS - Deepstack API Url (http://localhost:5000)
* DEEPSTACK_API_KEY - If your Deepstack API is token protected enter your token here or alse leave blank
* MIN_CONFIDANCE - Minimum Confidence level to identify object or face (Default is 0.70)


## Working with Deepstack Trainer
After the docker is up and running, open your browser and navigate to your Deepstack Trainer url. you will be able to see four tabs:
* Face Learning (Registring).
[![Face Registring](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/teach%20face.png?raw=true "Face Registring")](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/teach%20face.png?raw=true "Face Registring")

* Face Recognition
[![Face Recognition](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/face%20recognition.png?raw=true "Face Recognition")](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/face%20recognition.png?raw=true "Face Recognition")

* Object Detection
[![Object Detection](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/object%20detection.png?raw=true "Object Detection")](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/object%20detection.png?raw=true "Object Detection")

* Scene Detection
[![Scene Detection](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/scene%20detection.png?raw=true "Scene Detection")](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/scene%20detection.png?raw=true "Scene Detection")

* Photo Gallery
[![Scene Detection](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/gallery.png?raw=true "Scene Detection")](https://github.com/t0mer/deepstack-trainer/blob/main/screenshots/gallery.png?raw=true "Scene Detection")

# Integrations and Community
The DeepStack ecosystem includes a number of popular integrations and libraries built to expand the functionalities of the AI engine to serve IoT, industrial, monitoring and research applications. A number of them are listed below

* [HASS-DeepStack-Object](https://github.com/robmarkcole/HASS-Deepstack-object)
* [HASS-DeepStack-Face](https://github.com/robmarkcole/HASS-Deepstack-face)
* [HASS-DeepStack-Scene](https://github.com/robmarkcole/HASS-Deepstack-scene)
* [DeepStack with Blue Iris - YouTube video](https://www.youtube.com/watch?v=fwoonl5JKgo)
* [DeepStack with Blue Iris - Forum Discussion](https://ipcamtalk.com/threads/tool-tutorial-free-ai-person-detection-for-blue-iris.37330/)
* [DeepStack on Home Assistant](https://community.home-assistant.io/t/face-and-person-detection-with-deepstack-local-and-free/92041)
* [DeepStack-UI](https://github.com/robmarkcole/deepstack-ui)
* [DeepStack-Python Helper](https://github.com/robmarkcole/deepstack-python)
* [DeepStack-Analytics](https://github.com/robmarkcole/deepstack-analytics)
* [DeepStackAI Trigger](https://github.com/danecreekphotography/node-deepstackai-trigger)
