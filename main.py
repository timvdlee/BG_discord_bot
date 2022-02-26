import discord
import os
import datetime
from operator import itemgetter

BAD_ID = 754374401830551552
DOG_ID = 424883648349601793

ARCHIVED = 788839782901219338
EXIBITION = 943101926155902977
MY_DOG_TESTCAT = 424883648349601796

BOT_CMDS = 785626495837405205

intents = discord.Intents(messages=True, guilds=True, message_content=True)

client = discord.Client(intents=intents)


def add_channel_immunity(channel):
    with open("immunity.txt", "a", encoding="utf-8") as file:
        file.write(f"{channel.id}:{channel.name}\n")


async def change_category(channel: discord.TextChannel, category_id):
    category = client.get_channel(category_id)
    await channel.edit(category=category, sync_permissions=True)


def fetch_immune_channels():
    with open("immunity.txt", "r", encoding="utf-8") as file:
        return [line.split(":")[0] for line in file.readlines()]


def get_channel_dict(g_id):
    server = client.get_guild(g_id)
    channel_dicts = {}
    for channel in server.channels:
        if channel.type not in channel_dicts:
            channel_dicts[channel.type] = [channel]
        else:
            channel_dicts[channel.type].append(channel)
    return channel_dicts


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
        #print(f"{textchannel.name} with age: {elapsed.days}")
        return elapsed.days
    except Exception as e:
        print(e)
        return -1


async def get_channel_msg_time():
    channel_dicts = get_channel_dict(BAD_ID)
    active_channels_list = []
    for textchannel in channel_dicts[discord.ChannelType.text]:
        if textchannel.category_id != ARCHIVED and \
                textchannel.category_id != EXIBITION and str(textchannel.id) not in fetch_immune_channels():
            active_channel = textchannel
            channel_age = await get_channel_age(textchannel)
            active_channels_list.append([channel_age, active_channel])
    return active_channels_list


async def archive_channels():
    chn_list = await get_channel_msg_time()
    candidates = get_achive_candidates(chn_list)
    for channel in candidates:
        print(f"Candidate for archive {channel[1].name} with last message being {channel[0]} days ago")
        #await change_category(channel[1],MY_DOG_TESTCAT)



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for inactive channels!"))
    await archive_channels()


@client.event
async def on_message(message):
    if message.author != client.user:
        if message.author.id == 278558820752424960 and message.content == "!immune":
            add_channel_immunity(message.channel)
            await message.channel.send(f"Added <#{message.channel.id}> to the archive immunity list")


@client.event
async def on_message_edit(msg_b, msg_a):
    print(f"Message by {msg_b.author} edited from {msg_b.content} to {msg_a.content}")


client.run(os.environ.get("BOT_TOKEN"))
