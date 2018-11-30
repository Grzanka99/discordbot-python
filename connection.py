import mysql.connector
from data.data import datab

con = object


def mysqlQuery(query):
    try:
        mydb = mysql.connector.connect(
            host=datab['host'],
            user=datab['user'],
            passwd=datab['password'],
            database=datab['database']
        )
        con = mydb.cursor()
        con.execute(query)
        res = con.fetchall()
        con.close()
        return res
    except Exception as err:
        print(err)
        return


def mysqlExecute(query):
    try:
        mydb = mysql.connector.connect(
            host=datab['host'],
            user=datab['user'],
            passwd=datab['password'],
            database=datab['database']
        )
        con = mydb.cursor()
        con.execute(query)
        mydb.commit()
        con.close()
        return
    except Exception as err:
        print(err)
        return
