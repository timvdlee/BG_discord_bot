import discord
import os
import datetime
import random

from discord.ext.commands import has_permissions
from operator import itemgetter

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

intents = discord.Intents(messages=True, guilds=True, members=True)
print("IF NOT RESPONDING ADD message_content=True to intents (only after august 1st)")

client = discord.Client(intents=intents)


#  START_GENERAL_USE


def get_channel_dict(g_id):
    """
    Gets all channels and punts them in a dictonary based on type
    :param g_id: The id of the server it should fetch the channels from
    :return: Channel dict
    """
    server = client.get_guild(g_id)
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
async def add_channel_immunity(channel, a_id):
    if a_id == 278558820752424960:
        with open("immunity.txt", "a", encoding="utf-8") as file:
            file.write(f"{channel.id}:{channel.name}\n")
        await channel.send(f"Added <#{channel.id}> to the archive immunity list")
    else:
        await channel.send("Sadly you can't make channels immune. Thats not how it works :)")


def fetch_immune_channels():
    with open("immunity.txt", "r", encoding="utf-8") as file:
        return [line.split(":")[0] for line in file.readlines()]


# ___END_!IMMUNE

# __START_ auto archive
async def get_candidates(message):
    immune = fetch_immune_channels()
    await message.channel.trigger_typing()
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
        await message.channel.send(msg)


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
    category = client.get_channel(category_id)
    await channel.edit(category=category, sync_permissions=sync_perms)


# archive 1 channel only
@has_permissions(administrator=True)
async def archive_channel(message: discord.Message):
    archive_msg = """This channel has been <#788840904412233778>!
It can be brought back with 5 votes and permission from at least two admins. 
You can request this in <#788054115955245056>
"""
    if str(message.channel.id) not in fetch_immune_channels():
        await change_category(message.channel, ARCHIVED_2)
        await message.channel.send(archive_msg)
        await message.delete()
    else:
        await message.channel.send("This channel is immune. And cannot be archived automatically!")


# __END_archive

async def change_bot_status(message):
    try:
        msglist = message.content.split(" ")
        del msglist[0]
        type = msglist.pop(0)
        name = " ".join(msglist)
        activity = None
        match type:
            case "p":
                activity = discord.ActivityType.playing
            case "s":
                activity = discord.ActivityType.streaming
            case "l":
                activity = discord.ActivityType.listening
            case "w":
                activity = discord.ActivityType.watching
        await client.change_presence(
            activity=discord.Activity(type=activity, name=name))
        await message.channel.send(f"Successfully changed status to `{activity.name} {name}`")
    except:
        errormsg = """```
Incorrect syntax use 
!status type message
types:
p = playing
s = streaming
l = listening
w = watching
    
Example: !status p Among Us!
```"""
        await message.channel.send(errormsg)


@has_permissions(administrator=True)
async def send_msg_in_channels(message: discord.Message):
    try:
        msglist = message.content.split(" ")
        del msglist[0]
        target = int(msglist.pop(0).lstrip("<#").rstrip(">"))
        channel: discord.channel = message.guild.get_channel(target)
        msg_to_send = " ".join(msglist)
        if channel.type == discord.ChannelType.category:
            channels = get_channels_in_category(get_channel_dict(message.guild.id), channel.id)
        else:
            channels = [channel]
        for channel in channels:
            await channel.send(msg_to_send)
            await message.delete()
    except Exception as e:
        print(e)
        errormsg = """```
Incorrect syntax use 
!send-message-in target message
target should be either a channel 
Or a category ID!
Example: !send-message-in channel Hello!
            ```"""
        await message.channel.send(errormsg)


# MOTH

def get_possible_motw():
    server = client.get_guild(BAD_ID)
    eligable = []
    for member in server.members:
        if member.get_role(motw_participant) and not member.get_role(motw_role):
            eligable.append(member)
    return random.choice(eligable)


async def get_time_since_last_own_msg():
    server_not: discord.TextChannel = client.get_guild(BAD_ID).get_channel(server_notif)
    history = await server_not.history(limit=100).flatten()
    last_own_msg = None
    for msg in history:
        if msg.author == client.user:
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
        BG = client.get_guild(BAD_ID)
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
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name=f"{new_motw.display_name} is our new member of the week!"))


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    LOG = client.get_guild(DOG_ID).get_channel(arch_start)
    await LOG.send(f'{client.user} started at {datetime.datetime.now().strftime("%H:%M:%S")}')
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="for inactive channels!"))
    #await change_motw()


async def gif_only(message: discord.Message):

    if str(datetime.date.today())[5:] == '06-15' and message.channel.id != gaming_talk:
        datetime.datetime.astime
        valid = False
        if len(message.attachments) > 0:
            if "gif" in message.attachments[0].url:
                valid = True
        if len(message.embeds) > 0:
            if "gif" in message.embeds[0].url:
                valid = True
        if 'https://' in message.content and 'gif' in message.content:
            valid = True
        if not valid:
            await message.channel.send("https://tenor.com/view/today-gif-only-gif-gif-only-today-gif-25305650")


@client.event
async def on_message(message):
    if message.author != client.user:
        msgc: str = message.content
        if msgc == '!immune': await add_channel_immunity(message.channel, message.author.id)
        if msgc.startswith("!status"): await change_bot_status(message)
        if msgc.startswith("!echo"): await send_msg_in_channels(
            message) if message.author.guild_permissions.administrator else await no_perms(message)
        if msgc == '!archive': await archive_channel(
            message) if message.author.guild_permissions.administrator else await no_perms(message)
        if msgc == '!candidates' and message.channel.id == 785626495837405205: await get_candidates(message)
        if msgc == '!force_motw': await change_motw(
            True) if message.author.guild_permissions.administrator else await no_perms(message)
        if message.author.id == 1000529572644798494 and message.author.bot is True:
            await change_motw()


async def no_perms(message):
    await message.channel.send(
        f"Im sorry <@{message.author.id}> but you dont have the permissions to use this command!")


@client.event
async def on_message_edit(msg_b, msg_a):
    LOG = client.get_guild(DOG_ID).get_channel(arch_edit)
    notice = f"{msg_b.author} edited from {msg_a.channel}: {msg_b.content} to: {msg_a.content}"
    await LOG.send(notice)
    print(notice)


@client.event
async def on_message_delete(msg):
    LOG = client.get_guild(DOG_ID).get_channel(arch_del)
    notice = f"{msg.author} deleted: {msg.content} | from {msg.channel}"
    await LOG.send(notice)
    print(notice)


client.run(os.environ.get("BOT_TOKEN"))
