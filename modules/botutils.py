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
        await ctx.message.delete()

    @commands.command(aliases=["clear", "purge", "cls"])
    async def clean(self, ctx, amount=25):
        await ctx.channel.purge(limit=amount)

    @commands.command(aliases=["lsr"])
    async def listrole(self, ctx, *, target_role):
        member_list = []
        for role in ctx.guild.roles:
            if role.name == target_role:
                for members in role.members:
                    member_list.append(members.display_name)
        await ctx.channel.send(f"```\n"
                               f"{member_list}\n"
                               f"```")


def setup(client):
    client.add_cog(Utilities(client))
