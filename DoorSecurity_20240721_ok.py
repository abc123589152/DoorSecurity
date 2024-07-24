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
relay_uart1 = ''
relay_uart2 = ''
relay_uart3 = ''
relay_uart4 = ''
doorsensor = gpiozero.Button(24)
#Setting red led pins
#redLed_uart1 = gpiozero.LED(17)
#redLed_uart2 = gpiozero.LED(27)
#redLed_uart3 = gpiozero.LED(20)
#redLed_uart4 = gpiozero.LED(21)
ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
onlyipaddress = ipadd.read().strip()
relay_uart1_noconvert = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart1',onlyipaddress,), onlyipaddress)
#Get first time door lock relay pin by uart1
if type(relay_uart1_noconvert) is not type(None) and relay_uart1_noconvert!='' and relay_uart1_noconvert!=[]: 
    relay_uart1_pin = int(relay_uart1_noconvert[0][0])
    relay_uart1 = gpiozero.LED(relay_uart1_pin) 
    check_uart1_pin.append(relay_uart1_pin)
else:
    relay_uart1_pin = relay_uart1_noconvert
    check_uart1_pin.append(relay_uart1_pin)
#Get first time door lock relay pin by uart2
relay_uart2_noconvert = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart2',onlyipaddress,), onlyipaddress)
if type(relay_uart2_noconvert) is not type(None) and relay_uart2_noconvert!='' and relay_uart2_noconvert!=[]: 
    relay_uart2_pin = int(relay_uart2_noconvert[0][0])
    relay_uart2 = gpiozero.LED(relay_uart2_pin) 
    check_uart2_pin.append(relay_uart2_pin)
else:
    relay_uart2_pin = relay_uart2_noconvert
    check_uart2_pin.append(relay_uart2_pin)
#Get first time door lock relay pin by uart3
relay_uart3_noconvert = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart3',onlyipaddress,), onlyipaddress)
if type(relay_uart3_noconvert) is not type(None) and relay_uart3_noconvert!='' and relay_uart3_noconvert!=[]: 
    relay_uart3_pin = int(relay_uart3_noconvert[0][0])
    relay_uart3 = gpiozero.LED(relay_uart3_pin) 
    check_uart3_pin.append(relay_uart3_pin)
else:
    relay_uart3_pin = relay_uart3_noconvert
    check_uart3_pin.append(relay_uart3_pin)
#Get first time door lock relay pin by uart4
relay_uart4_noconvert = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart4',onlyipaddress,), onlyipaddress)
if type(relay_uart4_noconvert) is not type(None) and relay_uart4_noconvert!='' and relay_uart3_noconvert!=[]: 
    relay_uart4_pin = int(relay_uart4_noconvert[0][0])
    relay_uart4 = gpiozero.LED(relay_uart4_pin) 
    check_uart4_pin.append(relay_uart4_pin)
else:
    relay_uart4_pin = relay_uart4_noconvert
check_uart4_pin.append(relay_uart4_pin)
# open door pin
#LINE = 25 
#Input check door status is permition open or force open
# record every port time flags and stop flags
timers = {}
stop_flags = {}

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
    while time.time() - start_time < resettime:
        if stop_event.is_set():
            return
        time.sleep(0.1)
    if uartport == 'uart2':
        if relay_uart2!='':
            relay_uart2.off()
        #redLed_uart2.off()
        print("Relay deactivated")
    elif uartport =='uart1':
        if relay_uart1!='':
            relay_uart1.off()
        #redLed_uart1.off()
        print("Relay deactivated")
    elif uartport =='uart3':
        if relay_uart3!='':
            relay_uart3.off()
        #redLed_uart3.off()
        print("Relay deactivated")
    elif uartport =='uart4':
        if relay_uart4!='':
            relay_uart4.off()
        #redLed_uart4.off()
        print("Relay deactivated")
    

#if relay_pin has change then execute this function
def update_relay_pin(new_pin, uartport):
    try:
        if uartport == 'uart2':
            global relay_uart2
            with lock:
                if relay_uart2!='':
                    relay_uart2.close()  # Close the old relay object
                relay_uart2 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart1':
            global relay_uart1
            with lock:
                if relay_uart1!='':
                    relay_uart1.close()  # Close the old relay object
                relay_uart1 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart3':
            global relay_uart3
            with lock:
                if relay_uart3!='':
                    relay_uart3.close()  # Close the old relay object
                relay_uart3 = gpiozero.LED(new_pin)  # Initialize the new relay object
        elif uartport == 'uart4':
            global relay_uart4
            with lock:
                if relay_uart4!='':
                    relay_uart4.close()  # Close the old relay object
                relay_uart4 = gpiozero.LED(new_pin)  # Initialize the new relay object
    except event as e:
        print(f"gpio pin has error,please check error event:{event}")
        
