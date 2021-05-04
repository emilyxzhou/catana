#!/usr/bin/env python3.8

from ee250_final.discord_pub import Commands, Topics
import grovepi
import grove_rgb_lcd
import logging
import os
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import subprocess
import sys
import time

logging.basicConfig(level=logging.INFO)

sys.path.append('/home/pi/Documents/Software/Python/')
sys.path.append('/home/pi/DocumentsSoftware/Python/grove_rgb_lcd')

dirname = os.path.dirname(__file__)
SNAPSHOT_SCRIPT_PATH = os.path.join(dirname, 'snapshot.sh')


class RpiController:

    def __init__(self, username, host, port, keepalive):
        self._username = username
        self._host = host
        self._port = port

        self._uson = 4  # D4
        self._uson_threshold = 10
        self._led = 3  # D3
        grovepi.pinMode(self._led, "OUTPUT")
        grove_rgb_lcd.setRGB(0, 255, 0)

        self._username = username
        self._feeder_topic = Topics.FEEDER.format(username=username)
        self._led_topic = Topics.LED.format(username=username)
        print(self._feeder_topic)
        print(self._led_topic)

        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.connect(host=self._host, port=self._port, keepalive=keepalive)
        self._client.loop_start()

    def run(self):
        dist = grovepi.ultrasonicRead(self._uson)
        line1 = "{dist} cm away   ".format(dist=str(dist))
        if dist <= self._uson_threshold:
            self._take_photo()
        grove_rgb_lcd.setText_norefresh("{}\n               ".format(line1))
        grove_rgb_lcd.setRGB(0, 255, 0)

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("MQTT publisher client connected to server with code {}".format(str(rc)))
        self._client.subscribe(self._feeder_topic)
        self._client.subscribe(self._led_topic)
        self._client.message_callback_add(self._feeder_topic, self._feeder_callback)
        self._client.message_callback_add(self._led_topic, self._led_callback)

    def _feeder_callback(self, client, userdata, msg):
        msg = msg.payload.decode("utf-8")
        logging.info("Message received by feeder subscriber: {}".format(msg))
        self._servo_call()

    def _servo_call(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)

        servo = GPIO.PWM(17, 50)
        servo.start(0)

        time.sleep(2)

        duty = 7
        while duty <= 10:
            servo.ChangeDutyCycle(duty)
            time.sleep(0.25)
            duty = duty + 1

        time.sleep(2)

        servo.stop()
        GPIO.cleanup()

    def _led_callback(self, client, userdata, msg):
        msg = msg.payload.decode("utf-8")
        logging.info("Message received by led subscriber: {}".format(msg))
        if msg == Commands.LED_ON:
            grovepi.digitalWrite(self._led, 1)
        elif msg == Commands.LED_OFF:
            grovepi.digitalWrite(self._led, 0)
        else:
            logging.info("LED callback for RPi node received invalid command: {}".format(msg))

    def _take_photo(self):
        subprocess.call(["./{}".format(SNAPSHOT_SCRIPT_PATH), self._username, self._host, self._port])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("This script requires the following arguments: discord username, MQTT host, and port.")
    username = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
    rpi_controller = RpiController(
        username=username,
        host=host,
        port=port,
        keepalive=60
    )

    while True:
        rpi_controller.run()
        time.sleep(1)
