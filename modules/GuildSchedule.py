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

    @tasks.loop(seconds=20, reconnect=True)
    async def reset_daily(self):
        log_channel = self.client.get_channel(BotConf.id_channel_log)
        notice_channel = self.client.get_channel(BotConf.id_channel_notice)
        id_inactive_notice_embed = 715520609890729995

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
            guild = self.client.get_guild(BotConf.id_guild)
            to_attend = get(guild.roles, name="To-Attend")
            for role in guild.roles:
                if role.name == "Member":
                    for member in role.members:
                        await member.add_roles(to_attend)

            if current_day == BotConf.reset_day:
                connection = sqlite3.connect("modules/data/guild.db")
                c = connection.cursor()
                c.execute('''INSERT OR IGNORE INTO infractions(Username) SELECT Username FROM guild
                          ''')
                connection.commit()

                c.execute(f'''SELECT Username FROM guild WHERE Total < {BotConf.num_attendances_required}
                           ''')
                members = c.fetchall()
                list_member = []
                for member in members:
                    list_member.append(member[0])

                for member in list_member:
                    c.execute(f'''UPDATE infractions
                                  SET Penalties = Penalties + 1
                                  WHERE Username = '{member}'
                               ''')
                    connection.commit()

                c.execute('''UPDATE guild
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

                c.execute('''SELECT * FROM infractions WHERE Penalties > 0''')
                list_entry = c.fetchall()
                connection.close()

                embed = discord.Embed(title="Azure Club", description="Member inactivity notice", color=0xff0000)
                embed.set_author(name="Azure",
                                 url="https://github.com/mrrazonj/Azure-Bot",
                                 icon_url="https://i.imgur.com/alUOIgz.png")

                list_entry_formatted = []
                for entry in list_entry:
                    list_entry_formatted.append(f"{entry[0]} - {entry[1]} infractions")

                list_finalized = ("\n".join(str(i) for i in list_entry_formatted))
                string_empty = "None"

                embed.add_field(name=f"Members with infractions incurred:",
                                value=f"{string_empty if not list_entry_formatted else list_finalized}")
                embed.set_footer(text="This stub updates every Sunday at 23:10.")
                embed_inactive_notice = await log_channel.fetch_message(id_inactive_notice_embed)
                await embed_inactive_notice.edit(embed=embed)
            await log_channel.send("Attendance module reset!")
            self.has_reset_daily = True

    @reset_daily.before_loop
    async def before_reset_daily(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["chkrloop"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def checkresetloop(self, ctx):
        if self.reset_daily.get_task() is not None:
            print(self.reset_daily.get_task())
            await ctx.channel.send(f"Attendance reset module is currently running.")
        else:
            await ctx.channel.send(f"Attendance reset module is offline.")

    @commands.Cog.listener()
    async def on_ready(self):
        self.reset_daily.start()
        print("Attendance module online.")


def setup(client):
    client.add_cog(GuildSchedule(client))
