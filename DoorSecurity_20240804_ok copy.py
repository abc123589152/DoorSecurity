import serial
import time
import os
import threading
import gpiozero
from gpiozero import event
import db_model.dbConnection as db
from db_model.dbConnection_new import dbConnect
from mysql.connector import Error
from db_model.dbconnect_query import dbConnect_query
from db_model.get_now_time import get_now_date_time
from doorsensor.reedSwitch_model import reedswitchClass
# Arduino AMA port
CheckPermition_uart1 = False
CheckPermition_uart2 = False
CheckPermition_uart3 = False
CheckPermition_uart4 = False
set_input_switch_uart1 = 0
set_input_switch_uart2 = 0
set_input_switch_uart3 = 0
set_input_switch_uart4 = 0
readCount_uart1 = 0
readCount_uart2 = 0
readCount_uart3 = 0
readCount_uart4 = 0
reedswitchCount_uart1 = 0
reedswitchCount_uart4 = 0
#Card Reader port
uart1_dev = "/dev/ttyAMA0"
uart2_dev = "/dev/ttyAMA1"
uart3_dev = "/dev/ttyAMA2"
uart4_dev = "/dev/ttyAMA3"
reedswitch_uart1 = ''
reedswitch_uart2 = ''
reedswitch_uart3 = ''
reedswitch_uart4 = ''
reedswitchdict = {
    'uart1':0,
    'uart2':0,
    'uart3':0,
    'uart4':0

}
ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
onlyipaddress = ipadd.read().strip()
#Input check door status is permition open or force open
# record every port time flags and stop flags
timers = {}
stop_flags = {}
reedswitch_check_change= []
lock = threading.Lock()
stop_event =threading.Event()
#setting threading to put resest time to timer_thread function
def reset_timer(uartport,controlip):
    global stop_event
    #select database to setting reset_time
    stop_event.set()
    stop_event = threading.Event()
    resettime = db.dbConnect("select reset_time from doorsetting where control = %s and wiegand = %s",(controlip,uartport,),controlip)
    if type(resettime) is not type(None) and resettime!='':
            resettime = int(resettime[0][0])
    else:
            resettime = 5 
    # check which uartport in use
    if uartport == 'uart2':
        threading.Thread(target=timer_thread, args=(stop_event,'uart2',resettime,)).start()
    elif uartport == 'uart1':
        threading.Thread(target=timer_thread, args=(stop_event,'uart1',resettime,)).start()
    elif uartport == 'uart3':
        threading.Thread(target=timer_thread, args=(stop_event,'uart3',resettime,)).start()
    elif uartport == 'uart4':
        threading.Thread(target=timer_thread, args=(stop_event,'uart4',resettime,)).start()       
#time to Return door doo lock
def timer_thread(stop_event,uartport,resettime):
    start_time = time.time()
    global CheckPermition_uart1
    global CheckPermition_uart2
    global CheckPermition_uart3
    global CheckPermition_uart4
    while time.time() - start_time < resettime:
        if stop_event.is_set():
            return
        time.sleep(0.1)
    if uartport == 'uart2':
        global relay_uart2
        global readCount_uart2
        relay_uart2.off()
        relay_uart2.close()
        readCount_uart2 = 0
        CheckPermition_uart2 = False
        #redLed_uart2.off()
        print("Relay deactivated")
    elif uartport =='uart1':
        global relay_uart1
        global readCount_uart1
        relay_uart1.off()
        relay_uart1.close()
        readCount_uart1 = 0
        CheckPermition_uart1 = False
        #redLed_uart1.off()
        print("Relay deactivated")
    elif uartport =='uart3':
        global relay_uart3
        global readCount_uart3
        relay_uart3.off()
        relay_uart3.close()
        readCount_uart3 = 0
        CheckPermition_uart3 = False
        print("Relay deactivated")
    elif uartport =='uart4':
        global relay_uart4
        global readCount_uart4
        relay_uart4.off()
        relay_uart4.close()
        readCount_uart4 = 0
        CheckPermition_uart4 = False
        print("Relay deactivated")

