import discord
from discord.ext import commands, tasks
import asyncio

import random
import time

import BotConf


class DragonRajaUtilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["iof"])
    async def iceorfire(self, ctx):
        list_choice = ["Ice", "Ice", "Ice", "Fire", "Fire", "Fire"]
        await ctx.channel.send(f"You must choose **{random.choice(list_choice)}**.")
        await ctx.message.delete()

    @tasks.loop(minutes=1.0)
    async def timed_event_ping(self):
        guild = self.client.get_guild(BotConf.id_guild)
        channel_reminder = guild.get_channel(BotConf.dict_id_channels["Reminder"])

        role_salon_brain = guild.get_role(BotConf.dict_id_role_events["Salon"])
        role_event_pve = guild.get_role(BotConf.dict_id_role_events["ClubPVE"])
        role_gossip = guild.get_role(BotConf.dict_id_role_events["Gossip"])
        role_event_pvp = guild.get_role(BotConf.dict_id_role_events["ClubPVP"])
        role_liberty_day = guild.get_role(BotConf.dict_id_role_events["DayOfLiberty"])
        role_irritated_blood = guild.get_role(BotConf.dict_id_role_events["IrritatedBlood"])
        role_wboss_borgman = guild.get_role(BotConf.dict_id_role_events["WBBorgman"])

        time_liberty_day_irrblood = "12:00"
        time_salon_brain = "13:00"
        time_event_pve = "13:30"
        time_irritated_blood = "13"
        time_gossip = "21:00"
        time_event_pvp = "22:00"
        list_time_borgman_spawn = ["12:30",
                                   "16:30",
                                   "20:30",
                                   "00:30"]

        t = time.localtime()
        current_time = time.strftime("%H:%M", t)

        if current_time == time_liberty_day_irrblood:
            await channel_reminder.send(role_liberty_day.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(1)
            await channel_reminder.send(role_irritated_blood.mention)
            msg2 = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
            await msg2.delete()
        if current_time == time_salon_brain:
            await channel_reminder.send(role_salon_brain.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_event_pve:
            await channel_reminder.send(role_event_pve.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_irritated_blood:
            await channel_reminder.send(role_irritated_blood.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_gossip:
            await channel_reminder.send(role_gossip.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_event_pvp:
            await channel_reminder.send(role_event_pvp.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time in list_time_borgman_spawn:
            await channel_reminder.send(role_wboss_borgman.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()

    @timed_event_ping.before_loop
    async def before_ping(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        self.timed_event_ping.start()


def setup(client):
    client.add_cog(DragonRajaUtilities(client))
