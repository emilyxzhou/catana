import logging
import paho.mqtt.client as mqtt
import sys
import time

logging.basicConfig(level=logging.INFO)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to server (i.e., broker) with result code " + str(rc))


def on_message(client, userdata, msg):
    logging.info("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit("This script requires the following arguments: image filepath, MQTT host, and port.")
    host = sys.argv[2]
    port = sys.argv[3]
    keepalive = 60
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host=host, port=port, keepalive=60)
    client.loop_start()

    f = open(sys.argv[1], "rb")
    fileContent = f.read()
    byteArr = bytearray(fileContent)

    client.publish("rpi/webcam", byteArr)
    time.sleep(5)