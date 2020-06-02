FROM python:3.8-alpine

RUN apk add g++
RUN apk add alpine-sdk
RUN apk add build-base
RUN apk add linux-headers
RUN apk add autoconf
RUN apk add musl-dev
RUN apk add python3-dev
RUN apk add automake
RUN apk add bash
RUN apk add nano

RUN python3 -m pip install redis
RUN python3 -m pip install sanic
RUN python3 -m pip install viziocontroller
RUN python3 -m pip install wakeonlan

COPY python_app /home/python_app
WORKDIR "/home/python_app"

#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python3" , "server.py" ]