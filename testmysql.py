import db_model.dbConnection as db
door_lock = db.dbConnect("select door_lock from doorsetting where weigand = %s" ,('uart1',),'192.168.1.186')
print(door_lock)
if type(door_lock[0][0]) is type(None):
    print("1")
print(type(door_lock[0][0]))