import asyncio
import datetime
import discord
from discord.ext import commands, tasks
import json
import logging
import paho.mqtt.client as mqtt
from user import User

logging.basicConfig(level=logging.INFO)


class Commands:
    LED_OFF = "LED off"
    LED_ON = "LED on"
    START = "start"


class Topics:
    FEEDER = "{username}/feeder"
    IMAGE = "rpi/image"
    LED = "{username}/LED"


class DiscordPub(commands.Cog):

    def __init__(self, bot: commands.Bot, channel_id, host, port, keepalive):
        self._bot = bot
        self._channel_id = channel_id
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.connect(host=host, port=port, keepalive=keepalive)
        self._mqtt_client.loop_start()
        self._users = []
        self._image_data = {}

        self.check_for_images_to_send.start()

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("MQTT publisher client connected to server with code {}".format(str(rc)))
        self._mqtt_client.subscribe(Topics.IMAGE)
        self._mqtt_client.message_callback_add(Topics.IMAGE, self._save_image_data)

    def _save_image_data(self, client, userdata, msg):
        msg = msg.payload.decode("utf-8")
        msg = json.loads(msg)
        username = msg["username"]
        image_data = msg["image_data"]
        self._image_data[username] = image_data

    @tasks.loop(seconds=10.0)
    async def check_for_images_to_send(self):
        for username in self._image_data:
            image = self._image_data[username]
            self._image_data.pop(username)
            channel = await self._bot.fetch_channel(self._channel_id)
            await channel.send("{name}: {image}".format(name=username, image=image))

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
        name="LED_off", help="Send message to RPI to turn off LED"
    )
    async def turn_led_off(self, message: discord.Message):
        name = message.author.name
        self._create_user_if_not_exists(name)
        user = self._find_user(name)
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
        self._find_user(name).add_feeding_times(times_array)

    def _create_user_if_not_exists(self, name):
        if not self._find_user(name):
            self.add_user(name)
