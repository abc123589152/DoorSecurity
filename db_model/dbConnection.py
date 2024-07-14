import mysql.connector as mysql
def dbConnect(sqlCommand,params1,hostip):
    ConnectDBlist = []
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
    for result in ConnectDB_result:
        ConnectDBlist.append(result)
    return ConnectDBlist