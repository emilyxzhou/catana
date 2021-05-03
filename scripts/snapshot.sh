#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")
fswebcam --no-banner /home/pi/Documents/ee250-final/$DATE.jpg

python3 img_pub.py $DATE.jpg
