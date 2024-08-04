from db_model.dbConnection import dbConnect
class reedswitchClass:
    def __init__(self,uartport,controlip):
        self.uartport = uartport
        self.controlip = controlip
        
    def getnewpin(self):
        reedswitchpin_noconvert = dbConnect("select door_sensor from doorsetting where wiegand = %s and control = %s", (self.uartport,self.controlip,), self.controlip)
        if reedswitchpin_noconvert[0][0]!='':
            return int(reedswitchpin_noconvert[0][0])
        else:
            return 0