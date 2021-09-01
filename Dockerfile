#set the base image
FROM python:3.6.14-alpine

#set the working directory in the container
WORKDIR /usr/src/app

#copy all the files (zoom.py and requirements.txt)
COPY manager.py .
COPY requirements.txt .

#install dependencies
RUN pip install -r requirements.txt

CMD ["python", "./manager.py"]