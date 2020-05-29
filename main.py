import discord
from discord.ext import commands, tasks
import asyncio
import os

import BotConf


client = commands.Bot(command_prefix=BotConf.bot_prefix, description=BotConf.bot_description)


@client.event
async def on_ready():
    print(f"{client.user} is now online!")
    if client.get_guild(BotConf.id_guild):
        guild = client.get_guild(BotConf.id_guild)
        channel = client.get_channel(BotConf.id_channel_log)
        await channel.send(f"{client.user.name} is now online!")
        role_gm = guild.get_role(BotConf.dict_id_role_general["GuildMaster"])
        await channel.send(role_gm.mention)
        msg = await channel.fetch_message(channel.last_message_id)
        await asyncio.sleep(3)
        await msg.delete()


for modules in os.listdir("./modules"):
    if modules.endswith(".py"):
        client.load_extension(f"modules.{modules[:-3]}")

client.run(BotConf.bot_token)
