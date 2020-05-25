import discord
from discord.ext import commands

import sqlite3


class GeneralUtilities(commands.Cog):

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
        if not ctx.message.role_mentions:
            if target_role.startswith('@'):
                target_role = target_role[1:]
            role_list = []
            for role in ctx.guild.roles:
                role_list.append(role.name)
            if target_role not in role_list:
                await ctx.channel.send(f"{target_role} role not found!")
                await ctx.message.delete()
                return

        else:
            target_role = ctx.message.role_mentions[0].name

        member_list = []
        for role in ctx.guild.roles:
            if role.name == target_role:
                for members in role.members:
                    member_list.append(members.display_name)

        final_list = ("\n".join(str(i) for i in member_list))
        await ctx.channel.send(f"**Members in {target_role} role:**"
                               f"```css\n"
                               f"{final_list}\n"
                               f"```")
        await ctx.message.delete()


def setup(client):
    client.add_cog(GeneralUtilities(client))