# Check permition and door open status
def read_from_port(port,wiegand_uart):
    global CheckPermition_uart1
    global CheckPermition_uart2
    global CheckPermition_uart3
    global CheckPermition_uart4
    global relay_uart2_pin
    global relay_uart1_pin
    global relay_uart3_pin
    global relay_uart4_pin
    global relay_uart1
    global relay_uart2
    global relay_uart3
    global relay_uart4
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port}-({wiegand_uart})...")
        while True:
            try:
                allDoorname=[]
                data = ''
                #Get raspberry pi ip address
                ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
                onlyipaddress = ipadd.read().strip()
                #get the uart define door name 
                doorName = db.dbConnect("select door from doorsetting where wiegand = %s and control = %s" ,(wiegand_uart,onlyipaddress,),onlyipaddress)

                #Check doorname not the empty
                if doorName:
                    #check serial port has read something 
                    if ser.in_waiting > 0:
                        try:
                            #Get the arduino send message and decode
                            data = ser.readline().decode('Utf-8').strip()
                        except UnicodeDecodeError as e:
                            print(e)
                        #Check data(cardnumber) is not empty
                        if data and data!='0' or data!='1' and data!='':
                            find_card_group = ""
                            username = db.dbConnect("select username from employ where cardnumber = %s",(data,),onlyipaddress)
                             #Get the door status
                            doorstatus = db.dbConnect("select remark from doorsetting where door=%s",(doorName[0][0],),onlyipaddress)
                            #get readcard door number
                            door_lock = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", (wiegand_uart, onlyipaddress,), onlyipaddress)
                            #print(door_lock)
                            #print(wiegand_uart)
                            try:
                                print(f"cardnumber:{data}")
                                #find card number to permit groupname
                                findcardgroup = dbConnect("select doorgroup from employ where cardnumber =%s",(data,),onlyipaddress)
                                #print(findcardgroup)
                                if findcardgroup != []:
                                    if findcardgroup[0][0]!='':
                                        try:
                                            for findcard_group in findcardgroup[0]:
                                                find_card_group = findcard_group.split(',')
                                            #use groupname to find in the group doors name
                                            for get_doorgroup_name in find_card_group:
                                                find_every_door = dbConnect("select doorname from doorgroup where groupname = %s",(get_doorgroup_name,),onlyipaddress)
                                                for getalldoor in find_every_door[0]:
                                                    for every_door in getalldoor.split(','):
                                                        allDoorname.append(every_door)
                                        except IndexError as iner:
                                            print(f"IndexError message1:{iner}")
                                #find all doorgroup permit door number
                                try:
                                    #Check door is in the doogroup
                                    if doorName[0][0] in allDoorname:
                                        global readCount_uart1
                                        global readCount_uart2
                                        global readCount_uart3
                                        global readCount_uart4
                                        if wiegand_uart == 'uart2':
                                            relay_uart2_pin = int(db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart2', onlyipaddress,), onlyipaddress)[0][0])
                                            dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Permit',get_now_date_time()),onlyipaddress)
                                            if not type(relay_uart2_pin) is type(None) and relay_uart2_pin!=''and username!=[] and username!='':
                                                relay_uart2_pin = int(relay_uart2_pin)
                                                if readCount_uart2 ==0:
                                                    relay_uart2 = gpiozero.LED(relay_uart2_pin)
                                                print(f"{doorName[0][0]} Access granted")
                                                CheckPermition_uart2 = True
                                                relay_uart2.on()
                                                ser.write(b'1')
                                                readCount_uart2+=1
                                                reset_timer('uart2',onlyipaddress)
                                                #set_value_with_timeout(request, int(door_lock[0][0]), Value.ACTIVE, 5)#open the door to put GPIO 23(LINE is 23) Active
                                        elif wiegand_uart == 'uart1':
                                            relay_uart1_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart1', onlyipaddress,), onlyipaddress)[0][0]
                                            if not type(relay_uart1_pin) is type(None) and relay_uart1_pin!=''and username!=[] and username!='':
                                                relay_uart1_pin = int(relay_uart1_pin)
                                                if readCount_uart1 ==0:
                                                    relay_uart1 = gpiozero.LED(relay_uart1_pin)
                                                print(f"{doorName[0][0]} Access granted")
                                                dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Permit',get_now_date_time()),onlyipaddress)
                                                CheckPermition_uart1= True
                                                relay_uart1.on()
                                                ser.write(b'1')
                                                readCount_uart1+=1
                                                reset_timer('uart1',onlyipaddress)
                                        elif wiegand_uart == 'uart3':
                                            relay_uart3_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart3', onlyipaddress,), onlyipaddress)
                                            if relay_uart3_pin !=[]:
                                                relay_uart3_pin = relay_uart3_pin[0][0]
                                                if not type(relay_uart3_pin) is type(None) and relay_uart3_pin !='':    
                                                    relay_uart3_pin = int(relay_uart3_pin)
                                                    if readCount_uart3==0:                                                
                                                        relay_uart3 = gpiozero.LED(relay_uart3_pin)
                                                    dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Permit',get_now_date_time()),onlyipaddress)
                                                    print(f"{doorName[0][0]} Access granted")
                                                    CheckPermition_uart3 = True
                                                    relay_uart3.on()
                                                    ser.write(b'1')                                                   
                                                    readCount_uart3+=1
                                                    reset_timer('uart3',onlyipaddress)
                                        elif wiegand_uart == 'uart4':
                                            relay_uart4_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart4', onlyipaddress,), onlyipaddress)
                                            dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Permit',get_now_date_time()),onlyipaddress)
                                            if relay_uart4_pin !=[]:
                                                relay_uart4_pin = relay_uart4_pin[0][0]
                                                if not type(relay_uart4_pin) is type(None) and relay_uart4_pin !='':
                                                    relay_uart4_pin = int(relay_uart4_pin)
                                                    if readCount_uart4 == 0:
                                                        relay_uart4 = gpiozero.LED(relay_uart4_pin)
                                                    #alter relay_uart4 port 
                                                    print(f"{doorName[0][0]} Access granted")
                                                    CheckPermition_uart4 = True
                                                    relay_uart4.on()
                                                    ser.write(b'1')
                                                    readCount_uart4+=1
                                                    reset_timer('uart4',onlyipaddress)                                                  
                                    else:
                                        with lock:
                                            #print(door_lock[0][0]) 
                                            print(f"{doorName[0][0]} Access Deny")
                                            if username!=[]:
                                                dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'deny',get_now_date_time()),onlyipaddress)
                                                ser.write(b'0')
                                            else:
                                                dbConnect_query("insert into swipeCardLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",('Unknown Card',data,doorName[0][0],doorstatus[0][0],'deny',get_now_date_time()),onlyipaddress)
                                                ser.write(b'0')
                                except IndexError as iner:
                                    print(f"IndexError message2:{iner}")
                            except Error as e:
                                print(f"data base has error: {e}")
                else:
                    ser.reset_input_buffer()
                    continue
            except OSError as e:
                print(e)   
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()

