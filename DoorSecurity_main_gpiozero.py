import serial
import time
import os
import threading
from gpiod.line import Direction, Value
import gpiod
import gpiozero
import db_model.dbConnection as db
# Arduino AMA port
CheckPermition = False
#???????
uart1_dev = "/dev/ttyAMA0"
uart2_dev = "/dev/ttyAMA1"
uart3_dev = "/dev/ttyAMA2"
uart4_dev = "/dev/ttyAMA3"
check_uart2_pin = []
doorsensor = gpiozero.Button(24)
ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
onlyipaddress = ipadd.read().strip()
relay_uart2_pin = int(db.dbConnect("select door_lock from doors where weigand = %s and control = %s", ('uart2',onlyipaddress,), onlyipaddress)[0][0])
relay_uart2 = gpiozero.LED(relay_uart2_pin)
check_uart2_pin.append(relay_uart2_pin)
# open door pin
#LINE = 25 
#Input check door status is permition open or force open
LINE2 = 24
# record every port time flags and stop flags
timers = {}
stop_flags = {}

lock = threading.Lock()
stop_event =threading.Event()
def reset_timer(uartport):
    global stop_event
    # ����?�e??��?�{
    stop_event.set()
    stop_event = threading.Event()
    # ?�طs��??��?�{
    if uartport == 'uart2':
        threading.Thread(target=timer_thread, args=(stop_event,'uart2',)).start()

# ??��?�{��?
def timer_thread(stop_event,uartport):
    start_time = time.time()
    while time.time() - start_time < 5:
        if stop_event.is_set():
            return
        time.sleep(0.1)
    if uartport == 'uart2':
        relay_uart2.off()
        print("Relay deactivated")

# ??��srelay?�H��GPIO��?
def update_relay_pin(new_pin, uartport):
    if uartport == 'uart2':
        global relay_uart2
        with lock:
            relay_uart2.close()  # Close the old relay object
            relay_uart2 = gpiozero.LED(new_pin)  # Initialize the new relay object



def set_value_with_timeout(request, line, value, timeout):
    #GPIO timeout to reset
    def reset_value(stop_flag):
        global CheckPermition
        time.sleep(timeout)
        with lock:
            if not stop_flag.is_set():               
                request.set_value(line, Value.INACTIVE)
                CheckPermition = False

    #open the door
    with lock:
        request.set_value(line, value)

    # if time flags is start,then cancal it
    if line in stop_flags:
        stop_flags[line].set()
    # Creat the new time flags
    #print(stop_flags)
    stop_flags[line] = threading.Event()
    timer = threading.Thread(target=reset_value, args=(stop_flags[line],))
    timers[line] = timer
    #print(timers[line])
    timer.start()

    
# Check permition and door open status
def read_from_port(port,weigand_uart):
    global CheckPermition
    global relay_uart2_pin
    print(relay_uart2_pin)
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port}-({weigand_uart})...")
        while True:
            allDoorname=[]
            #Get raspberry pi ip address
            ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
            onlyipaddress = ipadd.read().strip()
            #get the uart define door name 
            doorName = db.dbConnect("select door from doors where weigand = %s and control = %s" ,(weigand_uart,onlyipaddress,),onlyipaddress)
            if doorName:
                if ser.in_waiting > 0:
                    door_lock = db.dbConnect("select door_lock from doors where weigand = %s and control = %s", (weigand_uart, onlyipaddress,), onlyipaddress)
                    print(door_lock)
                    print(weigand_uart)
                    data = ser.readline().decode('utf-8').strip()
                    if data:
                        #find card number to permit groupname
                        findcardgroup = db.dbConnect("select groupname from cardGroups where cardnumber =%s",(data,),onlyipaddress)
                        for i in range(0,len(findcardgroup)):
                            allDoorname.append(db.dbConnect("select doorname from doorgroup where groupname = %s",(findcardgroup[i][0],),onlyipaddress))#all permit door append to list
                        door_list = [item for sublist in allDoorname for item in sublist]
                        door_everyone_list = [item[0] for item in door_list]#Convert a multidimensional array into a one-dimensional array
                        if doorName[0][0] in door_everyone_list:
                            if weigand_uart == 'uart2':
                                relay_uart2_pin = int(db.dbConnect("select door_lock from doors where weigand = %s and control = %s", ('uart2', onlyipaddress,), onlyipaddress)[0][0])
                                print("uart2 inside........")
                                print(relay_uart2_pin)
                                print(check_uart2_pin[0])
                                if relay_uart2_pin == check_uart2_pin[0]:
                                    print(f"{doorName[0][0]} Access granted")
                                    CheckPermition = True
                                    relay_uart2.on()
                                    reset_timer('uart2')
                                else:
                                    check_uart2_pin[0] = relay_uart2_pin
                                    update_relay_pin(relay_uart2_pin,'uart2')
                                    CheckPermition = True
                                    print(f"{doorName[0][0]} Access granted")
                                    relay_uart2.on()
                                    reset_timer('uart2')
                                #set_value_with_timeout(request, int(door_lock[0][0]), Value.ACTIVE, 5)#open the door to put GPIO 23(LINE is 23) Active
                        else:
                            with lock:
                                #print(door_lock[0][0]) 
                                print(f"{doorName[0][0]} Access Deny!")
            
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
        #weigand1 = threading.Thread(target=read_from_port, args=(request,uart1_dev,"uart1"))
        weigand2 = threading.Thread(target=read_from_port, args=(uart2_dev,'uart2'))
        #weigand3 = threading.Thread(target=read_from_port, args=(request,uart3_dev,'uart3'))
        #weigand4 = threading.Thread(target=read_from_port, args=(request,uart4_dev,'uart4'))
        #Check door status is open or cloes
        #t3 = threading.Thread(target=checkdoorstatus)
        #weigand1.start()
        weigand2.start()
        #weigand3.start()
        #weigand4.start()
        #t3.start()
        #weigand1.join()
        weigand2.join()
        #weigand3.join()
        #weigand4.join()
        #t3.join()
if __name__ == "__main__":
    main()
