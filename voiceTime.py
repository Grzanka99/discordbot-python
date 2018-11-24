from connection import mysqlExecute
from functions import ifExist, userTime
from time import time
from logger import log
import os
from data.data import czas as timeToRole
from discord.utils import get


async def voiceTime(before, after, client):
    oldUserChannel = before.voice.voice_channel
    newUserChannel = after.voice.voice_channel
    username = after.name
    userID = after.id
    serverID = after.server.id
    oldTimeOnline = int

    try:
        oldTimeOnline = userTime(userID, serverID)
    except Exception as err:
        oldTimeOnline = 0

    if oldUserChannel is None and newUserChannel is not None:
        log('User: {} join to {}'.format(username, newUserChannel.name), serverID)
        if ifExist(userID, serverID):
            joinTime(userID)
        else:
            log("Doesnt exist. Creating user in database", serverID)
            mysqlExecute("INSERT INTO server_{} (user_id, time) VALUES ({}, 0)".format(serverID, userID))
            joinTime(userID)
    elif newUserChannel is None:
        log("User: {} left from {}".format(username, oldUserChannel.name), serverID)
        try:
            countTime(userID, serverID)
            await checkRole(userID, oldTimeOnline, before, client, serverID)
        except Exception as err:
            print(err)


def joinTime(id):
    now = str(int(time()))
    with open("users/{}.txt".format(id), "w+") as file:
        file.write(now)


def countTime(id, serverID):
    file = open("users/{}.txt".format(id))
    now = int(time())
    read = int(file.read())
    online = now - read
    addTime(online, id, serverID)
    file.close()
    os.unlink("users/{}.txt".format(id))


def addTime(time, id, serverID):
    onlineTime = userTime(id, serverID)
    onlineTime += time
    mysqlExecute("UPDATE server_{} SET time = {} WHERE user_id = {}".format(serverID, onlineTime, id))


async def checkRole(id, oldTime, member, client, serverID):
    onlineTime = userTime(id, serverID)
    if onlineTime >= timeToRole and not hasRole(member):
        rola = get(member.server.roles, name="User")
        await client.add_roles(member, rola)
        if oldTime < timeToRole:
            log("{} is now an active user".format(member.name), serverID)


def hasRole(member):
    if "User" in member.server.roles:
        return True
    else:
        return False