def checkdoorsensor(uartport):
    #First Get reedswitch pin
    ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
    controlip = ipadd.read().strip()
    #Get reedswitch pin
    global set_input_switch_uart1
    global set_input_switch_uart2
    global set_input_switch_uart3
    global set_input_switch_uart4
    while True:
        # global CheckPermition    
        reedswitch_uart1 = reedswitchClass('uart1',controlip)
        reedswitch_uart2 = reedswitchClass('uart2',controlip)
        reedswitch_uart3 = reedswitchClass('uart3',controlip)
        reedswitch_uart4 = reedswitchClass('uart4',controlip)
        
        if uartport == 'uart1' and reedswitchdict.get('uart1')!=reedswitch_uart1.getnewpin():
            reedswitchdict['uart1'] = reedswitch_uart1.getnewpin()
            if reedswitchdict['uart1']!=0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
                    set_input_switch_uart1 = gpiozero.Button(reedswitch_uart1.getnewpin())
            elif reedswitchdict['uart1'] == 0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
        elif uartport == 'uart2' and reedswitchdict.get('uart2')!=reedswitch_uart2.getnewpin():
            reedswitchdict['uart2'] = reedswitch_uart2.getnewpin()
            if reedswitchdict['uart2']!=0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
                    set_input_switch_uart2 = gpiozero.Button(reedswitch_uart2.getnewpin())
            elif reedswitchdict['uart2'] == 0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
        elif uartport == 'uart3' and reedswitchdict.get('uart3')!=reedswitch_uart3.getnewpin():
            reedswitchdict['uart3'] = reedswitch_uart3.getnewpin()
            if reedswitchdict['uart3']!=0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
                    set_input_switch_uart3 = gpiozero.Button(reedswitch_uart3.getnewpin())
            elif reedswitchdict['uart3'] == 0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
        elif uartport == 'uart4' and reedswitchdict.get('uart4')!=reedswitch_uart4.getnewpin():
            reedswitchdict['uart4'] = reedswitch_uart4.getnewpin()
            if reedswitchdict['uart4']!=0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
                    set_input_switch_uart4 = gpiozero.Button(reedswitch_uart4.getnewpin())
            elif reedswitchdict['uart4'] == 0:
                    if "is_active=True" in str(set_input_switch_uart4):
                        set_input_switch_uart4.close()
                    elif "is_active=True" in str(set_input_switch_uart1):
                        set_input_switch_uart1.close()
                    elif "is_active=True" in str(set_input_switch_uart2):
                        set_input_switch_uart2.close()
                    elif "is_active=True" in str(set_input_switch_uart3):
                        set_input_switch_uart3.close()
        if uartport == 'uart4' and set_input_switch_uart4!=0:
            return set_input_switch_uart4
        elif uartport == 'uart1' and set_input_switch_uart1!=0:
            return set_input_switch_uart1
        elif uartport == 'uart2' and set_input_switch_uart2!=0:
            return set_input_switch_uart2
        elif uartport == 'uart3' and set_input_switch_uart3!=0:
            return set_input_switch_uart3
