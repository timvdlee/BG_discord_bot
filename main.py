import discord
from os import environ


class Archivator(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


client = Archivator()
client.run(environ.get("BOT_TOKEN"))


def main():
    pass


if __name__ == '__main__':
    main()
