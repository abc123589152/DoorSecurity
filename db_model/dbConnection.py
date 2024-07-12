import mysql.connector as mysql
def dbConnect(sqlCommand,params1):
    ConnectDBlist = []
    db = mysql.connect(
    host = "192.168.1.186",
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