#!/usr/bin/env python3.8

import logging
import paho.mqtt.client as mqtt
import time

from discord_bot import DiscordCog

logging.basicConfig(level=logging.INFO)

FEEDER_TOPIC = "rpi/feeder"
LED_TOPIC = "rpi/led"


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to server with result code "+str(rc))
    client.subscribe(FEEDER_TOPIC)
    client.subscribe(LED_TOPIC)