from connection import mysqlQuery
from math import floor


def getCommands():
    res = mysqlQuery("SELECT * FROM commands ORDER BY cmd_name")
    return res


def getTime(userID, serverID):
    if ifExist(userID, serverID):
        return userTime(userID, serverID)
    else:
        return 0


def ifExist(userID, serverID):
    try:
        res = mysqlQuery("SELECT * FROM server_{} WHERE user_id = {}".format(serverID, userID))
        if len(res) > 0:
            return True
        else:
            return False
    except Exception as err:
        print(err)
        return False


def userTime(userID, serverID):
    res = mysqlQuery("SELECT time FROM server_{} WHERE user_id = {}".format(serverID, userID))
    return res[0][0]


def convertTime(time):
    timeResult = ""
    seconds: float
    minutes: float
    hours: float
    days: float

    #sekundy
    if time > 60: seconds = time % 60
    else: seconds = time
    #minuty
    if time > 60: minutes = floor(time / 60)
    else: minutes = -1
    #godziny
    if minutes > 60: hours = floor(minutes / 60)
    else: hours = -1
    #minuty
    if minutes > 60: minutes = minutes % 60
    else: minutes = minutes

    if hours != -1: timeResult = "{} hours ".format(hours)
    if minutes != -1: timeResult += "{} minutes ".format(minutes)
    timeResult += "{} seconds".format(seconds)

    if hours > 24:
        timeResult += ". It means: "

        days = floor(hours / 24)
        hours = hours % 24

        timeResult += "{} days ".format(days)
        timeResult += "{} hours ".format(hours)
        timeResult += "{} minutes ".format(minutes)
        timeResult += "{} seconds ".format(seconds)

    return timeResult
