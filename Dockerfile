
FROM ubuntu:18.04

LABEL maintainer="tomer.klein@gmail.com"
ENV DEEPSTACK_HOST_ADDRESS=""
ENV DEEPSTACK_API_KEY=""
ENV MIN_CONFIDANCE=0.70
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

RUN apt update -yqq

RUN apt -yqq install python3-pip
    
RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir && \
     pip3 install fastapi  --no-cache-dir && \
     pip3 install uvicorn  --no-cache-dir && \
     pip3 install jinja2  --no-cache-dir && \
     pip3 install aiofiles  --no-cache-dir && \
     pip3 install loguru --no-cache-dir && \
     pip3 install cryptography --no-cache-dir && \
     pip3 install python-multipart --no-cache-dir && \
     pip3 install requests --no-cache-dir
     
<<<<<<< HEAD
RUN mkdir -p /opt/trainer/photos/uploads
 
COPY trainer /opt/trainer
 
EXPOSE 8080
 
WORKDIR /opt/trainer/
 
ENTRYPOINT ["/usr/bin/python3", "trainer.py"]
=======
RUN mkdir -p /app/trainer/photos/uploads
 
COPY trainer /app/trainer
 
EXPOSE 8080
 
CMD ["uvicorn", "app.trainer:app", "--host", "0.0.0.0", "--port", "8080"]
#ENTRYPOINT ["/usr/local/bin/uvicorn", "trainer:app --port 8080 --host 0.0.0.0  --workers 1"]
>>>>>>> a08e8ec9994472bd449f4e2904a53b07beb4e982
