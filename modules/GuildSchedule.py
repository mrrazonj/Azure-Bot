import discord
from discord.ext import commands, tasks
from discord.utils import get

import time

import sqlite3

import BotConf


class GuildSchedule(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.has_reset_daily = False

    @commands.Cog.listener()
    async def on_ready(self):
        self.reset_daily.start()

    @tasks.loop(seconds=1)
    async def reset_daily(self):
        log_channel = self.client.get_channel(BotConf.log_channel_id)

        reset_hour = str(BotConf.reset_hour)
        if len(reset_hour) == 1:
            reset_hour = f"0{reset_hour}"
        reset_minute = str(BotConf.reset_minute)
        if len(reset_minute) == 1:
            reset_minute = f"0{reset_minute}"

        if BotConf.reset_minute == 0:
            flag_reset_minute = "59"
            if BotConf.reset_hour == 0:
                flag_reset_hour = "23"
            else:
                flag_reset_hour = str(BotConf.reset_hour - 1)
                if len(flag_reset_hour) == 1:
                    flag_reset_hour = f"0{flag_reset_hour}"
        else:
            flag_reset_minute = str(BotConf.reset_minute - 1)
            if len(flag_reset_minute) == 1:
                flag_reset_minute = f"0{flag_reset_minute}"
            flag_reset_hour = str(BotConf.reset_hour)
            if len(flag_reset_hour) == 1:
                flag_reset_hour = f"0{flag_reset_hour}"

        flag_reset_time = f"{flag_reset_hour}:{flag_reset_minute}"
        reset_time = f"{reset_hour}:{reset_minute}"

        t = time.localtime()
        current_time = time.strftime("%H:%M", t)
        current_day = time.strftime("%A", t)

        if current_time == flag_reset_time:
            print("Flags Reset")
            self.has_reset_daily = False

        if current_time == reset_time and not self.has_reset_daily:
            guild = self.client.get_guild(BotConf.guild_id)
            to_attend = get(guild.roles, name="To-Attend")
            for role in guild.roles:
                if role.name == "Member":
                    for member in role.members:
                        await member.add_roles(to_attend)

            if current_day == BotConf.reset_day:
                connection = sqlite3.connect("modules/data/guild.db")
                c = connection.cursor()
                c.execute('''UPDATE attendance
                             SET Monday = 0,
                                 Tuesday = 0,
                                 Wednesday = 0,
                                 Thursday = 0,
                                 Friday = 0,
                                 Saturday = 0,
                                 Sunday = 0,
                                 Total = 0
                          ''')
                connection.commit()
                connection.close()

            await log_channel.send("Attendance module reset!")
            self.has_reset_daily = True

    @reset_daily.before_loop
    async def before_reset_daily(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(GuildSchedule(client))
