import discord
from discord.ext import commands, tasks

import schedule

import sqlite3

import botconf

client = commands.Bot(command_prefix=botconf.prefix, description=botconf.description)


@client.event
async def on_ready():
    print(f"{client.user} is now online!")
    if client.get_guild(713379747517694004):
        channel = client.get_channel(713649107499090011)
        await channel.send(f"{client.user} is now online!")


@client.command()
async def ping(ctx):
    await ctx.send(f"```css\n"
                   f"Latency to bot is {round(client.latency, 5)}ms.\n"
                   f"```")


@client.command()
async def clean(ctx, amount=25):
    await ctx.channel.purge(limit=amount)

client.run(botconf.token)
