import serial
import time
import os
import threading
from gpiod.line import Direction, Value
import gpiod
import gpiozero
from gpiozero import event
import db_model.dbConnection as db
from db_model.dbConnection_new import dbConnect
from mysql.connector import Error
from db_model.dbconnect_query import dbConnect_query
from db_model.get_now_time import get_now_date_time
# Arduino AMA port
CheckPermition = False
#???????
uart1_dev = "/dev/ttyAMA0"
uart2_dev = "/dev/ttyAMA1"
uart3_dev = "/dev/ttyAMA2"
uart4_dev = "/dev/ttyAMA3"
check_uart1_pin = []
check_uart2_pin = []
check_uart3_pin = []
check_uart4_pin = []
doorsensor = gpiozero.Button(24)
ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
onlyipaddress = ipadd.read().strip()
relay_uart1_noconvert = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart1',onlyipaddress,), onlyipaddress)
if type(relay_uart1_noconvert) is not type(None) and relay_uart1_noconvert!='': 
    relay_uart1_pin = int(relay_uart1_noconvert[0][0])
    relay_uart1 = gpiozero.LED(relay_uart1_pin) 
    check_uart1_pin.append(relay_uart1_pin)
else:
    relay_uart1_pin = relay_uart1_noconvert
    check_uart1_pin.append(relay_uart1_pin)

relay_uart2_noconvert = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart2',onlyipaddress,), onlyipaddress)
if type(relay_uart2_noconvert) is not type(None) and relay_uart2_noconvert!='': 
    relay_uart2_pin = int(relay_uart2_noconvert[0][0])
    relay_uart2 = gpiozero.LED(relay_uart2_pin) 
    check_uart2_pin.append(relay_uart2_pin)
else:
    relay_uart1_pin = relay_uart1_noconvert
    check_uart1_pin.append(relay_uart1_pin)

relay_uart3_noconvert = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart3',onlyipaddress,), onlyipaddress)
if type(relay_uart3_noconvert) is not type(None) and relay_uart3_noconvert!='': 
    relay_uart3_pin = int(relay_uart3_noconvert[0][0])
    relay_uart3 = gpiozero.LED(relay_uart3_pin) 
    check_uart3_pin.append(relay_uart3_pin)
else:
    relay_uart3_pin = relay_uart3_noconvert
    check_uart3_pin.append(relay_uart3_pin)

relay_uart4_noconvert = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart4',onlyipaddress,), onlyipaddress)
if type(relay_uart4_noconvert) is not type(None) and relay_uart4_noconvert!='': 
    relay_uart4_pin = int(relay_uart4_noconvert[0][0])
    relay_uart4 = gpiozero.LED(relay_uart4_pin) 
    check_uart4_pin.append(relay_uart4_pin)
else:
    relay_uart4_pin = relay_uart4_noconvert
check_uart4_pin.append(relay_uart4_pin)
# open door pin
#LINE = 25 
#Input check door status is permition open or force open
LINE2 = 24
# record every port time flags and stop flags
timers = {}
stop_flags = {}

lock = threading.Lock()
stop_event =threading.Event()
def reset_timer(uartport,controlip):
    global stop_event
    #select database to setting reset_time
    stop_event.set()
    stop_event = threading.Event()
    resettime = db.dbConnect("select reset_time from doorsetting where control = %s and weigand = %s",(controlip,uartport,),controlip)
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

# ??��?�{��?
def timer_thread(stop_event,uartport,resettime):
    start_time = time.time()
    while time.time() - start_time < resettime:
        if stop_event.is_set():
            return
        time.sleep(0.1)
    if uartport == 'uart2':
        relay_uart2.off()
        print("Relay deactivated")
    elif uartport =='uart1':
        relay_uart1.off()
        print("Relay deactivated")
    elif uartport =='uart3':
        relay_uart3.off()
        print("Relay deactivated")
    elif uartport =='uart4':
        relay_uart4.off()
        print("Relay deactivated")
    

# ??��srelay?�H��GPIO��?
def update_relay_pin(new_pin, uartport):
    try:
        if uartport == 'uart2':
            global relay_uart2
            with lock:
                relay_uart2.close()  # Close the old relay object
                relay_uart2 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart1':
            global relay_uart1
            with lock:
                relay_uart1.close()  # Close the old relay object
                relay_uart1 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart3':
            global relay_uart3
            with lock:
                relay_uart3.close()  # Close the old relay object
                relay_uart3 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart4':
            global relay_uart4
            with lock:
                relay_uart4.close()  # Close the old relay object
                relay_uart4 = gpiozero.LED(new_pin)  # Initialize the new relay object
    except event as e:
        print(f"gpio pin has error,please check error event:{event}")


