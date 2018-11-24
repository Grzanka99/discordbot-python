from connection import mysqlExecute, mysqlQuery
from time import gmtime, strftime


def gCT():
    return strftime("%Y.%m.%d@%H:%M:%S#", gmtime())


def log(msg, serverID="err"):
    out = "{} {}".format(gCT(), msg)
    print(out)
    mysqlExecute("INSERT INTO logs_{} (log) VALUES ('{}')".format(serverID, out))
