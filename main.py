import discord
from discord.ext import commands, tasks
import os

import BotConf


client = commands.Bot(command_prefix=BotConf.bot_prefix, description=BotConf.bot_description)


@client.event
async def on_ready():
    print(f"{client.user} is now online!")
    if client.get_guild(713379747517694004):
        channel = client.get_channel(713649107499090011)
        await channel.send(f"{client.user.name} is now online!")


for modules in os.listdir("./modules"):
    if modules.endswith(".py"):
        client.load_extension(f"modules.{modules[:-3]}")

client.run(BotConf.bot_token)
