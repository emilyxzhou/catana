import asyncio
import datetime
import discord
from discord.ext import commands, tasks
from ee250_final.user import User
import io
import json
import logging
import os
import paho.mqtt.client as mqtt
from PIL import Image
import schedule
import threading
import time

logging.basicConfig(level=logging.INFO)


class Commands:
    LED_OFF = "LED off"
    LED_ON = "LED on"
    FEED = "feed"


class Topics:
    FEEDER = "{username}/feeder"
    IMAGE = "rpi/image"
    LED = "{username}/LED"


class DiscordPub(commands.Cog):

    def __init__(self, bot: commands.Bot, channel_id, host, port, keepalive):
        self._feeder_scheduler = schedule.Scheduler()
        self._sched_stop = threading.Event()
        self._scheduler_thread = threading.Thread(target=self._feeder_timer)
        self._scheduler_thread.start()

        self._bot = bot
        self._channel_id = channel_id
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.connect(host=host, port=port, keepalive=keepalive)
        self._mqtt_client.loop_start()
        self._users = []
        self._image_data = {}

        self.check_for_images_to_send.start()

    def _feeder_timer(self):
        while not self._sched_stop.is_set():
            self._feeder_scheduler.run_pending()
            time.sleep(10)

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("MQTT publisher client connected to server with code {}".format(str(rc)))
        self._mqtt_client.subscribe(Topics.IMAGE)
        self._mqtt_client.message_callback_add(Topics.IMAGE, self._save_image_data)

    def _save_image_data(self, client, userdata, msg):
        msg = msg.payload.decode("utf-8")
        msg = json.loads(msg)
        username = msg["username"]
        image_data = msg["image_data"]
        user: User = self._find_user(username)
        if not User:
            raise ValueError("No user with the username \'{}\'".format(username))
        image_file_name = os.path.join(user.image_file_name)
        self._save_image_to_file(image_data, image_file_name)
        self._image_data[username] = image_file_name

    def _save_image_to_file(self, bytes_array, file_path):
        image = Image.open(io.BytesIO(bytes_array))
        image.save(file_path)

    @tasks.loop(seconds=10.0)
    async def check_for_images_to_send(self):
        for username in self._image_data:
            image_file_path = self._image_data.pop(username)
            if image_file_path is not None:
                channel = await self._bot.fetch_channel(self._channel_id)
                await channel.send("{name}: image taken from webcam".format(name=username))
                await channel.send(file=discord.File(image_file_path))
                os.remove(image_file_path)
                self._image_data[username] = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('hello, {0.mention}!'.format(member))

    @commands.command(
        name="set", help="set times to trigger the automatic feeder"
    )
    async def ask_to_set_times(self, message: discord.Message):
        name = message.author.name
        self._create_user_if_not_exists(name)

        await message.channel.send("enter times (hh:mm:ss) separated by a space.")

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
                "sorry, you took too long. please enter the command again."
            )

        self._save_times(times, name)
        await message.channel.send("cool, thanks!")

    @commands.command(
        name="feed", help="send 'feed' command to rpi feeder"
    )
    async def send_feed_command(self, message: discord.Message):
        name = message.author.name
        self._create_user_if_not_exists(name)
        user: User = self._find_user(name)
        self._mqtt_client.publish(user.feeder_topic, Commands.FEED)

    @commands.command(
        name="LED_off", help="Send message to RPI to turn off LED"
    )
    async def turn_led_off(self, message: discord.Message):
        name = message.author.name
        self._create_user_if_not_exists(name)
        user = self._find_user(name)
        logging.info(user)
        logging.info(user.led_topic)
        if user is not None:
            self._mqtt_client.publish(user.led_topic, Commands.LED_OFF)

    @commands.command(
        name="LED_on", help="Send message to RPI to turn on LED"
    )
    async def turn_led_on(self, message: discord.Message):
        name = message.author.name
        self._create_user_if_not_exists(name)
        user = self._find_user(name)
        self._mqtt_client.publish(user.led_topic, Commands.LED_ON)

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
        user: User = self._find_user(name)
        user.add_feeding_times(times_array)
        for time in times_array:
            self._feeder_scheduler.every().day.at(time).do(
                self._mqtt_client.publish,
                user.feeder_topic,
                Commands.FEED
            )

    def _create_user_if_not_exists(self, name):
        if not self._find_user(name):
            self.add_user(name)
