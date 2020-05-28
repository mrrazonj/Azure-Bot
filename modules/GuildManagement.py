import discord
from discord.ext import commands, tasks
from discord.utils import get

import sqlite3
import time

import BotConf

connect = sqlite3.connect("modules/data/guild.db")
c = connect.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS guild
            (
             Username text primary key,
             Monday int,
             Tuesday int,
             Wednesday int,
             Thursday int,
             Friday int,
             Saturday int,
             Sunday int,
             Total int default 0)
           ''')

c.execute('''CREATE TABLE IF NOT EXISTS infractions
            (
             Username text primary key,
             Penalties int DEFAULT 0,
                FOREIGN KEY (Username)
                    REFERENCES guild (USERNAME)
            )
           ''')

connect.close()


class GuildManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for_approval = get(member.guild.roles, name=BotConf.name_role_for_approval)
        await member.add_roles(for_approval)

        if member.dm_channel is None:
            await member.create_dm()
        await member.dm_channel.send("Welcome to Azure's Discord Channel! Please wait while one of the guild "
                                     "masters attend to your verification...")

    @commands.command(aliases=["vm"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def verify(self, ctx, *, member: discord.Member):
        connect = sqlite3.connect("modules/data/guild.db")
        c = connect.cursor()
        c.execute(f'''INSERT INTO guild (Username, Total)
                      VALUES ('{member.display_name}', 7)
                   ''')
        connect.commit()
        connect.close()
        to_attend = get(ctx.guild.roles, name=BotConf.name_role_to_attend)
        for_approval = get(ctx.guild.roles, name=BotConf.name_role_for_approval)
        member_role = get(ctx.guild.roles, name=BotConf.name_role_member)
        await member.remove_roles(for_approval)
        await member.add_roles(member_role)
        await member.add_roles(to_attend)
        await ctx.message.delete()

    @commands.command(aliases=["ci"])
    @commands.has_role(BotConf.name_role_to_attend)
    @BotConf.in_channel(BotConf.id_channel_attendance)
    async def checkin(self, ctx):
        t = time.localtime()
        connect = sqlite3.connect("modules/data/guild.db")
        c = connect.cursor()
        c.execute(f'''UPDATE guild
                      SET {time.strftime("%A", t)} = 1,
                          Total = Total + 1
                      WHERE Username = '{ctx.author.display_name}'
                   ''')
        connect.commit()
        c.execute(f'''SELECT Total FROM guild WHERE Username = '{ctx.author.display_name}'
                   ''')
        total = c.fetchone()
        connect.close()
        to_attend = get(ctx.guild.roles, name=BotConf.name_role_to_attend)
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        await ctx.author.dm_channel.send(f"Thank you for logging in today {ctx.author.display_name}, the guild "
                                         f"appreciates you for being active! You have currently logged in "
                                         f"{total[0]} time(s) this week.")
        await ctx.author.remove_roles(to_attend)
        await ctx.message.delete()

    @commands.command(aliases=["grc"])
    @commands.has_role(BotConf.name_role_member)
    async def guildrecords(self, ctx):
        connect = sqlite3.connect("modules/data/guild.db")
        c = connect.cursor()
        c.execute(f'''SELECT Username FROM guild WHERE Total < {BotConf.num_attendances_required}
        ''')
        members = c.fetchall()
        connect.close()

        list_member = []
        for member in members:
            list_member.append(member[0])
        list_inactive = ("\n".join(str(i) for i in list_member))

        string_blank = "None\n"
        await ctx.channel.send(f"**Inactive Members (less than 5 check-ins for this week):**\n"
                               f"```css\n"
                               f"{string_blank if not list_member else list_inactive}\n"
                               f"```")
        await ctx.message.delete()

    @commands.command(aliases=["mp"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def manualpenalty(self, ctx):
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
            print(member)
            c.execute(f'''UPDATE infractions
                          SET Penalties = Penalties + 1
                          WHERE Username = '{member}'
                       ''')
            connection.commit()
        connection.close()

        list_inactive = ("\n".join(str(i) for i in list_member))
        await ctx.channel.send(f"**Inactive members penalized:**\n"
                               f"```css\n"
                               f"{list_inactive}\n"
                               f"```")
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def welcomeembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description="Screening channel for members", color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_thumbnail(url="https://i.imgur.com/w7jhGua.png")
        embed.add_field(name="Why is this necessary?", value=">>> 1. To make it easier for us to discuss what to do "
                                                             "for events.\n\n"
                                                             "2. To make it easier for us to look for party members or "
                                                             "make schedules in doing events. \n\n"
                                                             "3. To make it easier for me to track inactive "
                                                             "members. \n\n"
                                                             "These are all possible through this bot made specially "
                                                             "for this guild.",
                        inline=False)
        embed.add_field(name="What to do now?", value=">>> 1. Change your nickname to match your in-game character "
                                                      "name.\n\n"
                                                      "2. Wait for a guildmaster to process your verification.",
                        inline=False)
        embed.set_footer(text="Please be patient if no guildmaster is currently online to process your verification.")
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def attendanceembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description=f"Please type {BotConf.bot_prefix}checkin or "
                                                              f"{BotConf.bot_prefix}ci to record your attendance "
                                                              f"for today.",
                              color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_footer(text="Attendance module resets at 23:10 Server Time.")
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def inactiveembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description="Member inactivity notice", color=0xff0000)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")

        connection = sqlite3.connect("modules/data/guild.db")
        c = connection.cursor()
        c.execute('''SELECT * FROM infractions WHERE Penalties > 0''')
        list_entry = c.fetchall()
        connection.close()

        list_entry_formatted = []
        for entry in list_entry:
            list_entry_formatted.append(f"{entry[0]} - {entry[1]} infractions")

        list_finalized = ("\n".join(str(i) for i in list_entry_formatted))
        string_empty = "None"

        embed.add_field(name=f"Members with infractions incurred:",
                        value=f"{string_empty if not list_entry_formatted else list_finalized}")
        embed.set_footer(text="This stub updates every Sunday at 23:10.")
        msg_embed = await ctx.channel.fetch_message(715520609890729995)
        await msg_embed.edit(embed=embed)
        await ctx.message.delete()


def setup(client):
    client.add_cog(GuildManagement(client))
