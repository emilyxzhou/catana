#!/bin/bash

FILE_NAME=$1
HOST=$2
PORT=$3
fswebcam --no-banner /home/pi/Documents/ee250-final/$FILE_NAME.jpg

python3 img_pub.py $FILE_NAME.jpg $HOST $PORT
rm $FILE_NAME.jpg
