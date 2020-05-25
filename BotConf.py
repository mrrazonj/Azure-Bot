import discord
from discord.ext import commands

#====Bot description and configuration
bot_description = ""
bot_token = ""
bot_prefix = ''


#====Discord server IDs/Names needed for most commands
id_guild = 0
id_channel_log = 0
id_channel_attendance = 0
id_channel_notice = 0
name_role_guildmaster = ""
name_role_member = ""
name_role_to_attend = ""
name_role_for_approval = ""


#====Penalty parameters in GuildManagement.py
num_attendances_required = 0


#====Reset parameters for daily/weekly attendance in GuildSchedule.py
reset_day = ""
reset_hour = 0
reset_minute = 0


#====Extra decorators !!!DO NOT EDIT IF YOU DON'T KNOW WHAT YOU'RE DOING!!!
def in_channel(item):
    def predicate(ctx):
        return ctx.channel.id == item
    return commands.check(predicate)
