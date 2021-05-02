import paho.mqtt.client as mqtt
import time
#test servo
from pynput import keyboard

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    #subscribe to the webcam topic here
    client.subscribe("rpi/webcam")

def on_message(client, userdata, msg):
    #print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))
    f = open('output.jpg',"wb")
    f.write(msg.payload)
    print("Image received")
    f.close()

#test servo
def on_press(key):
    try: 
        k = key.char # single-char keys
    except: 
        k = key.name # other keys

    if k == 'a':
        print("a")
        #send servo on
        client.publish("rpi/feeder", "feed")

if __name__ == '__main__':

    #test servo
    lis = keyboard.Listener(on_press=on_press)
    lis.start()

    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        #print("delete this line")
        time.sleep(1)

