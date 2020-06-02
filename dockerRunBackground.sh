#!/bin/bash

sudo docker rm -f "local-storage-controller"

sudo docker run -dit --restart='always' \
--name 'local-storage-controller' \
-p 11301:11301
local-storage-controller