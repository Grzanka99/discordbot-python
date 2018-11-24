import mysql.connector
from data.data import datab

con = object

try:
    mydb = mysql.connector.connect(
        host=datab['host'],
        user=datab['user'],
        passwd=datab['password'],
        database=datab['database']
    )
    con = mydb.cursor()
except Exception as err:
    print(err)


def mysqlQuery(query):
    con.execute(query)
    return con.fetchall()


def mysqlExecute(query):
    con.execute(query)
    mydb.commit()
