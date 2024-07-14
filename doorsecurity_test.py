import serial
import time
import os
import threading
from gpiod.line import Direction, Value
import gpiod
import gpiozero
import db_model.dbConnection as db
lock = threading.Lock()
stop_event =threading.Event()
checkPermition = False

uart1_dev = "/dev/ttyAMA0"
uart2_dev = "/dev/ttyAMA1"
uart3_dev = "/dev/ttyAMA2"
uart4_dev = "/dev/ttyAMA3"

check_uart2_pin = []
ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
onlyipaddress = ipadd.read().strip()
relay_uart2_pin = int(db.dbConnect("select door_lock from doors where weigand = %s and control = %s", ('uart2',onlyipaddress,), onlyipaddress)[0][0])
relay_uart2 = gpiozero.LED(relay_uart2_pin)
check_uart2_pin.append(relay_uart2_pin)


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
def read_from_port(port,weigand_uart):
    global CheckPermition
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Listening on {port}-({weigand_uart})...")
        
        while True:
            data = ser.readline().decode('utf-8').strip()
            allDoorname=[]
            #Get raspberry pi ip address
            ipadd = os.popen("ip -br add | grep eth0 | awk '{print $3}' | cut -d '/' -f1")
            onlyipaddress = ipadd.read().strip()
            #get the uart define door name 
            doorName = db.dbConnect("select door from doors where weigand = %s and control = %s" ,(weigand_uart,onlyipaddress,),onlyipaddress)
            if doorName:
                if data:
                    #relay_uart2_pin = int(db.dbConnect("select door_lock from doors where weigand = %s and control = %s", ('uart2',onlyipaddress,), onlyipaddress)[0][0])
                    #print(f"check_uart2_pin = {check_uart2_pin[0]}")
                    #print(f"relay_uart2_pin now pin = {check_uart2_pin[0]}")
                    print(data)
                
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()         






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