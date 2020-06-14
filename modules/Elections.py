import discord
from discord.ext import commands, tasks

import sqlite3

import BotConf
import datetime
from pytz import timezone


class Elections(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client

        self.list_candidates = []
        self.list_votes = []
        self.dict_count_votes = {}

        self.current_time = ""

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        guild: discord.Guild = self.client.get_guild(BotConf.id_guild)
        role_gm = guild.get_role(BotConf.dict_id_role_general["GuildMaster"])
        if msg.channel == self.client.get_channel(BotConf.dict_id_channels["Elections"]):
            if role_gm not in msg.author.roles:
                if not msg.author == self.client.user:
                    if not msg.content.startswith("."):
                        await msg.delete()

    @commands.command()
    async def resetelection(self, ctx):
        self.list_candidates = []
        self.list_votes = []
        self.dict_count_votes = {}
        await ctx.message.delete()

    @commands.command()
    async def geteligible(self, ctx):
        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute('''SELECT Username 
                     FROM guild 
                     WHERE Total >= 5
                  ''')

        list_candidates = c.fetchall()
        for candidate in list_candidates:
            self.list_candidates.append(candidate[0])

    @commands.command()
    async def electiondeputy(self, ctx):
        channel_log: discord.TextChannel = self.client.get_channel(BotConf.id_channel_log)
        string_candidates = ""
        for idx, candidate in enumerate(self.list_candidates, start=1):
            string_candidates += f"{idx} - {candidate}\n"
        embed = discord.Embed(title="Azure Club",
                              description="Welcome to the official elections for our 2nd club Deputy. If you have at "
                                          "least 5 check-ins on Discord for this week, you are automatically a "
                                          "candidate. Should you win, and you choose to relinquish the position, "
                                          "it will be given to the next member with the most votes. Should a tie "
                                          "occur, it shall be decided by the Ice or Fire command, whereby the member "
                                          "with the lower ballot number will be Ice.")
        embed.set_thumbnail(url="https://i.imgur.com/4AwatSh.png")
        embed.set_author(name="Azure", url="https://www.github.com/mrrazonj/Azure-Bot",
                         icon_url="https://i.imgur.com/alUOIgz.png")
        embed.add_field(name="How to Vote", value=f"Just type in `.vote #` in this channel.")
        embed.add_field(name="Candidates", value=f"{string_candidates}", inline=False)

        server_time = timezone("Asia/Jakarta")
        t = datetime.datetime.now(server_time)
        self.current_time = t.strftime("%H:%M")
        embed.set_footer(text=f"This election started on {self.current_time} GMT+7")
        await ctx.channel.send(embed=embed)

        guild = self.client.get_guild(BotConf.id_guild)
        role_vote = guild.get_role(721377309138878465)
        role_member: discord.Role = guild.get_role(BotConf.dict_id_role_general["Member"])
        list_member = role_member.members
        for member in list_member:
            await member.add_roles(role_vote)

        await ctx.message.delete()

    @commands.command()
    async def vote(self, ctx, number: int):
        if number < 1:
            return
        if number > len(self.list_candidates):
            return
        number -= 1
        self.list_votes.append(self.list_candidates[number])
        self.dict_count_votes = {x: self.list_votes.count(x) for x in self.list_votes}

        guild = self.client.get_guild(BotConf.id_guild)
        role_vote = guild.get_role(721377309138878465)
        await ctx.author.remove_roles(role_vote)

    @commands.command()
    async def results(self, ctx):
        string_results = ""
        for member, vote in self.dict_count_votes.items():
            string_results += f"{member} - {vote}\n"
        await ctx.channel.send(f"```\n"
                               f"{string_results}"
                               f"```")


def setup(client):
    client.add_cog(Elections(client))