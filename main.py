import discord
import os
import datetime

from discord.ext.commands import has_permissions

BAD_ID = 754374401830551552
DOG_ID = 424883648349601793

ARCHIVED = 788839782901219338
EXIBITION = 943101926155902977
MY_DOG_TESTCAT = 424883648349601796

BOT_CMDS = 785626495837405205

intents = discord.Intents(messages=True, guilds=True, message_content=True)

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
        print(channel.name,channel.category_id, category_ids, channel.category_id in category_ids)
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
    await message.channel.trigger_typing()
    chn_list = await get_channel_msg_time()
    candidates = get_achive_candidates(chn_list)
    archivestring = "Unarchived channels which have atleast 7 days of inactivity\nWhich are candidates for archivation:\n\n"
    for channel in candidates:
        archivestring += f"<#{channel[1].id}> with the last message being {channel[0]} days ago.\n"
    await message.channel.send(archivestring)


async def get_channel_msg_time():
    channel_dicts = get_channel_dict(BAD_ID)
    active_channels_list = []
    unarchived_channels = get_channels_in_category(channel_dicts, [ARCHIVED, EXIBITION], inverted=True)
    for textchannel in unarchived_channels:
        if str(textchannel.id) not in fetch_immune_channels():
            active_channel = textchannel
            channel_age = await get_channel_age(textchannel)
            active_channels_list.append([channel_age, active_channel])
    return active_channels_list


def get_achive_candidates(channel_list):
    candidates = []
    for channel in channel_list:
        if channel[0] >= 7:
            candidates.append(channel)
    return candidates


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

#archive 1 channel only
@has_permissions(administrator=True)
async def archive_channel(message: discord.Message):
    archive_msg = """This channel has been <#788840904412233778>!
It can be brought back with 5 votes and permission from at least two admins. 
You can request this in <#788054115955245056>
"""
    await change_category(message.channel, ARCHIVED)
    await message.channel.send(archive_msg)
    await message.delete()

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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="for inactive channels!"))


@client.event
async def on_message(message):
    if message.author != client.user:
        msgc: str = message.content
        if msgc == '!immune': add_channel_immunity(message.channel, message.author.id)
        if msgc.startswith("!status"): await change_bot_status(message)
        if msgc.startswith("!send-message-in"): await send_msg_in_channels(message)
        if msgc == '!archive': await archive_channel(message)
        if msgc == '!candidates': await get_candidates(message)


@client.event
async def on_message_edit(msg_b, msg_a):
    print(f"Message by {msg_b.author} edited from {msg_b.content} to {msg_a.content}")


client.run(os.environ.get("BOT_TOKEN"))
