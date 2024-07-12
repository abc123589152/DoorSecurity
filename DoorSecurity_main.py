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

doorsensor = gpiozero.Button(24)
# open door pin
LINE = 23 
#Input check door status is permition open or force open
LINE2 = 24
# record every port time flags and stop flags
timers = {}
stop_flags = {}

lock = threading.Lock()

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
    print(stop_flags)
    stop_flags[line] = threading.Event()
    timer = threading.Thread(target=reset_value, args=(stop_flags[line],))
    timers[line] = timer
    print(timers[line])
    timer.start()

    
# Check permition and door open status
def read_from_port(port, request,weigand_uart):
    global CheckPermition
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port} ({device_ids[port]})...")
        while True:
            allDoorname=[]
            #Get raspberry pi ip address
            ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
            onlyipaddress = ipadd.read().strip()
            #get the uart define door name 
            doorName = db.dbConnect("select door from doors where weigand = %s and control = %s" ,(weigand_uart,onlyipaddress,))
            if doorName:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    if data:
                        #find card number to permit groupname
                        findcardgroup = db.dbConnect("select groupname from cardGroups where cardnumber =%s",(data,))
                        for i in range(0,len(findcardgroup)):
                            allDoorname.append(db.dbConnect("select doorname from doorgroup where groupname = %s",(findcardgroup[i][0],)))#all permit door append to list
                        door_list = [item for sublist in allDoorname for item in sublist]
                        door_everyone_list = [item[0] for item in door_list]#Convert a multidimensional array into a one-dimensional array
                        if data in door_everyone_list:
                            print("Access granted")
                            CheckPermition = True
                            set_value_with_timeout(request, LINE, Value.ACTIVE, 5)#open the door to put GPIO 23(LINE is 23) Active
                        else:
                            with lock:
                                request.set_value(LINE, Value.INACTIVE)#close door
                                print("Access Deny!")
            
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()
#check door status function
def checkdoorstatus():
    global CheckPermition
    # read status for input  
    while True:
            if doorsensor.wait_for_press():
                print("Close door")
                time.sleep(1)
            if doorsensor.wait_for_release():
                if CheckPermition:
                    print("open door")
                    CheckPermition = False
                    time.sleep(1)
                else:
                    print("Force Open")
def main():
    #config to define gpiod
    config = {
        LINE: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
    }
    with gpiod.request_lines("/dev/gpiochip4", consumer="blink-example", config=config) as request:
        #card reader to use uart port 1-4
        weigand1 = threading.Thread(target=read_from_port, args=(uart1_dev, request,"uart1"))
        weigand2 = threading.Thread(target=read_from_port, args=(uart2_dev, request,'uart2'))
        weigand3 = threading.Thread(target=read_from_port, args=(uart3_dev, request,'uart3'))
        weigand4 = threading.Thread(target=read_from_port, args=(uart4_dev, request,'uart4'))
        #Check door status is open or cloes
        t3 = threading.Thread(target=checkdoorstatus)
        weigand1.start()
        weigand2.start()
        weigand3.start()
        weigand4.start()
        t3.start()
        weigand1.join()
        weigand2.join()
        weigand3.join()
        weigand4.join()
        t3.join()
if __name__ == "__main__":
    main()
