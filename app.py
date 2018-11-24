import discord
from discord.ext import commands
import functions as fn
from voiceTime import voiceTime
from data.data import token
from connection import mysqlExecute

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


@client.event
async def on_voice_state_update(before, after):
    await voiceTime(before, after, client)


client.run(token)
