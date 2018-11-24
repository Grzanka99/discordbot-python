import discord
import youtube_dl
from discord.ext import commands
import functions as fn
from voiceTime import voiceTime
from data.data import token
from connection import mysqlExecute
from logger import log

client = commands.Bot(command_prefix='?')
client.remove_command('help')


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Bot Admin, say ?help"))
    print('I am ready!')
    for server in client.servers:
        mysqlExecute("CREATE TABLE IF NOT EXISTS server_{} LIKE users".format(server.id))
        mysqlExecute("CREATE TABLE IF NOT EXISTS server_err LIKE users")
        mysqlExecute("CREATE TABLE IF NOT EXISTS logs_{} (id INT PRIMARY KEY AUTO_INCREMENT, log TEXT)".format(server.id))
        mysqlExecute("CREATE TABLE IF NOT EXISTS logs_{} (id INT PRIMARY KEY AUTO_INCREMENT, log TEXT)".format("err"))


@client.event
async def on_voice_state_update(before, after):
    await voiceTime(before, after, client)


@client.event
async def on_server_join(server):
    log("Joined to new server: {}".format(server.name))
    mysqlExecute("CREATE TABLE IF NOT EXISTS server_{} LIKE users".format(server.id))
    mysqlExecute("CREATE TABLE IF NOT EXISTS logs_{} (id INT PRIMARY KEY AUTO_INCREMENT, log TEXT)".format(server.id))


@client.event
async def on_server_remove(server):
    log("Removed from server: {}".format(server.name))
    mysqlExecute("DROP TABLE logs_{}".format(server.id))
    mysqlExecute("DROP TABLE server_{}".format(server.id))


#Bazowe komendy


@client.command(pass_context=True)
async def id(ctx):
    id = ctx.message.author.id
    username = ctx.message.author.mention
    await client.say("{} Your ID is {}".format(username, id))


@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    cmds = fn.getCommands()
    embed = discord.Embed(
        colour=discord.Colour.green()
    )
    embed.set_author(name="Available Commands")
    for line in cmds:
        embed.add_field(name=line[1], value=line[2], inline=False)
    await client.say("{}".format(author.mention), embed=embed)


@client.command(pass_context=True)
async def time(ctx):
    author = ctx.message.author
    onlineTime = fn.getTime(author.id, author.server.id)
    if onlineTime != 0:
        await client.say("{} Your time on voice channel is {}".format(author.mention, fn.convertTime(onlineTime)))
    else:
        await client.say("{} Your time on voice channel is 0 seconds".format(author.mention))


@client.command(pass_context=True)
async def clear(ctx, amount = 50):
    author = ctx.message.author.mention
    if ctx.message.author.server_permissions.administrator:
        amount = int(amount) + 1
        if amount > 100:
            if amount == 101:
                amount = amount - 1
            elif amount != 100:
                await client.say("{} I can delete max 100 items!".format(author))
                return
        channel = ctx.message.channel
        messages = []
        async for message in client.logs_from(channel, limit=amount):
            messages.append(message)
        await client.delete_messages(messages)
    else:
        await client.say("{} You have no permission!".format(author))


#Komendy związane z czatem głosowym


players = {}
queues = {}


def checkQueue(id):
    if queues[id] is not []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()


@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    if channel is None:
        await client.say("{} You must join to any channel first".format(ctx.message.author.mention))
    else:
        await client.join_voice_channel(channel)


@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voiceClient = client.voice_client_in(server)
    await voiceClient.disconnect()


#KOMENDA PLAY


@client.command(pass_context=True)
async def play(ctx, url=None):
    mention = ctx.message.author.mention
    if url is None:
        await client.say("{} Please use ?play <url>".format(mention))
        return
    server = ctx.message.server

    try:
        voiceClient = client.voice_client_in(server)
        if voiceClient is None:
            channel = ctx.message.author.voice.voice_channel
            if channel is None:
                await client.say("{} You must join to any channel first".format(mention))
                return
            else:
                await client.join_voice_channel(channel)
                voiceClient = client.voice_client_in(server)

        if server.id in players:
            newVoiceClient = client.voice_client_in(server)
            newPlayer = await newVoiceClient.create_ytdl_player(url, after=lambda: checkQueue(server.id))

            if server.id in queues:
                queues[server.id].append(newPlayer)
            else:
                queues[server.id] = [newPlayer]
            await client.say('{} Video queued'.format(mention))
            return

        player = await voiceClient.create_ytdl_player(url, after=lambda: checkQueue(server.id))
        players[server.id] = player
        player.start()

    except youtube_dl.utils.DownloadError as err:
        msg = "{} Error: '{}' is not a valid URL".format(mention, url)
        await client.send_message(ctx.message.channel, msg)


@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    try: players[id].pause()
    except Exception: return


@client.command(pass_context=True)
async def stop(ctx):
    server = ctx.message.server
    if server.id in queues:
        queues.pop(server.id)
    if server.id in players:
        players[server.id].stop()
        players.pop(server.id)
    voiceClient = client.voice_client_in(server)
    await voiceClient.disconnect()


@client.command(pass_context=True)
async def skip(ctx):
    server = ctx.message.server
    try:
        players[server.id].stop()
        client.say("Video skipped")
    except Exception: return


@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    try: players[id].resume()
    except Exception: return


client.run(token)
