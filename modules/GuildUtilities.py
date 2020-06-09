import discord
from discord.ext import commands,tasks
from discord.utils import get

import sqlite3

import BotConf


class GuildUtilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["rcself"])
    @commands.has_role(BotConf.name_role_member)
    async def recordsself(self, ctx):
        connection = sqlite3.connect("modules/data/guild.db")
        c = connection.cursor()
        c.execute(f'''SELECT Total FROM guild WHERE Username = '{ctx.author.display_name}'
                       ''')
        total = c.fetchone()
        c.close()
        await ctx.channel.send(f"{ctx.author.display_name} has checked-in {total[0]} time(s) this week!")
        await ctx.message.delete()

    @commands.command(aliases=["rc"])
    @commands.has_role(BotConf.name_role_member)
    async def records(self, ctx, *, member: discord.Member):
        for role in member.roles:
            if role.name == BotConf.name_role_member:
                connection = sqlite3.connect("modules/data/guild.db")
                c = connection.cursor()
                c.execute(f'''SELECT Total FROM guild WHERE Username = '{member.display_name}'
                           ''')
                total = c.fetchone()
                c.close()
                await ctx.channel.send(f"{member.display_name} has checked-in {total[0]} time(s) this week!")
                await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        sender: discord.Member = msg.author
        channel: discord.TextChannel = msg.channel
        if msg.mention_everyone:
            await channel.send(f"Please do not mention @~~everyone~~. {sender.mention}'s infractions have increased "
                               f"by 1!")


def setup(client):
    client.add_cog(GuildUtilities(client))