# def set_value_with_timeout(request, line, value, timeout):
#     #GPIO timeout to reset
#     def reset_value(stop_flag):
#         global CheckPermition
#         time.sleep(timeout)
#         with lock:
#             if not stop_flag.is_set():               
#                 request.set_value(line, Value.INACTIVE)
#                 CheckPermition = False

#     #open the door
#     with lock:
#         request.set_value(line, value)

#     # if time flags is start,then cancal it
#     if line in stop_flags:
#         stop_flags[line].set()
#     # Creat the new time flags
#     #print(stop_flags)
#     stop_flags[line] = threading.Event()
#     timer = threading.Thread(target=reset_value, args=(stop_flags[line],))
#     timers[line] = timer
#     #print(timers[line])
#     timer.start()

    
# Check permition and door open status
def read_from_port(port,weigand_uart):
    global CheckPermition
    global relay_uart2_pin
    global relay_uart1_pin
    global relay_uart3_pin
    global relay_uart4_pin
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port}-({weigand_uart})...")
        while True:
            try:
                allDoorname=[]
                data = ''
                #Get raspberry pi ip address
                ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
                onlyipaddress = ipadd.read().strip()
                #get the uart define door name 
                doorName = db.dbConnect("select door from doorsetting where weigand = %s and control = %s" ,(weigand_uart,onlyipaddress,),onlyipaddress)
                
                if doorName:
                    doorstatus = db.dbConnect("select remark from doorsetting where door=%s",(doorName[0][0],),onlyipaddress)
                    if ser.in_waiting > 0:
                        #get readcard door number
                        door_lock = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", (weigand_uart, onlyipaddress,), onlyipaddress)
                        print(door_lock)
                        print(weigand_uart)
                        try:
                            data = ser.readline().decode('Utf-8').strip()
                        except UnicodeDecodeError as e:
                            print(e)
                        if data:
                            find_card_group = ""
                            try:
                                print(f"cardnumber:{data}")
                                #find card number to permit groupname
                                findcardgroup = dbConnect("select doorgroup from employ where cardnumber =%s",(data,),onlyipaddress)
                                print(findcardgroup)
                                for findcard_group in findcardgroup[0]:
                                    find_card_group = findcard_group.split(',')
                                #use groupname to find in the group doors name
                                for get_doorgroup_name in find_card_group:
                                    find_every_door = dbConnect("select doorname from doorgroup where groupname = %s",(get_doorgroup_name,),onlyipaddress)
                                    for getalldoor in find_every_door[0]:
                                        for every_door in getalldoor.split(','):
                                            allDoorname.append(every_door)
                                #find all doorgroup perrmit doorr number
                                if doorName[0][0] in allDoorname:
                                    if weigand_uart == 'uart2':
                                        if not type(relay_uart2_pin) is type(None):
                                            relay_uart2_pin = int(db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart2', onlyipaddress,), onlyipaddress)[0][0])
                                            print("uart2 inside........")
                                            print(relay_uart2_pin)
                                            print(check_uart2_pin[0])
                                            if relay_uart2_pin == check_uart2_pin[0]:
                                                print(f"{doorName[0][0]} Access granted")
                                                CheckPermition = True
                                                relay_uart2.on()
                                                reset_timer('uart2',onlyipaddress)
                                            else:
                                                check_uart2_pin[0] = relay_uart2_pin
                                                update_relay_pin(relay_uart2_pin,'uart2')
                                                CheckPermition = True
                                                print(f"{doorName[0][0]} Access granted")
                                                relay_uart2.on()
                                                reset_timer('uart2',onlyipaddress)
                                            #set_value_with_timeout(request, int(door_lock[0][0]), Value.ACTIVE, 5)#open the door to put GPIO 23(LINE is 23) Active
                                    elif weigand_uart == 'uart1':
                                        relay_uart1_pin = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart1', onlyipaddress,), onlyipaddress)[0][0]
                                        if not type(relay_uart1_pin) is type(None) and relay_uart1_pin!='':
                                            print("uart1 inside........")
                                            print(relay_uart1_pin)
                                            print(check_uart1_pin[0])
                                            relay_uart1_pin = int(relay_uart1_pin)
                                            if relay_uart1_pin == check_uart1_pin[0]:
                                                print(f"{doorName[0][0]} Access granted")
                                                insertauthorization = dbConnect_query("insert into doorLog(doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s)",(doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()))
                                                CheckPermition = True
                                                relay_uart1.on()
                                                reset_timer('uart1',onlyipaddress)
                                            else:
                                                check_uart1_pin[0] = relay_uart1_pin
                                                update_relay_pin(relay_uart1_pin,'uart1')
                                                CheckPermition = True
                                                print(f"{doorName[0][0]} Access granted")
                                                insertauthorization = dbConnect_query("insert into doorLog(doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s)",(doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()))
                                                relay_uart1.on()
                                                reset_timer('uart1',onlyipaddress)
                                    elif weigand_uart == 'uart3':
                                        relay_uart3_pin = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart3', onlyipaddress,), onlyipaddress)
                                        if relay_uart3_pin !=[]:
                                            relay_uart3_pin = relay_uart3_pin[0][0]
                                            if not type(relay_uart3_pin) is type(None) and relay_uart3_pin !='':
                                                print("uart3 inside........")
                                                print(relay_uart3_pin)
                                                print(check_uart3_pin[0])
                                                relay_uart3_pin = int(relay_uart3_pin)
                                                if relay_uart3_pin == check_uart3_pin[0]:
                                                    print(f"{doorName[0][0]} Access granted")
                                                    CheckPermition = True
                                                    relay_uart3.on()
                                                    reset_timer('uart3',onlyipaddress)
                                                else:
                                                    if check_uart3_pin[0] !='':
                                                        update_relay_pin(relay_uart3_pin,'uart3')
                                                    CheckPermition = True
                                                    print(f"{doorName[0][0]} Access granted")
                                                    relay_uart3.on()
                                                    reset_timer('uart3',onlyipaddress)
                                                    check_uart3_pin[0] = relay_uart3_pin
                                    elif weigand_uart == 'uart4':
                                        relay_uart4_pin = db.dbConnect("select door_lock from doorsetting where weigand = %s and control = %s", ('uart4', onlyipaddress,), onlyipaddress)
                                        if relay_uart4_pin !=[]:
                                            relay_uart4_pin = relay_uart4_pin[0][0]
                                            print(f"inside ={relay_uart4_pin}")
                                            if not type(relay_uart4_pin) is type(None) and relay_uart4_pin !='':
                                                print("uart4 inside........")
                                                print(relay_uart4_pin)
                                                print(check_uart4_pin[0])
                                                relay_uart4_pin = int(relay_uart4_pin)
                                                #alter relay_uart4 port 
                                                if relay_uart4_pin == check_uart4_pin[0]:
                                                    print(f"{doorName[0][0]} Access granted")
                                                    CheckPermition = True
                                                    relay_uart4.on()
                                                    reset_timer('uart4',onlyipaddress)
                                                else:
                                                    check_uart4_pin[0] = relay_uart4_pin
                                                    update_relay_pin(relay_uart4_pin,'uart4')
                                                    CheckPermition = True
                                                    print(f"{doorName[0][0]} Access granted")
                                                    relay_uart4.on()
                                                    reset_timer('uart4',onlyipaddress)
                                else:
                                    with lock:
                                        #print(door_lock[0][0]) 
                                        print(f"{doorName[0][0]} Access Deny!") 
                            except Error as e:
                                print(f"data base has error: {e}")
            except OSError as e:
                print(e)   
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()
#check door status function
def checkdoorstatus(input_sensor):
    global CheckPermition
    # read status for input  
    while True:
            if input_sensor.wait_for_press():
                print("Close door")
                time.sleep(1)
            if input_sensor.wait_for_release():
                if CheckPermition:
                    print("open door")
                    CheckPermition = False
                    time.sleep(1)
                else:
                    print("Force Open")
def main():
        #card reader to use uart port 1-4
        try:
            weigand1 = threading.Thread(target=read_from_port, args=(uart1_dev,"uart1"))
            weigand2 = threading.Thread(target=read_from_port, args=(uart2_dev,'uart2'))
            weigand3 = threading.Thread(target=read_from_port, args=(uart3_dev,'uart3'))
            weigand4 = threading.Thread(target=read_from_port, args=(uart4_dev,'uart4'))
            #Check door status is open or cloes
            #t3 = threading.Thread(target=checkdoorstatus)
            weigand1.start()
            weigand2.start()
            weigand3.start()
            weigand4.start()
            #t3.start()
            weigand1.join()
            weigand2.join()
            weigand3.join()
            weigand4.join()
            #t3.join()
        except OSError as e:
            print(f"Door Read error please check errlog{e}")
if __name__ == "__main__":
    main()
