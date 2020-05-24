import discord
from discord.ext import commands, tasks
from discord.utils import get

import sqlite3
import time

connect = sqlite3.connect("modules/data/guild.db")
c = connect.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS attendance
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

connect.close()


class GuildManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for_approval = get(member.guild.roles, name="For-Approval")
        await member.add_roles(for_approval)

        if member.dm_channel is None:
            await member.create_dm()
        await member.dm_channel.send("Welcome to Azure's Discord Channel! Please wait while one of the guild "
                                     "masters attend to your verification...")

    @commands.command(aliases=["ci"])
    @commands.has_role("To-Attend")
    async def checkin(self, ctx):
        t = time.localtime()
        connect = sqlite3.connect("modules/data/guild.db")
        c = connect.cursor()
        c.execute(f'''UPDATE attendance
                      SET {time.strftime("%A", t)} = 1,
                          Total = Total + 1
                      WHERE Username = '{ctx.author.display_name}'
                   ''')
        connect.commit()
        c.execute(f'''SELECT Total FROM attendance WHERE Username = '{ctx.author.display_name}'
                   ''')
        total = c.fetchone()
        connect.close()
        to_attend = get(ctx.guild.roles, name="To-Attend")
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        await ctx.author.dm_channel.send(f"Thank you for logging in today {ctx.author.display_name}, the guild "
                                         f"appreciates you for being active! You have currently logged in "
                                         f"{total[0]} time(s) this week.")
        await ctx.author.remove_roles(to_attend)
        await ctx.message.delete()

    @commands.command(aliases=["vm"])
    @commands.has_role("Guild Master")
    async def verify(self, ctx, *, member: discord.Member):
        connect = sqlite3.connect("modules/data/guild.db")
        c = connect.cursor()
        c.execute(f'''INSERT INTO attendance (Username, Total)
                      VALUES ('{member.display_name}', 7)
                   ''')
        connect.commit()
        connect.close()
        to_attend = get(ctx.guild.roles, name="To-Attend")
        for_approval = get(ctx.guild.roles, name="For-Approval")
        member_role = get(ctx.guild.roles, name="Member")
        await member.remove_roles(for_approval)
        await member.add_roles(member_role)
        await member.add_roles(to_attend)
        await ctx.message.delete()


def setup(client):
    client.add_cog(GuildManagement(client))