#The reedswitch sensor port is not open do this
def doorsensor_close(doorsensor,doorname,controlip):
    if 'is_active=True' in str(doorsensor):
        dbConnect_query("update door_status set doorstatus = %s where doorname = %s",('close',doorname),controlip)
        #print("Close door")
        time.sleep(1)
# the reedswitch sensor port is open do thiss
def doorsensor_open(doorsensor,doorname,controlip,checkpermition):
     if 'is_active=False' in str(doorsensor):
        if  checkpermition:
            #print("open door")
            dbConnect_query("update door_status set doorstatus = %s where doorname = %s",('open',doorname),controlip)
            time.sleep(1)
            return 1
        else:
            dbConnect_query("update door_status set doorstatus = %s where doorname = %s",('Force Open',doorname),controlip)
            #print("Force Open")
            time.sleep(1)
            return 0

#The uart1 reedswitch port to check door is open or closes
def doorsensor_uart1():
    global CheckPermition_uart1
    count = 0 #calculate count is 0 then is close is 1 then open s
    while True:
        #First Get reedswitch pin
        ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
        controlip = ipadd.read().strip()
        input_uart1 = checkdoorsensor('uart1')
        doorname = dbConnect("select door from doorsetting where wiegand = %s",('uart1',),controlip)
        # read status for input
        if doorname !='' and doorname!=[]: 
            doorname = doorname[0][0]
            if count == 0: 
                doorsensor_close(input_uart1,doorname,controlip)  
                count+=1
            elif count>0:
                if CheckPermition_uart1:
                    doorsensor_open(input_uart1,doorname,controlip,CheckPermition_uart1)
                    CheckPermition_uart1 = False
                    count-=1    
                else:
                    doorsensor_open(input_uart1,doorname,controlip,CheckPermition_uart1)
                    count-=1
