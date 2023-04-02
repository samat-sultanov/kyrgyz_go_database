# pull official base image
FROM ubuntu:22.04

# Set DEBIAN_FRONTEND to noninteractive to avoid prompts
ENV DEBIAN_FRONTEND noninteractive

# set work directory
WORKDIR /kyrgyz_go_database

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y build-essential python3 python3-dev python3-pip gcc musl-dev postgresql postgresql-contrib vim

# install dependencies
RUN pip install --upgrade pip
COPY /requirements.txt .
RUN pip install -r requirements.txt && pip install uwsgi

# copy entrypoint.sh
COPY /entrypoint.sh .
RUN sed -i 's/\r$//g' /kyrgyz_go_database/entrypoint.sh
RUN chmod +x /kyrgyz_go_database/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/kyrgyz_go_database/entrypoint.sh"]