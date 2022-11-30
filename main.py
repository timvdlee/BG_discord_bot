import discord
import os
import datetime
import random

from operator import itemgetter
from discord.commands import Option

BAD_ID = 754374401830551552
DOG_ID = 424883648349601793
arch_start = 990225116824743947
arch_edit = 985244981159678012
arch_del = 990225145811595344

ARCHIVED = 788839782901219338
ARCHIVED_2 = 982710119538229278
EXIBITION = 943101926155902977

BOT_CMDS = 785626495837405205

server_notif = 782217034662019102
gaming_talk = 822172638100193400
motw_participant = 949800887797317692
motw_role = 949801868303958107
motw_channel = 985226350505898054

intents = discord.Intents(messages=True, guilds=True, members=True, message_content=True)

bot = discord.Bot(intents=intents)

EDIT_DICT = {}
DELETION_DICT = {}


#  START_GENERAL_USE


def get_channel_dict(g_id):
    """
    Gets all channels and punts them in a dictonary based on type
    :param g_id: The id of the server it should fetch the channels from
    :return: Channel dict
    """
    server = bot.get_guild(g_id)
    channel_dicts = {}
    for channel in server.channels:
        if channel.type not in channel_dicts:
            channel_dicts[channel.type] = [channel]
        else:
            channel_dicts[channel.type].append(channel)
    return channel_dicts


def get_channels_in_category(chr_dict, category_ids, inverted=False, channel_type=discord.ChannelType.text):
    """
    Finds all channel of the same type which are in a category.
    :param chr_dict: The dictonary with all channels sorted by type
    :param category_ids: List with IDS of categorys to check if channels are in
    :param inverted: If it should return all the channels inside the category or outside it (def False)
    :param channel_type: The type of channel to return. Default TextChannel
    :return: List of channels
    """
    if type(category_ids) is not list:
        category_ids = [category_ids]
    return_channels = []
    channels = chr_dict[channel_type]
    for channel in channels:
        # print(channel.name, channel.category_id, category_ids, channel.category_id in category_ids)
        if channel.category_id in category_ids:
            return_channels.append(channel)
    if inverted:
        result = list(set(channels) - set(return_channels))
        return result
    else:
        return return_channels


# ___START_!IMMUNE
@bot.slash_command(name="immune", description="Adds a channel to the archive immunity list")
async def immune(ctx: discord.ApplicationContext):
    if ctx.author.id == 278558820752424960:
        with open("immunity.txt", "a", encoding="utf-8") as file:
            file.write(f"{ctx.channel.id}:{ctx.channel.name}\n")
        await ctx.respond(f"Added <#{ctx.channel.id}> to the archive immunity list")
    else:
        await ctx.respond("Sadly you can't make channels immune. Thats not how it works :)")


@bot.slash_command(name="revoke", description="Removes a channel to the archive immunity list")
async def revoke(ctx: discord.ApplicationContext):
    if ctx.author.id == 278558820752424960:
        with open("immunity.txt", "r", encoding="utf-8") as file:
            removed_channel = False
            keep_list = []
            for immune_channel in file.readlines():
                immune_channel_id = int(immune_channel.split(":")[0])
                if immune_channel_id == ctx.channel_id:
                    removed_channel = True
                else:
                    keep_list.append(immune_channel)
        with open("immunity.txt", "w", encoding="utf-8") as file:
            file.write("".join(keep_list))
        if removed_channel:
            await ctx.respond(f"Removed <#{ctx.channel_id}> from the archive immunity list")
        else:
            await ctx.respond(f"<#{ctx.channel.id}> was not immune so nothing happened!")
    else:
        await ctx.respond("Sadly you cannot revoke immunity. Thats not how it works :)")


def fetch_immune_channels(full=False):
    with open("immunity.txt", "r", encoding="utf-8") as file:
        if full:
            return file.readlines()
        return [line.split(":")[0] for line in file.readlines()]


# ___END_!IMMUNE

# __START_ auto archive

