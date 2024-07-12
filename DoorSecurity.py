import serial
import time
import os
import threading
from gpiod.line import Direction, Value
import gpiod
import gpiozero
# Arduino AMA port
CheckPermition = False
uart3_port = '/dev/ttyAMA2'
uart4_port = '/dev/ttyAMA3'
ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
ipaddread = ipadd.read().strip()
device_ids = {
    uart3_port: ipaddread + '_1',
    uart4_port: ipaddread + '_2'
}
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
def read_from_port(port, request):
    global CheckPermition
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port} ({device_ids[port]})...")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    print(f"{device_ids[port]}:{data}")
                    if data == "8466156136":
                        print("Access granted")
                        CheckPermition = True
                        set_value_with_timeout(request, LINE, Value.ACTIVE, 5)
                    else:
                        with lock:
                            request.set_value(LINE, Value.INACTIVE)
                            print("Access Deny!")
            
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()
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
    config = {
        LINE: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
    }
    with gpiod.request_lines("/dev/gpiochip4", consumer="blink-example", config=config) as request:
        t1 = threading.Thread(target=read_from_port, args=(uart3_port, request))
        t2 = threading.Thread(target=read_from_port, args=(uart4_port, request))
        t3 = threading.Thread(target=checkdoorstatus)
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
if __name__ == "__main__":
    main()
