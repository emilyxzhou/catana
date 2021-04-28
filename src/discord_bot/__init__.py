#!/usr/bin/env python3.8

import asyncio
import discord
from discord.ext import commands
import os
import typing


TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


class MyBot(commands.Bot):

    async def on_ready(self):
        channel = await self.fetch_channel(CHANNEL_ID)
        await channel.send(f"I'm ON and ready!")


class DiscordCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("Welcome {0.mention}.".format(member))


if __name__ == "__main__":

    b = MyBot(command_prefix=commands.when_mentioned)
    b.add_cog(DiscordCog(b))
    b.run(TOKEN)