@bot.slash_command(name="candidates", description="Prints all the non immune channels which could be archived")
async def candidates(ctx: discord.ApplicationContext):
    immune = fetch_immune_channels()
    await ctx.respond("Calculating channel activity!")
    await ctx.channel.trigger_typing()
    chn_list = await get_channel_msg_time()
    candidates, safe = get_achive_candidates(chn_list)
    archive_string_list = []
    archivestring = "Unarchived channels which have atleast 7 days of inactivity\n\n"
    for channel in candidates:
        archivestring += f"<#{channel[1].id}> with the last message being {channel[0]} days ago.\n"
    safe.sort(key=itemgetter(0), reverse=True)
    archivestring += "\nThese channels are no candidates because they are immune or they dont have 7 days of inactivity!\n"
    for safe_chn in safe:
        if len(archivestring) + len(f"Last message: {safe_chn[0]} days ago for <#{safe_chn[1].id}>") < 1900:
            archivestring += f"Last message: {safe_chn[0]} days ago for <#{safe_chn[1].id}>"
            if str(safe_chn[1].id) in immune:
                archivestring += ":shield:\n"
            else:
                archivestring += "\n"
        else:
            archive_string_list.append(archivestring)
            archivestring = ""
    archive_string_list.append(archivestring)
    for msg in archive_string_list:
        await ctx.channel.send(msg)


async def get_channel_msg_time():
    channel_dicts = get_channel_dict(BAD_ID)
    active_channels_list = []
    unarchived_channels = get_channels_in_category(channel_dicts, [ARCHIVED, ARCHIVED_2, EXIBITION], inverted=True)
    for textchannel in unarchived_channels:
        if str(textchannel.id):  # not in fetch_immune_channels():
            active_channel = textchannel
            channel_age = await get_channel_age(textchannel)
            active_channels_list.append([channel_age, active_channel])
    return active_channels_list


def get_achive_candidates(channel_list):
    immune = fetch_immune_channels()
    candidates = []
    safe_from_archive = []
    for channel in channel_list:
        if channel[0] >= 7 and str(channel[1].id) not in immune:
            candidates.append(channel)
        else:
            safe_from_archive.append(channel)
    return candidates, safe_from_archive


async def get_channel_age(textchannel):
    try:
        msg: discord.Message = (await textchannel.history(limit=1).flatten())[0]
        created = msg.created_at
        now = datetime.datetime.utcnow()
        now, created = now.replace(tzinfo=None), created.replace(tzinfo=None)
        elapsed = now - created
        # print(f"{textchannel.name} with age: {elapsed.days}")
        return elapsed.days
    except Exception as e:
        print(e)
        return -1


async def change_category(channel: discord.TextChannel, category_id, sync_perms=True):
    category = bot.get_channel(category_id)
    await channel.edit(category=category, sync_permissions=sync_perms)


# archive 1 channel only
@bot.slash_command(name="archive", description="Archives the current channel if its not immune")
async def archive(ctx: discord.ApplicationContext):
    archive_msg = """This channel has been <#788840904412233778>!
It can be brought back with 5 votes and permission from at least two admins. 
You can request this in <#788054115955245056>
"""
    if ctx.author.guild_permissions.administrator:
        if str(ctx.channel_id) not in fetch_immune_channels():
            await change_category(ctx.channel, ARCHIVED_2)
            await ctx.channel.send(archive_msg)
            await ctx.respond("Archiving channel!", ephemeral=True)
        else:
            await ctx.respond("This channel is immune. And cannot be archived automatically!", ephemeral=True)
    else:
        await ctx.respond("You cannot archive channels since you are not an admin!", ephemeral=True)


# __END_archive
@bot.slash_command(name="status", description="Change bot status")
async def status(ctx: discord.ApplicationContext,
                 type: Option(str, name="type",
                              choices=["Playing", "Streaming", "Watching", "Listening", "Competing", "Disable"]),
                 msg: Option(str, name="message", description="The message to display")):
    activity = discord.ActivityType.unknown
    match type:
        case "Playing":
            activity = discord.ActivityType.playing
        case "Streaming":
            activity = discord.ActivityType.streaming
        case "Listening":
            activity = discord.ActivityType.listening
        case "Watching":
            activity = discord.ActivityType.watching
        case "Competing":
            activity = discord.ActivityType.competing
        case "Disable":
            activity = discord.ActivityType.unknown
    await bot.change_presence(
        activity=discord.Activity(type=activity, name=msg))
    await ctx.respond(f"Successfully changed status to `{activity.name} {msg}`")


@bot.slash_command(name="echo", description="Send a message coming from the bot in a specific channel")
async def echo(ctx: discord.ApplicationContext,
               channel: Option(input_type=discord.TextChannel, name="channel",
                               description="The channel to send the message in"),
               msg: Option(str, name="message", description="Message to send")):
    if ctx.author.guild_permissions.administrator:
        channel_id = int(channel.lstrip("<#").rstrip(">"))
        channel_obj: discord.TextChannel = bot.get_guild(ctx.guild_id).get_channel(channel_id)
        await channel_obj.send(msg)
        await ctx.respond(f"Succesfully send {msg} in <#{channel_id}>", ephemeral=True)
    else:
        await ctx.respond(f"You do not have the permissions for this", ephemeral=True)


