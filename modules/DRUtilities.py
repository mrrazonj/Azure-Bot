import discord
from discord.ext import commands, tasks
import asyncio

import random
import time

import BotConf


class DragonRajaUtilities(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.dict_event_members = {
            "Good Times": [],
            "Dragonhunt": [],
            "Radiant - Normal": [],
            "Radiant - Hard": [],
            "Nirvana - Normal": [],
            "Nirvana - Hard": []
        }

        self.dict_event_dungeons = {}
        index = 1
        for key, value in self.dict_event_members.items():
            self.dict_event_dungeons[index] = key
            index += 1

    @commands.command(aliases=["iof"])
    async def iceorfire(self, ctx):
        list_choice = ["Ice", "Ice", "Ice", "Fire", "Fire", "Fire"]
        await ctx.channel.send(f"You must choose **{random.choice(list_choice)}**.")
        await ctx.message.delete()

    @tasks.loop(minutes=1.0)
    async def timed_event_ping(self):
        guild = self.client.get_guild(BotConf.id_guild)
        channel_reminder = guild.get_channel(BotConf.dict_id_channels["Reminder"])

        role_salon_brain = guild.get_role(BotConf.dict_id_role_events["Salon"])
        role_event_pve = guild.get_role(BotConf.dict_id_role_events["ClubPVE"])
        role_gossip = guild.get_role(BotConf.dict_id_role_events["Gossip"])
        role_event_pvp = guild.get_role(BotConf.dict_id_role_events["ClubPVP"])
        role_liberty_day = guild.get_role(BotConf.dict_id_role_events["DayOfLiberty"])
        role_irritated_blood = guild.get_role(BotConf.dict_id_role_events["IrritatedBlood"])
        role_wboss_borgman = guild.get_role(BotConf.dict_id_role_events["WBBorgman"])

        time_liberty_day = "12:00"
        time_salon_brain = "13:00"
        time_event_pve = "13:30"
        list_time_irritated_blood = ["13:00",
                                     "20:00"]
        time_gossip = "21:00"
        time_event_pvp = "22:00"
        list_time_borgman_spawn = ["12:30",
                                   "16:30",
                                   "20:30",
                                   "00:30"]

        t = time.localtime()
        current_time = time.strftime("%H:%M", t)

        if current_time == time_liberty_day:
            await channel_reminder.send(role_liberty_day.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_salon_brain:
            await channel_reminder.send(role_salon_brain.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_event_pve:
            await channel_reminder.send(role_event_pve.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time in list_time_irritated_blood:
            await channel_reminder.send(role_irritated_blood.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_gossip:
            await channel_reminder.send(role_gossip.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time == time_event_pvp:
            await channel_reminder.send(role_event_pvp.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()
        if current_time in list_time_borgman_spawn:
            await channel_reminder.send(role_wboss_borgman.mention)
            msg = await channel_reminder.fetch_message(channel_reminder.last_message_id)
            await asyncio.sleep(5)
            await msg.delete()

    @timed_event_ping.before_loop
    async def before_ping(self):
        await self.client.wait_until_ready()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def partybuilderembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description="This is the list of members per dungeon/event that "
                                                              "haven't finished them yet and are looking for party "
                                                              "members. Coordinate with each other bearing in mind "
                                                              "each other's classes", color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_footer(text="This stub refreshes every 5 seconds.")
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["lfp"])
    @commands.has_any_role("Blademaster", "Gunslinger", "Assassin", "Souldancer")
    async def lookingforparty(self, ctx, event_code):
        guild = self.client.get_guild(BotConf.id_guild)

        role_blademaster = guild.get_role(BotConf.dict_id_role_class["Blademaster"])
        role_gunslinger = guild.get_role(BotConf.dict_id_role_class["Gunslinger"])
        role_assassin = guild.get_role(BotConf.dict_id_role_class["Assassin"])
        role_souldancer = guild.get_role(BotConf.dict_id_role_class["Souldancer"])
        list_abc_roles = [role_assassin, role_blademaster, role_gunslinger, role_souldancer]

        member_role = discord.abc.Snowflake
        for role in list_abc_roles:
            if role in ctx.author.roles:
                member_role = role

        code = int(event_code)
        self.dict_event_members[self.dict_event_dungeons[code]].append(f"{ctx.author.display_name} - "
                                                                       f"{member_role.name}")

        channel_lfp = self.client.get_channel(BotConf.dict_id_channels["LFP"])
        embed_msg = await channel_lfp.fetch_message(716222933839904880)

        string_event_formatted = ""
        for key, value in self.dict_event_dungeons.items():
            string_event_formatted += f"{key} - {value}\n"

        embed = discord.Embed(title="Azure Club",
                              description=f"These are lists of members per dungeon/event that "
                                          f"haven't finished them yet and are looking for party "
                                          f"members. Coordinate with each other bearing in mind "
                                          f"each other's classes.\n\n"
                                          f"To add yourself to any of the lists, type "
                                          f"`.lfp event-number`\n\n"
                                          f"The event numbers and corresponding events are as follows:\n\n"
                                          f"{string_event_formatted}\n"
                                          f"To remove yourself, use `.nlfp event-number`",
                              color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")

        for key, value in self.dict_event_dungeons.items():
            string_list_format = ("\n".join(str(i) for i in self.dict_event_members[value]))
            string_blank = "None"
            embed.add_field(name=f"{value}",
                            value=f"{string_blank if not self.dict_event_members[value] else string_list_format}",
                            inline=False)

        embed.set_footer(text="This stub refreshes every 5 seconds.")
        await embed_msg.edit(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["nlfp"])
    async def notlookingforparty(self, ctx, event_code):
        guild = self.client.get_guild(BotConf.id_guild)

        role_blademaster = guild.get_role(BotConf.dict_id_role_class["Blademaster"])
        role_gunslinger = guild.get_role(BotConf.dict_id_role_class["Gunslinger"])
        role_assassin = guild.get_role(BotConf.dict_id_role_class["Assassin"])
        role_souldancer = guild.get_role(BotConf.dict_id_role_class["Souldancer"])
        list_abc_roles = [role_assassin, role_blademaster, role_gunslinger, role_souldancer]

        member_role = discord.abc.Snowflake
        for role in list_abc_roles:
            if role in ctx.author.roles:
                member_role = role

        channel_lfp = self.client.get_channel(BotConf.dict_id_channels["LFP"])
        embed_msg = await channel_lfp.fetch_message(716222933839904880)

        string_event_formatted = ""
        for key, value in self.dict_event_dungeons.items():
            string_event_formatted += f"{key} - {value}\n"

        embed = discord.Embed(title="Azure Club",
                              description=f"These are lists of members per dungeon/event that "
                                          f"haven't finished them yet and are looking for party "
                                          f"members. Coordinate with each other bearing in mind "
                                          f"each other's classes.\n\n"
                                          f"To add yourself to any of the lists, type "
                                          f"`.lfp <event-number>`\n\n"
                                          f"The event numbers and corresponding events are as follows:\n\n"
                                          f"{string_event_formatted}\n"
                                          f"To remove yourself, use `.nlfp <event-number>`",
                              color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")

        for key, value in self.dict_event_dungeons.items():
            string_list_format = ("\n".join(str(i) for i in self.dict_event_members[value]))
            string_blank = "None"
            embed.add_field(name=f"{value}",
                            value=f"{string_blank if not self.dict_event_members[value] else string_list_format}",
                            inline=False)

        embed.set_footer(text="This stub refreshes every 5 seconds.")
        await embed_msg.edit(embed=embed)

        code = int(event_code)
        self.dict_event_members[self.dict_event_dungeons[code]].remove(f"{ctx.author.display_name} - "
                                                                       f"{member_role.name}")
        await ctx.message.delete()

    @tasks.loop(seconds=5.0)
    async def update_party_builder(self):
        channel_lfp = self.client.get_channel(BotConf.dict_id_channels["LFP"])
        embed_msg = await channel_lfp.fetch_message(716222933839904880)

        string_event_formatted = ""
        for key, value in self.dict_event_dungeons.items():
            string_event_formatted += f"{key} - {value}\n"

        embed = discord.Embed(title="Azure Club",
                              description=f"These are lists of members per dungeon/event that "
                                          f"haven't finished them yet and are looking for party "
                                          f"members. Coordinate with each other bearing in mind "
                                          f"each other's classes.\n\n"
                                          f"To add yourself to any of the lists, type "
                                          f"`.lfp event-number`\n\n"
                                          f"The event numbers and corresponding events are as follows:\n\n"
                                          f"{string_event_formatted}\n"
                                          f"To remove yourself, use `.nlfp event-number`",
                              color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")

        for key, value in self.dict_event_dungeons.items():
            string_list_format = ("\n".join(str(i) for i in self.dict_event_members[value]))
            string_blank = "None"
            embed.add_field(name=f"{value}",
                            value=f"{string_blank if not self.dict_event_members[value] else string_list_format}",
                            inline=False)

        embed.set_footer(text="This stub refreshes every 5 seconds.")
        await embed_msg.edit(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.timed_event_ping.start()
        self.update_party_builder.start()


def setup(client):
    client.add_cog(DragonRajaUtilities(client))
