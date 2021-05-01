# DeepStack Trainer
[DeepStack](https://deepstack.cc/) is an AI server that empowers every developer in the world to easily build state-of-the-art AI systems both on premise and in the cloud. The promises of Artificial Intelligence are huge but becoming a machine learning engineer is hard. DeepStack is device and language agnostic. You can run it on Windows, Mac OS, Linux, Raspberry PI and use it with any programming language.

DeepStack’s source code is available on GitHub via [https://github.com/johnolafenwa/DeepStack](https://github.com/johnolafenwa/DeepStack/)

[DeepStack Trainer](https://github.com/t0mer/deepstack-trainer) is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) powerd web application that helps us train and test Deepstack AI easelly as possible.

## Features
- Face Registring.
- Test face recognition.
- Test scene recognition.
- Test object detection.

## Components used in Deepstack Trainer
- [Flask](https://flask.palletsprojects.com/en/1.1.x/) - For running web server
- [materializecss](https://materializecss.com/) - For web forms
- [sweetalert2](https://sweetalert2.github.io/) - For alerts and messages

# Installation
In order to use Deepstack Trainer we need to install Deepstack.
We can do that by running the following command:
```docker run -e VISION-FACE=True -v localstorage:/datastore -p 80:5000 deepquestai/deepstack```

Basic Parameters:
* -e VISION-FACE=True This enables the face recognition APIs.
* -v localstorage:/datastore This specifies the local volume where deepstack will store all data.
* -p 80:5000 This makes deepstack accessible via port 80 of the machine.