# Check permition and door open status
def read_from_port(port,wiegand_uart):
    global CheckPermition
    global relay_uart2_pin
    global relay_uart1_pin
    global relay_uart3_pin
    global relay_uart4_pin
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
                        if data and data!='0' or data!='1':
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
                                        if wiegand_uart == 'uart2':
                                            if not type(relay_uart2_pin) is type(None) and relay_uart1_pin!=''and username!=[] and username!='':
                                                relay_uart2_pin = int(db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart2', onlyipaddress,), onlyipaddress)[0][0])
                                                #print("uart2 inside........")
                                                #print(relay_uart2_pin)
                                                #print(check_uart2_pin[0])
                                                if relay_uart2_pin == check_uart2_pin[0]:
                                                    print(f"{doorName[0][0]} Access granted")
                                                    dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                    CheckPermition = True
                                                    relay_uart2.on()
                                                    reset_timer('uart2',onlyipaddress)
                                                else:
                                                    check_uart2_pin[0] = relay_uart2_pin
                                                    update_relay_pin(relay_uart2_pin,'uart2')
                                                    CheckPermition = True
                                                    print(f"{doorName[0][0]} Access granted")
                                                    dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                    relay_uart2.on()
                                                    reset_timer('uart2',onlyipaddress)
                                                #set_value_with_timeout(request, int(door_lock[0][0]), Value.ACTIVE, 5)#open the door to put GPIO 23(LINE is 23) Active
                                        elif wiegand_uart == 'uart1':
                                            relay_uart1_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart1', onlyipaddress,), onlyipaddress)[0][0]
                                            if not type(relay_uart1_pin) is type(None) and relay_uart1_pin!=''and username!=[] and username!='':
                                                #print("uart1 inside........")
                                                #print(relay_uart1_pin)
                                                #print(check_uart1_pin[0])
                                                relay_uart1_pin = int(relay_uart1_pin)
                                                if relay_uart1_pin == check_uart1_pin[0]:
                                                    print(f"{doorName[0][0]} Access granted")
                                                    dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                    CheckPermition = True
                                                    relay_uart1.on()
                                                    ser.write(b'1')
                                                    reset_timer('uart1',onlyipaddress)
                                                else:
                                                    check_uart1_pin[0] = relay_uart1_pin
                                                    update_relay_pin(relay_uart1_pin,'uart1')
                                                    CheckPermition = True
                                                    print(f"{doorName[0][0]} Access granted")
                                                    dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                    relay_uart1.on()
                                                    ser.write(b'1')
                                                    reset_timer('uart1',onlyipaddress)
                                        elif wiegand_uart == 'uart3':
                                            relay_uart3_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart3', onlyipaddress,), onlyipaddress)
                                            if relay_uart3_pin !=[]:
                                                relay_uart3_pin = relay_uart3_pin[0][0]
                                                if not type(relay_uart3_pin) is type(None) and relay_uart3_pin !='':
                                                    #print("uart3 inside........")
                                                    #print(relay_uart3_pin)
                                                    #print(check_uart3_pin[0])
                                                    relay_uart3_pin = int(relay_uart3_pin)
                                                    if relay_uart3_pin == check_uart3_pin[0]:
                                                        dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                        print(f"{doorName[0][0]} Access granted")
                                                        CheckPermition = True
                                                        relay_uart3.on()
                                                        reset_timer('uart3',onlyipaddress)
                                                    else:
                                                        check_uart3_pin[0] = relay_uart3_pin
                                                        update_relay_pin(relay_uart3_pin,'uart3')
                                                        CheckPermition = True
                                                        print(f"{doorName[0][0]} Access granted")
                                                        dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                        relay_uart3.on()
                                                        reset_timer('uart3',onlyipaddress)
                                        elif wiegand_uart == 'uart4':
                                            relay_uart4_pin = db.dbConnect("select door_lock from doorsetting where wiegand = %s and control = %s", ('uart4', onlyipaddress,), onlyipaddress)
                                            if relay_uart4_pin !=[]:
                                                relay_uart4_pin = relay_uart4_pin[0][0]
                                                print(f"inside ={relay_uart4_pin}")
                                                if not type(relay_uart4_pin) is type(None) and relay_uart4_pin !='':
                                                    #print("uart4 inside........")
                                                    #print(relay_uart4_pin)
                                                    #print(check_uart4_pin[0])
                                                    relay_uart4_pin = int(relay_uart4_pin)
                                                    #alter relay_uart4 port 
                                                    if relay_uart4_pin == check_uart4_pin[0]:
                                                        print(f"{doorName[0][0]} Access granted")
                                                        dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                        CheckPermition = True
                                                        relay_uart4.on()
                                                        reset_timer('uart4',onlyipaddress)
                                                    else:
                                                        check_uart4_pin[0] = relay_uart4_pin
                                                        update_relay_pin(relay_uart4_pin,'uart4')
                                                        CheckPermition = True
                                                        print(f"{doorName[0][0]} Access granted")
                                                        dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'Pemit',get_now_date_time()),onlyipaddress)
                                                        relay_uart4.on()
                                                        reset_timer('uart4',onlyipaddress)
                                    else:
                                        with lock:
                                            #print(door_lock[0][0]) 
                                            print(f"{doorName[0][0]} Access Deny")
                                            if username!=[]:
                                                dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",(username[0][0],data,doorName[0][0],doorstatus[0][0],'deny',get_now_date_time()),onlyipaddress)
                                                ser.write(b'0')
                                            else:
                                                dbConnect_query("insert into doorLog(username,cardnumber,doorName,doorStatus,authorization,swipeTime)values(%s,%s,%s,%s,%s,%s)",('Unknown Card',data,doorName[0][0],doorstatus[0][0],'deny',get_now_date_time()),onlyipaddress)
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
            wiegand1 = threading.Thread(target=read_from_port, args=(uart1_dev,"uart1"))
            wiegand2 = threading.Thread(target=read_from_port, args=(uart2_dev,'uart2'))
            wiegand3 = threading.Thread(target=read_from_port, args=(uart3_dev,'uart3'))
            wiegand4 = threading.Thread(target=read_from_port, args=(uart4_dev,'uart4'))
            #Check door status is open or cloes
            #t3 = threading.Thread(target=checkdoorstatus)
            wiegand1.start()
            wiegand2.start()
            wiegand3.start()
            wiegand4.start()
            #t3.start()
            wiegand1.join()
            wiegand2.join()
            wiegand3.join()
            wiegand4.join()
            #t3.join()
        except OSError as e:
            print(f"Door Read error please check errlog{e}")
if __name__ == "__main__":
    main()
