import mysql.connector as mysql
def dbConnect(sqlCommand,params1,hostip):
    db = mysql.connect(
    host = hostip,
    user = "root",
    passwd = "1qaz@WSX",
    database = "DoorSecurity",
    port = "13306"
    )
    ConnectDB = db.cursor()
    ConnectDB.execute(sqlCommand,params1)
    ConnectDB_result = ConnectDB.fetchall()
    return ConnectDB_result