#The uart2 reedswitch port to check door is open or closes
def doorsensor_uart2():
    global CheckPermition_uart2
    count = 0
    while True:
        #First Get reedswitch pin
        ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
        controlip = ipadd.read().strip()
        input_uart2 = checkdoorsensor('uart2')
        doorname = dbConnect("select door from doorsetting where wiegand = %s",('uart2',),controlip)
       # read status for input
        if doorname !='' and doorname!=[]: 
            doorname = doorname[0][0]
            if count == 0: 
                doorsensor_close(input_uart2,doorname,controlip)  
                count+=1
            elif count>0:
                if CheckPermition_uart2:
                    doorsensor_open(input_uart2,doorname,controlip,CheckPermition_uart2)
                    CheckPermition_uart2 = False
                    count-=1    
                else:
                    doorsensor_open(input_uart2,doorname,controlip,CheckPermition_uart2)
                    count-=1
#The uart3 reedswitch port to check door is open or closes
def doorsensor_uart3():
    global CheckPermition_uart3
    count = 0
    while True:
        #First Get reedswitch pin
        ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
        controlip = ipadd.read().strip()
        input_uart3 = checkdoorsensor('uart3')
        doorname = dbConnect("select door from doorsetting where wiegand = %s",('uart3',),controlip)
        # read status for input
        if doorname !='' and doorname!=[]: 
            doorname = doorname[0][0]
            if count == 0: 
                doorsensor_close(input_uart3,doorname,controlip)  
                count+=1
            elif count>0:
                if CheckPermition_uart3:
                    if doorsensor_open(input_uart3,doorname,controlip,CheckPermition_uart3)==1:
                        CheckPermition_uart3 = False
                    count-=1    
                else:
                    doorsensor_open(input_uart3,doorname,controlip,CheckPermition_uart3)
                    count-=1
#The uart4 reedswitch port to check door is open or closes
def doorsensor_uart4():
    global CheckPermition_uart4
    count = 0
    while True:
        #First Get reedswitch pin
        ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
        controlip = ipadd.read().strip()
        input_uart4 = checkdoorsensor('uart4')
        doorname = dbConnect("select door from doorsetting where wiegand = %s",('uart4',),controlip)
        # read status for input
        if doorname !='' and doorname!=[]: 
            doorname = doorname[0][0]
            if count == 0: 
                doorsensor_close(input_uart4,doorname,controlip)  
                count+=1
            elif count>0:
                if CheckPermition_uart4:
                    doorsensor_open(input_uart4,doorname,controlip,CheckPermition_uart4)
                    CheckPermition_uart4 = False
                    count-=1    
                else:
                    doorsensor_open(input_uart4,doorname,controlip,CheckPermition_uart4)
                    count-=1
def main():
        #card reader to use uart port 1-4
        global CheckPermition
        try:
            wiegand1 = threading.Thread(target=read_from_port, args=(uart1_dev,"uart1"))
            wiegand2 = threading.Thread(target=read_from_port, args=(uart2_dev,'uart2'))
            wiegand3 = threading.Thread(target=read_from_port, args=(uart3_dev,'uart3'))
            wiegand4 = threading.Thread(target=read_from_port, args=(uart4_dev,'uart4'))
            #Check door status is open or cloes
            t1 = threading.Thread(target=doorsensor_uart1)
            t2 = threading.Thread(target=doorsensor_uart2)
            t3 = threading.Thread(target=doorsensor_uart3)
            t4 = threading.Thread(target=doorsensor_uart4)
            wiegand1.start()
            wiegand2.start()
            wiegand3.start()
            wiegand4.start()
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            wiegand1.join()
            wiegand2.join()
            wiegand3.join()
            wiegand4.join()
            t1.join()
            t2.join()
            t3.join()
            t4.join()
        except OSError as e:
            print(f"Door Read error please check errlog{e}")
if __name__ == "__main__":
    main()
