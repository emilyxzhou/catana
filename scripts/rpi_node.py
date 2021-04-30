#!/usr/bin/env python3.8

import logging
import paho.mqtt.client as mqtt
import time

logging.basicConfig(level=logging.INFO)

FEEDER_TOPIC = "rpi/feeder"
LED_TOPIC = "rpi/led"
