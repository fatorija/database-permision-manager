#set the base image
FROM python:3.6.14-alpine

#set the working directory in the container
WORKDIR /usr/src/app

#copy all the files (zoom.py and requirements.txt)
COPY manager.py .
COPY requirements.txt .

#install dependencies
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

CMD ["python", "./manager.py"]