# MOTH

def get_possible_motw():
    server = bot.get_guild(BAD_ID)
    eligable = []
    for member in server.members:
        if member.get_role(motw_participant) and not member.get_role(motw_role):
            eligable.append(member)
    return random.choice(eligable)


async def get_time_since_last_own_msg():
    server_not: discord.TextChannel = bot.get_guild(BAD_ID).get_channel(server_notif)
    history = await server_not.history(limit=100).flatten()
    last_own_msg = None
    for msg in history:
        if msg.author == bot.user:
            last_own_msg = msg
            break
    if last_own_msg:
        created = last_own_msg.created_at
        now = datetime.datetime.utcnow()
        now, created = now.replace(tzinfo=None), created.replace(tzinfo=None)
        elapsed = now - created
    else:
        return 100
    return elapsed.days


async def change_motw(force=False):
    day_of_week = datetime.datetime.today().weekday()
    if day_of_week == 0 and await get_time_since_last_own_msg() > 3 or force:  # Monday
        BG = bot.get_guild(BAD_ID)
        server_not: discord.TextChannel = BG.get_channel(server_notif)
        new_motw: discord.user = get_possible_motw()
        motw_role_obj = BG.get_role(motw_role)
        for member in motw_role_obj.members:
            await member.remove_roles(motw_role_obj)
        await new_motw.add_roles(motw_role_obj)
        MOTW_MESSAGE = f"""Another week has begun that means that <@{new_motw.id}> is our new <@&{motw_role}>!
This week <#985226350505898054> is dedicated to <@{new_motw.id}>. Say something nice about them here!
<@&{motw_participant}>
"""
        await server_not.send(MOTW_MESSAGE)
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing,
                                      name=f"{new_motw.display_name} is our new member of the week!"))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    LOG = bot.get_guild(DOG_ID).get_channel(arch_start)
    await LOG.send(f'{bot.user} started at {datetime.datetime.now().strftime("%H:%M:%S")}')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="for inactive channels!"))
    # await change_motw()


def check_for_gif(message: discord.Message):
    valid = False
    if len(message.attachments) > 0:
        if "gif" in message.attachments[0].url:
            valid = True
    if len(message.embeds) > 0:
        if "gif" in message.embeds[0].url:
            valid = True
    if 'https://' in message.content and 'gif' in message.content:
        valid = True
    return valid


@bot.slash_command(name="dm", description="Send a direct message through the bot")
async def dm(ctx: discord.ApplicationContext,
             user: Option(discord.Member, input_type=discord.Member, name="member", required=True),
             message: Option(str, "message", required=True)):
    if ctx.author.guild_permissions.administrator:
        try:
            await user.send(message)
        except Exception as e:
            await ctx.respond(f"Failed to send dm\n {str(e)}", ephemeral=True)
        else:
            await ctx.respond(f"Successfully send dm to <@{user.id}>! With message: {message}", ephemeral=True)


@bot.slash_command(name="shutdown",
                   description="Kills the python proccess which keeps the bot alive. Needs a manual restart")
async def restart_bot(ctx: discord.ApplicationContext):
    if ctx.author.id == 278558820752424960:
        await ctx.respond(f"Shutting down <@{bot.user.id}>")
        exit()
    else:
        await ctx.respond("Only the bot author can shutdown the bot!")


def td_format(seconds):
    seconds = int(seconds)
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def calculate_age(created):
    now = datetime.datetime.utcnow()
    now, created = now.replace(tzinfo=None), created.replace(tzinfo=None)
    elapsed = now - created
    total_sec = elapsed.total_seconds()
    duration_string = td_format(total_sec)
    creation_date_string = created.strftime("%d %B %Y at %H:%M:%S")
    return creation_date_string, duration_string


@bot.slash_command(name="server_age", description="Display the age of the server!")
async def server_age(ctx: discord.ApplicationContext):
    server: discord.guild = bot.get_guild(ctx.guild_id)
    created = server.created_at
    cds, ds = calculate_age(created)
    to_send = f"""This server has been created on {cds}.
This means that the server has an age of {ds}"""
    await ctx.respond(to_send)


@bot.slash_command(name="account_age", description="Display the age of the supplied account!")
async def account_age(ctx: discord.ApplicationContext,
                      user: Option(discord.Member, input_type=discord.Member, name="member", required=True)):
    cds, ds = calculate_age(user.created_at)
    to_send = f"""The account of <@{user.id}> has been created on {cds}.
That gives it an age of {ds}"""
    await ctx.respond(to_send)


