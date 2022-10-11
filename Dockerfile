# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app
RUN apk add build-base
RUN apk add libffi-dev
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

ENTRYPOINT FLASK_APP=myproject flask run --host=0.0.0.0