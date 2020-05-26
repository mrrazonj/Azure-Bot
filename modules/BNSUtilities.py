import discord
from discord.ext import commands, tasks

import BotConf
id_world_boss_channel = 714724286379589692


class BNSUtilities(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.world_boss_and_timer_list = []

    @tasks.loop(minutes=1)
    async def update_world_boss_embed(self):
        channel_world_boss = self.client.get_channel(id_world_boss_channel)
        embed_fbt = discord.Embed(color=0x27d827)
        embed_fbt.title = "Field Boss Timers"
        embed_fbt.set_author(name="Azure", url="https://github.com/mrrazonj/Azure-Bot/",
                             icon_url="https://i.imgur.com/tFuM5gd.png")
        embed_fbt.set_thumbnail(url="https://i.imgur.com/XUldg3M.png")

        if not self.world_boss_and_timer_list:
            embed_fbt.add_field(name="Boss - Spawn timer", value="No Data", inline=False)
        else:
            list_boss_strings = []
            index = 0
            for boss, timer in self.world_boss_and_timer_list:
                self.world_boss_and_timer_list[index][1] -= 1
                timer -= 1
                if timer < 0:
                    del self.world_boss_and_timer_list[index]
                else:
                    list_boss_strings.append(f"{boss} - {timer} min(s)" if timer > 0 else f"{boss} - Spawned!")
                index += 1

            string_boss_column = ("\n".join(str(i) for i in list_boss_strings))
            print(string_boss_column)
            embed_fbt.add_field(name="Boss - Spawn timer", value=string_boss_column, inline=False)

        embed_fbt.set_footer(text="This information stub updates every 1 minute.")
        await channel_world_boss.purge()
        await channel_world_boss.send(embed=embed_fbt)

    @update_world_boss_embed.before_loop
    async def before_update(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["awb"])
    @commands.has_role(BotConf.name_role_member)
    @BotConf.in_channel(id_world_boss_channel)
    async def addworldboss(self, ctx, boss_name, spawn_timer):
        for boss, timer in self.world_boss_and_timer_list:
            if boss_name == boss:
                await ctx.message.delete()
                return

        buffer = [boss_name, int(spawn_timer)]
        self.world_boss_and_timer_list.append(buffer)

        channel_world_boss = self.client.get_channel(id_world_boss_channel)

        embed_fbt = discord.Embed(color=0x27d827)
        embed_fbt.title = "Field Boss Timers"
        embed_fbt.set_author(name="Azure", url="https://github.com/mrrazonj/Azure-Bot/",
                             icon_url="https://i.imgur.com/tFuM5gd.png")
        embed_fbt.set_thumbnail(url="https://i.imgur.com/XUldg3M.png")

        list_boss_strings = []
        index = 0
        for boss, timer in self.world_boss_and_timer_list:
            list_boss_strings.append(f"{boss} - {timer} min(s)" if timer > 0 else f"{boss} - Spawned!")
            index += 1

        string_boss_column = ("\n".join(str(i) for i in list_boss_strings))
        embed_fbt.add_field(name="Boss - Spawn timer", value=string_boss_column, inline=False)
        embed_fbt.set_footer(text="This information stub updates every 1 minute.")

        await channel_world_boss.purge()
        await channel_world_boss.send(embed=embed_fbt)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_world_boss_embed.start()


def setup(client):
    client.add_cog(BNSUtilities(client))