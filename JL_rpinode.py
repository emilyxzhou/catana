import sys
import time
import paho.mqtt.client as mqtt
import subprocess

sys.path.append('/home/pi/Documents/Software/Python/')
# This append is to support importing the LCD library.
sys.path.append('/home/pi/DocumentsSoftware/Python/grove_rgb_lcd')

import grovepi
from grove_rgb_lcd import * 
from servo import *

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    #subscribe to feeder topic
    client.subscribe("rpi/feeder")
    client.message_callback_add("rpi/feeder", custom_callback_feeder)

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))
    
def custom_callback_feeder(client, userdata, message):
    print("custom_callback: " + message.topic + " " + "\"" + 
        str(message.payload, "utf-8") + "\"")
    if(str(message.payload,"utf-8") == "feed"):
        servocall()


if __name__ == '__main__':
    
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()
    
    setRGB(0,255,0)
    USON = 4    # D4
    threshold = 10
    while True:
        #So we do not poll the sensors too quickly 
        time.sleep(1)
        dist = grovepi.ultrasonicRead(USON)
        l1 = str(dist) + " cm away   "
        if dist <= threshold:
            setText(l1+"\n"+"Taking photo...")
            setRGB(255,0,0)
            
            #print("calling bash script now")
            rc = subprocess.call("./snapshot.sh")

        else:
            setText_norefresh(l1+"\n"+"               ")
            setRGB(0,255,0)

    

