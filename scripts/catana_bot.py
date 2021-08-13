#!/usr/bin/env python3.8

from discord.ext import commands
from ee250_final.discord_pub import DiscordPub
import logging
import random
import sys

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


class CatanaBot(commands.Bot):

    async def on_ready(self):
        channel = await self.fetch_channel(CHANNEL_ID)
        greetings = [
            "ayo what's up",
            "hello there!",
            "hi :)",
            "i'm,,,awake"
        ]
        await channel.send(random.choice(greetings))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("This script requires the following arguments: MQTT host and port.")
    host = sys.argv[1]
    port = int(sys.argv[2])
    bot = CatanaBot(command_prefix=commands.when_mentioned)
    discord_pub = DiscordPub(
        bot=bot,
        channel_id=CHANNEL_ID,
        host=host,
        port=port,
        keepalive=60
    )
    bot.add_cog(discord_pub)
    bot.run(TOKEN)
