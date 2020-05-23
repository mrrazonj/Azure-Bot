import discord
from discord.ext import commands


class Utilities(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["p"])
    async def ping(self, ctx):
        await ctx.send(f"```md\n"
                       f"Latency to bot is {round(self.client.latency*1000, 2)}ms.\n"
                       f"```")

    @commands.command(aliases=["clear", "purge"])
    async def clean(self, ctx, amount=25):
        await ctx.channel.purge(limit=amount)


def setup(client):
    client.add_cog(Utilities(client))
