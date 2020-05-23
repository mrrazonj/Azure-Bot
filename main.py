import discord
from discord.ext import commands

import schedule
import time
import threading

import config

client = commands.Bot(command_prefix=config.prefix, description=config.description)

schedule_stop = threading.Event()


def dailies_timer():
    while not schedule_stop.is_set():
        schedule.run_pending()
        time.sleep(1)


schedule_thread = threading.Thread(target=dailies_timer)


async def dailies_reset():
    if client.get_guild(713379747517694004):
        channel = client.get_channel(713649107499090011)
        await channel.send("Dailies reset!")


@client.event
async def on_ready():
    print(f"Bot({client.user}) online!")

    if client.get_guild(713379747517694004):
        channel = client.get_channel(713649107499090011)
        await channel.send(f"Bot ({client.user}) is now online!")


@client.command()
async def ping(ctx):
    await ctx.send(f"Latency is {round(client.latency, 5)}")


@client.command()
async def clean(ctx, amount=25):
    await ctx.channel.purge(limit=amount)


schedule.every().day.at("15:56").do(client.loop.call_soon_threadsafe, dailies_reset())


client.run(config.token)
