import discord
from discord.ext import commands, tasks
from discord.utils import get

import sqlite3
import shelve
import random
import datetime
from pytz import timezone

import BotConf

class GuildManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        if not bool(raffle_entries):
            print("empty list created")
            raffle_entries["entry"] = []
        raffle_entries.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for_approval = get(member.guild.roles, name=BotConf.name_role_for_approval)
        await member.add_roles(for_approval)

        if member.dm_channel is None:
            await member.create_dm()
        await member.dm_channel.send("Welcome to Azure's Discord Channel! Please wait while one of the guild "
                                     "masters attend to your verification...")

    @commands.command(aliases=["vm"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy, BotConf.name_role_recruiter)
    async def verify(self, ctx, *, member: discord.Member):
        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute(f'''INSERT OR IGNORE INTO guild (Username, Total)
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

    @commands.command(aliases=["rj"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy, BotConf.name_role_recruiter)
    async def rejoin(self, ctx, *, member: discord.Member):
        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute(f'''INSERT OR IGNORE INTO guild (Username, Total) 
                      VALUES ('{member.display_name}', 7)
                   ''')
        connect.commit()
        connect.close()

        guild = self.client.get_guild(BotConf.id_guild)
        to_attend = guild.get_role(BotConf.dict_id_role_general["ToAttend"])
        await member.add_roles(to_attend)
        role_member = guild.get_role(BotConf.dict_id_role_general["Member"])
        await member.add_roles(role_member)
        ex_member = guild.get_role(BotConf.dict_id_role_general["Ex"])
        await member.remove_roles(ex_member)
        await ctx.message.delete()

    @commands.command(aliases=["rnm"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy, BotConf.name_role_recruiter)
    async def rename(self, ctx, member: discord.Member, *, new_name):
        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute(f'''UPDATE OR IGNORE infractions
                      SET Username = '{new_name}'
                      WHERE Username = '{member.display_name}'
                   ''')
        connect.commit()
        c.execute(f'''UPDATE OR IGNORE guild
                      SET Username = '{new_name}'
                      WHERE Username = '{member.display_name}'
                   ''')
        connect.commit()

        await member.edit(nick=f"{new_name}")
        await ctx.message.delete()

    @commands.command(aliases=["rs"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy)
    async def resign(self, ctx, member: discord.Member):
        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute(f'''DELETE from infractions
                      WHERE Username = '{member.display_name}'
                   ''')
        connect.commit()
        c.execute(f'''DELETE from guild
                      WHERE Username = '{member.display_name}'
                   ''')
        connect.commit()
        connect.close()

        guild = self.client.get_guild(BotConf.id_guild)
        role_ex = guild.get_role(BotConf.dict_id_role_general["Ex"])
        await member.add_roles(role_ex)
        role_member = guild.get_role(BotConf.dict_id_role_general["Member"])
        await member.remove_roles(role_member)
        role_to_attend = guild.get_role(BotConf.dict_id_role_general["ToAttend"])
        await member.remove_roles(role_to_attend)
        await ctx.message.delete()

    @commands.command(aliases=["ci"])
    @commands.has_role(BotConf.name_role_to_attend)
    @BotConf.in_channel(BotConf.id_channel_attendance)
    async def checkin(self, ctx):
        server_time = timezone("Asia/Jakarta")
        t = datetime.datetime.now(server_time)

        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute(f'''UPDATE guild
                      SET {t.strftime("%A")} = 1,
                          Total = Total + 1
                      WHERE Username = '{ctx.author.display_name}'
                   ''')
        connect.commit()
        c.execute(f'''SELECT Total FROM guild WHERE Username = '{ctx.author.display_name}'
                   ''')
        total = c.fetchone()
        connect.close()

        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        raffle_entries["entry"].append(f"{ctx.author.display_name}")
        raffle_entries.close()

        to_attend = get(ctx.guild.roles, name=BotConf.name_role_to_attend)
        await ctx.author.remove_roles(to_attend)
        await ctx.message.delete()
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        await ctx.author.dm_channel.send(f"Thank you for logging in today {ctx.author.display_name}, the guild "
                                         f"appreciates you for being active! You have currently logged in "
                                         f"{total[0]} time(s) this week.")

    @commands.command(aliases=["mrfl"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def manualraffle(self, ctx, member: discord.Member, entries):
        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        for i in range(int(entries)):
            raffle_entries["entry"].append(f"{member.display_name}")
        raffle_entries.close()

        guild = self.client.get_guild(BotConf.id_guild)
        role_attend = guild.get_role(BotConf.id_role_to_attend)
        if role_attend in member.roles:
            await member.remove_roles(role_attend)

        await ctx.message.delete()

    @commands.command(aliases=["chkrfl"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def checkraffle(self, ctx):
        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        string_entries = ""
        for entry in raffle_entries["entry"]:
            string_entries += f"{entry}\n"
        raffle_entries.close()

        await ctx.message.delete()
        await ctx.channel.send(f"**Raffle Entries for Deputy role:**"
                               f"```\n"
                               f"{string_entries}"
                               f"```")

    @commands.command(aliases=["drfl"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def drawraffle(self, ctx):
        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        string_winner = random.choice(raffle_entries["entry"])
        raffle_entries.close()
        await ctx.channel.send(f"**Congratulations to {string_winner}!** You have won the deputy role for the week!")
        await ctx.message.delete()

    @commands.command(aliases=["rstrfl"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def resetraffle(self, ctx):
        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        raffle_entries["entry"] = []
        raffle_entries.close()

    @commands.command(aliases=["cntrfl"])
    @commands.has_role(BotConf.name_role_guildmaster)
    async def countraffle(self, ctx):
        raffle_entries = shelve.open(BotConf.path_raffle_database, writeback=True)
        count_entries = {x: raffle_entries["entry"].count(x) for x in raffle_entries["entry"]}
        raffle_entries.close()

        string_entries = ""
        for key, value in count_entries.items():
            string_entries += f"{key} - {value}\n"

        await ctx.channel.send(f"**Member - \# of Entries:**\n"
                               f"```\n"
                               f"{string_entries}"
                               f"```")
        await ctx.message.delete()

    @commands.command(aliases=["grc"])
    @commands.has_role(BotConf.name_role_member)
    async def guildrecords(self, ctx):
        connect = sqlite3.connect(BotConf.path_database)
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
        connection = sqlite3.connect(BotConf.path_database)
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
    async def updateattendanceembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description=f"Please type {BotConf.bot_prefix}checkin or "
                                                              f"{BotConf.bot_prefix}ci to record your attendance "
                                                              f"for today. This will give you an entry to the deputy "
                                                              f"raffle which will happen every Sunday "
                                                              f"(after battle sim).",
                              color=0x0096ff)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_thumbnail(url="https://i.imgur.com/4AwatSh.png")

        embed.add_field(name="Terms and Conditions:",
                        value="Before/During raffle:\n"
                              "1. By checking in, you agree to accept the deputy role if "
                              "you ever win the raffle.\n"
                              "2. You must not be inactive 2 days or above at the time of the raffle. If you win and "
                              "are inactive, your win will be null and void and a re-roll for your spot will occur.\n\n"
                              "As Deputy:\n"
                              "1. You are not allowed to kick anyone or initiate any merge without my consent, or "
                              "instructions.\n"
                              "2. If ever I'm not online during Tuesday or Thursday night, you are urged to start the "
                              "Star of Cassell and Feast events.\n"
                              "3. I reserve the right to appoint another deputy if I deem you unfit for the role "
                              "during the week. (inactivity without notice)")

        embed.set_footer(text="Attendance module resets at 23:10 Server Time.")
        msg: discord.Message= await ctx.channel.fetch_message(715463399907262534)
        await msg.edit(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def inactiveembed(self, ctx):
        embed = discord.Embed(title="Azure Club", description="Member inactivity notice", color=0xff0000)
        embed.set_author(name="Azure",
                         url="https://github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")

        connection = sqlite3.connect(BotConf.path_database)
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

    @commands.command()
    async def directoryembed(self, ctx):
        channel_directory = self.client.get_channel(BotConf.dict_id_channels["Directory"])

        embed = discord.Embed(title="Azure Club", description="Directory for Azure's Discord", color=0x2decec)
        embed.set_author(name="Azure",
                         url="https://www.github.com/mrrazonj/Azure-Bot", icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_thumbnail(url="https://i.imgur.com/4AwatSh.png")
        embed.add_field(name="#attendance",
                        value="This is where you check-in daily to record your attendance. If you can see this "
                              "channel, then that means you still have yet to `checkin` for the day.",
                        inline=False)
        embed.add_field(name="#notices",
                        value="Check here for any new announcement or news regarding the game or our club.",
                        inline=False)
        embed.add_field(name="#general",
                        value="This is our main chat room, anything related to the game, or state of our club can be "
                              "discussed in here.",
                        inline=False)
        embed.add_field(name="#off-topic",
                        value="Everything not about the game, goes in here. You can chat with anyone about anything. ",
                        inline=False)
        embed.add_field(name="#nsfw", value="Not Safe For Work. Adult's channel ( ͡° ͜ʖ ͡°)", inline=False)
        embed.add_field(name="#quiz-event-answers",
                        value="Contains the links to the answer keys for Salon/Brain and Gossip. Other quiz events may "
                              "be added in the future.",
                        inline=False)
        embed.add_field(name="#tale-walkthrough",
                        value="Contains the links to the guides on how to start and complete the tales/anecdotes in "
                              "the game.",
                        inline=False)
        embed.add_field(name="#whale-101",
                        value="Contains the links to the guides on how to spend your money wisely on this game",
                        inline=False)
        embed.add_field(name="#build-sharing", value="Work-in-progress", inline=False)
        embed.add_field(name="#reminders",
                        value="You can get roles here so you can be notified if a certain event you want is starting.",
                        inline=False)
        embed.add_field(name="#party-builder",
                        value="You can get your class role from here, and you can enter your name to any of the "
                              "categories if you're looking for a group to play with. Remember to ping/mention others "
                              "if you can currently build a working team.",
                        inline=False)
        embed.add_field(name="#world-boss-timers", value="Deprecated channel, left over from Blade and Soul",
                        inline=False)
        embed.add_field(name="#bot-commands-channel", value="For bot usage", inline=False)
        embed.set_footer(text="Please remember to respect other members at all times. English-only please. Thank you!")

        await channel_directory.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def updatedirectory(self, ctx):
        channel_directory: discord.TextChannel = self.client.get_channel(BotConf.dict_id_channels["Directory"])
        embed_directory = await channel_directory.fetch_message(718139411086442516)

        embed = discord.Embed(title="Azure Club", description="Directory for Azure's Discord", color=0x2decec)
        embed.set_author(name="Azure",
                         url="https://www.github.com/mrrazonj/Azure-Bot",
                         icon_url="https://i.imgur.com/alUOIgz.png")
        embed.set_thumbnail(url="https://i.imgur.com/4AwatSh.png")

        embed.add_field(name="#attendance",
                        value="This is where you check-in daily to record your attendance. If you can see this "
                              "channel, then that means you still have yet to `checkin` for the day.",
                        inline=False)

        embed.add_field(name="#notices",
                        value="Check here for any new announcement or news regarding the game or our club.",
                        inline=False)

        embed.add_field(name="#inactivity-submission",
                        value="This is were you would request a break from the game for daily activity. Mention "
                              "XenoXIII, or AkshayAg in your message, include also the amount of time you need, "
                              "and optionally, the reason why. Please do not abuse this feature.",
                        inline=False)

        embed.add_field(name="#general",
                        value="This is our main chat room, anything related to the game, or state of our club can be "
                              "discussed in here.",
                        inline=False)

        embed.add_field(name="#off-topic",
                        value="Everything not about the game, goes in here. You can chat with anyone about anything. ",
                        inline=False)

        embed.add_field(name="#nsfw", value="Not Safe For Work. Adult's channel ( ͡° ͜ʖ ͡°)", inline=False)

        embed.add_field(name="#quiz-event-answers",
                        value="Contains the links to the answer keys for Salon/Brain and Gossip. Other quiz events may "
                              "be added in the future.",
                        inline=False)

        embed.add_field(name="#tale-walkthrough",
                        value="Contains the links to the guides on how to start and complete the tales/anecdotes in "
                              "the game.",
                        inline=False)

        embed.add_field(name="#whale-101",
                        value="Contains the links to the guides on how to spend your money wisely on this game",
                        inline=False)

        embed.add_field(name="#build-sharing", value="Work-in-progress", inline=False)

        embed.add_field(name="#reminders",
                        value="You can get roles here so you can be notified if a certain event you want is starting.",
                        inline=False)

        embed.add_field(name="#party-builder",
                        value="You can get your class role from here, and you can enter your name to any of the "
                              "categories if you're looking for a group to play with. Remember to ping/mention others "
                              "if you can currently build a working team.",
                        inline=False)

        embed.add_field(name="#world-boss-timers", value="Deprecated channel, left over from Blade and Soul",
                        inline=False)

        embed.add_field(name="#bot-commands-channel", value="For bot usage", inline=False)

        embed.set_footer(
            text="Please remember to respect other members at all times. English-only please. Thank you!")

        await embed_directory.edit(embed=embed)
        await ctx.message.delete()

    @commands.command(aliases=["glen"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy)
    async def giveleniency(self, ctx, member: discord.Member):
        guild = self.client.get_guild(BotConf.id_guild)
        leniency_role = guild.get_role(BotConf.dict_id_role_general["Leniency"])

        connection = sqlite3.connect(BotConf.path_database)
        c = connection.cursor()
        c.execute(f'''UPDATE guild
                      SET Total = Total + {BotConf.num_attendances_required}
                      WHERE Username = '{member.display_name}'
                   ''')
        connection.commit()
        connection.close()

        await member.add_roles(leniency_role)
        await ctx.message.delete()

    @commands.command(aliases=["rlen"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy)
    async def remove_leniency(self, ctx, member: discord.Member):
        guild = self.client.get_guild(BotConf.id_guild)
        leniency_role = guild.get_role(BotConf.dict_id_role_general["Leniency"])
        await member.remove_roles(leniency_role)
        await ctx.message.delete()

    @commands.command(aliases=["uinf"])
    @commands.has_any_role(BotConf.name_role_guildmaster, BotConf.name_role_deputy)
    async def update_infractions(self, ctx):
        channel_notice: discord.TextChannel = self.client.get_channel(BotConf.id_channel_notice)

        connect = sqlite3.connect(BotConf.path_database)
        c = connect.cursor()
        c.execute('''SELECT * FROM infractions WHERE Penalties > 0''')
        list_entry = c.fetchall()
        connect.close()

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
        msg = await channel_notice.fetch_message(715520609890729995)
        await msg.edit(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.has_role(BotConf.name_role_guildmaster)
    async def guidepve(self, ctx):
        embed = discord.Embed(title="Xeno's Ultimate PVE Guide for Assassins", url="https://www.github.com/mrrazonj",
                              description="Just as a preface to this guide, you should really be stacking MATK and MS "
                                          "as high as you can. This means focusing on INT and DEX. You won't need "
                                          "survivability much because in a working team, you should have a functional "
                                          "tank. You also have two invulnerability skills, plus if you transition to "
                                          "your dagger stance, you will become invisible and lose aggro.",
                              color=0x953eff)
        embed.set_author(
            name="XenoXIII",
            icon_url="https://i.pximg.net/img-master/img/2019/05/18/01/21/36/74775564_p0_master1200.jpg")
        embed.set_thumbnail(url="https://i.imgur.com/lSZlEFE.png")
        embed.add_field(name="Talents", value="-", inline=False)
        embed.add_field(name="C - Heroic Sonata",
                        value="Same with the PVP guide, this gives you the most benefits. The Variance "
                              "talent gives you a damage boost only for your MS procs, but this talent provides "
                              "a boost across the board.",
                        inline=False)
        embed.add_field(name="B - Dissonance",
                        value="This talent is RNG-based. It can get pretty crazy like let you reset your Prelude "
                              "Dawn AND Shadow Strike's cooldown 7 times in a row if you're lucky with the procs. "
                              "It benefits your DPS both in Hunt and Dark mode.",
                        inline=False)
        embed.add_field(name="A - Echo of Soul",
                        value="Ever wish you would proc more Multistrikes? Then take this talent with you! It gives "
                              "you twice the base chance to proc an MS from your Dawn Prelude or Soul FIssure skills, "
                              "both at a very low cooldown (5s~)",
                        inline=False)
        embed.add_field(name="S - Nibelungen Song",
                        value="This talent synergizes with the other ones. It gives a nice boost to your DPS in Hunt "
                              "Mode, and some much needed survivability in Dark Mode. Pray to RNGesus so you can proc "
                              "those MSes all day long.",
                        inline=False)
        embed.add_field(name="Ex Skills", value="-", inline=False)
        embed.add_field(name="Scorch",
                        value="Most damage per second elemental EX skill. Prioritize casting this whenever it goes off "
                              "CD",
                        inline=False)
        embed.add_field(name="Blackhole", value="Free DPS. Prioritize casting this whenever it goes off CD.",
                        inline=False)
        embed.add_field(name="Gameplay",
                        value="**!!DO NOT USE AUTOBATTLE!!** - Now that we have that out of the way, assassin can be "
                              "very mechanically intensive to play. My hands cramp up when playing the longer events, "
                              "but it's totally worth it. Most of your DPS comes from Dark Mode. You will only use "
                              "your Hunt Mode only if all your skills in Dark Mode are on cooldown (always wait for "
                              "CDs that are ~2s)",
                        inline=False)
        embed.add_field(name="Hunt Mode",
                        value="Use both of your EX skills for the opening. Follow up with Prelude Dawn, Dark Rhapsody, "
                              "and Nocturne Luna. Pay attention to your Prelude Dawn if its CD has reset. Prioritize "
                              "using it when it resets. When all skills are on cooldown, transition to Dark Mode.",
                        inline=False)
        embed.add_field(name="Dark Mode",
                        value="Pay attention to your marks. Always use Shadow Strike whenever you mark the enemy. "
                              "Prioritize using Soul Fissure because it has the least cooldown, and highest chance "
                              "to proc MS. Always use Shadow Dart in point blank range so all three shurikens will "
                              "hit, follow up this with Shadow Strike because it's a guaranteed mark. Be careful not "
                              "to consume your mark using Obsidian Edge. Your normal attacks also reduce Shadow "
                              "Dart's CD by 0.3s every time.You should only exit this form when every skill is on CD.",
                        inline=False)
        embed.set_image(url="https://i.imgur.com/CrFROvs.png")
        embed.set_footer(text="That's all for now.")
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        connect = sqlite3.connect(BotConf.path_database)
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


def setup(client):
    client.add_cog(GuildManagement(client))
