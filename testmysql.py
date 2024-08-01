import db_model.dbConnection as db
with open('controlip','r') as re:
    onlyipaddress = re.read().strip()
door_lock = db.dbConnect("select door_lock from doorsetting where wiegand = %s" ,('uart1',),onlyipaddress)
print(door_lock)
if type(door_lock[0][0]) is type(None):
    print("1")
print(type(door_lock[0][0]))