@bot.slash_command(name="ping", description="Gets the latency of the bot")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! `{bot.latency:.4f}` seconds")


@bot.event
async def on_message(message):
    if message.author != bot.user:
        pass
        # if msgc =  = '!candidates' and message.channel.id == 785626495837405205: await candidates(message)

        # if msgc == '!force_motw': await change_motw(
        #    True) if message.author.guild_permissions.administrator else await no_perms(message)
        # if message.author.id == 1000529572644798494 and message.author.bot is True:
        #    await change_motw()
        # if msgc == "!restart": await restart_bot(message)
        # if msgc == "!print_immune": await message.channel.send(fetch_immune_channels(full=True))


async def no_perms(message):
    await message.channel.send(
        f"Im sorry <@{message.author.id}> but you dont have the permissions to use this command!")


def message_persistance(channel_id,msgstring ,deletion=False):
    global EDIT_DICT, DELETION_DICT
    active_dict = EDIT_DICT
    if deletion:
        active_dict = DELETION_DICT
    if channel_id not in active_dict:
        active_dict[channel_id] = [msgstring]
    elif channel_id in active_dict:
        if len(active_dict[channel_id]) > 10:
            del active_dict[channel_id][0]
        active_dict[channel_id].append(msgstring)


@bot.slash_command(name="edits",description="Gets the most recent edits in the current channel")
async def get_edits(ctx: discord.ApplicationContext,
                    edit_num: Option(input_type=str,name="display_num",description="Number of edits to display (max 10)",required=True,choices=list(map(str,range(1,11)))),
                    silent: Option(input_type=bool,name="silent",description="Should the result be returned silently",default=False,choices=["True","False"])):
    if ctx.author.guild_permissions.administrator:
        if ctx.channel_id in EDIT_DICT:
            edit_list = EDIT_DICT[ctx.channel_id]
            edit_num = int(edit_num)
            if edit_num > len(edit_list):
                edit_num = len(edit_list)
            edit_msg = ""
            for msg in edit_list[len(edit_list)-edit_num:]:
                edit_msg += f"{msg}\n"
            await ctx.respond(edit_msg, ephemeral=silent)
        else:
            await ctx.respond("There are no recent edits in this channel", ephemeral=silent)
    else:
        await ctx.respond("Only admins can use this command",ephemeral=silent)


@bot.slash_command(name="deletions",description="Gets the most recent deletions in the current channel")
async def get_deletions(ctx: discord.ApplicationContext,
                    del_num: Option(input_type=str,name="display_num",description="Number of deletions to display (max 10)",required=True,choices=list(map(str,range(1,11)))),
                    silent: Option(input_type=bool,name="silent",description="Should the result be returned silently",default=False,choices=["True","False"])):
    if ctx.author.guild_permissions.administrator:
        if ctx.channel_id in DELETION_DICT:
            del_list = DELETION_DICT[ctx.channel_id]
            del_num = int(del_num)
            if del_num > len(del_list):
                del_num = len(del_list)
            del_msg = ""
            for msg in del_list[len(del_list)-del_num:]:
                del_msg += f"{msg}\n"
            await ctx.respond(del_msg, ephemeral=silent)
        else:
            await ctx.respond("There are no recent edits in this channel", ephemeral=silent)
    else:
        await ctx.respond("Only admins can use this command",ephemeral=silent)


@bot.event
async def on_message_edit(msg_b: discord.Message, msg_a: discord.Message):
    if not check_for_gif(msg_a):
        now = datetime.datetime.now()
        LOG = bot.get_guild(DOG_ID).get_channel(arch_edit)
        notice = f"`{msg_b.author} | {msg_a.channel}` {msg_b.content} `->` {msg_a.content}"
        save_notice = f"`{now.strftime('%d/%m/%Y, %H:%M:%S')}| {msg_b.author}` {msg_b.content} `->` {msg_a.content}"
        message_persistance(msg_b.channel.id,save_notice,deletion=False)
        await LOG.send(notice)
        print(notice)


@bot.event
async def on_message_delete(msg):
    now = datetime.datetime.now()
    LOG = bot.get_guild(DOG_ID).get_channel(arch_del)
    notice = f"`{msg.author} | {msg.channel}  deleted:` {msg.content}"
    save_notice = f"`{now.strftime('%d/%m/%Y: %H:%M:%S')}| {msg.author} deleted:` {msg.content}"
    message_persistance(msg.channel.id, save_notice, deletion=True)
    await LOG.send(notice)
    print(notice)


bot.run(os.environ.get("BOT_TOKEN"))
