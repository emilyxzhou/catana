#!/usr/bin/env python3.8

import asyncio
import datetime
import discord
from discord.ext import commands
import logging
import os
import paho.mqtt.client as mqtt
import re
import schedule
from user import User

logging.basicConfig(level=logging.INFO)

# TOKEN = os.environ["DISCORD_TOKEN"]
# CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
TOKEN = "ODM3NDU2OTM4MzA0Mjc0NTMy.YIs0jQ.ytoqi_pd8XJu7BqHn9kFDfp-H7c"
CHANNEL_ID = 837457410276327487


class MyBot(commands.Bot):

    async def on_ready(self):
        channel = await self.fetch_channel(CHANNEL_ID)
        await channel.send(f"ayo what's up")


class DiscordFeederClient:

    class Commands:
        LED_OFF = "LED off"
        LED_ON = "LED on"
        START = "start"

    def __init__(
            self,
            host,
            port,
            keepalive
    ):
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.connect(host=host, port=port, keepalive=keepalive)

    def _on_connect(self):
        pass

    def start_feeder(self, topic):
        self._mqtt_client.publish(topic, DiscordFeederClient.Commands.START)
        logging.info("Publishing to start feeder")

    def turn_led_off(self, topic):
        self._mqtt_client.publish(topic, DiscordFeederClient.Commands.LED_OFF)
        logging.info("Publishing to turn off LED")

    def turn_led_on(self, topic):
        self._mqtt_client.publish(topic, DiscordFeederClient.Commands.LED_ON)
        logging.info("Publishing to turn on LED")


class DiscordCog(commands.Cog):

    def __init__(
            self,
            bot: commands.Bot,
            feeder_client
    ):
        self._bot = bot
        self._feeder_client = feeder_client

        self._users = []

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("Welcome {0.mention}.".format(member.name))
            self.add_user(member.name)

    @commands.command(
        name="set", help="Set times to trigger the automatic feeder"
    )
    async def ask_to_set_times(self, message: discord.Message):
        name = message.author.name
        if not self._find_user(name):
            self.add_user(name)

        await message.channel.send("Enter times (hh:mm:ss) separated by a space.")

        def is_valid_time(message):
            times_array = message.content.split()
            for value in times_array:
                try:
                    datetime.datetime.strptime(value, "%H:%M:%S")
                except ValueError:
                    return False
            return True
        try:
            times: discord.Message = await self._bot.wait_for(
                "message", check=is_valid_time, timeout=40.0
            )
        except asyncio.TimeoutError:
            return await message.channel.send(
                "Sorry, you took too long. Please enter the command again."
            )

        self._save_times(times, name)
        await message.channel.send("Great, thank you.")

    @commands.command(
        name="LED_off", help="Send message to RPI to turn off LED"
    )
    async def turn_led_off(self, message: discord.Message):
        name = message.author.name
        user = self._find_user(name)
        led_topic = user.led_topic
        self._feeder_client.turn_led_off(led_topic)

    @commands.command(
        name="LED_on", help="Send message to RPI to turn on LED"
    )
    async def turn_led_on(self, message: discord.Message):
        name = message.author.name
        user = self._find_user(name)
        led_topic = user.led_topic
        self._feeder_client.turn_led_on(led_topic)

    def add_user(self, name: str):
        self._users.append(User(name))
        logging.info("New user added: {}".format(name))

    def _find_user(self, name: str):
        for user in self._users:
            if user.name == name:
                return user
        return None

    def _save_times(self, message: discord.Message, name: str):
        times_array = message.content.split()
        self._find_user(name).add_feeding_times(times_array)


if __name__ == "__main__":
    feeder_client = DiscordFeederClient(host="localhost", port=1883, keepalive=60)

    b = MyBot(command_prefix=commands.when_mentioned)
    b.add_cog(
        DiscordCog(b, feeder_client)
    )
    b.run(TOKEN)
