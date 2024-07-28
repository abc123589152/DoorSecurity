import mysql.connector as mysql
def dbConnect(sqlCommand,params1,hostip):
    db = mysql.connect(
    host = hostip,
    user = "your mysql username",
    passwd = "mysql password",
    database = "DoorSecurity",#DataBase Name
    port = "13306"
    )
    ConnectDB = db.cursor()
    ConnectDB.execute(sqlCommand,params1)
    ConnectDB_result = ConnectDB.fetchall()
    return ConnectDB_result
