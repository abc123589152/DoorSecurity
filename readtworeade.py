import serial
import time
import os
import threading
from gpiod.line import Direction,Value
import gpiod
from gpiod.line import Direction, Value
#Arduino AMA port
uart3_port = '/dev/ttyAMA2' 
uart4_port = '/dev/ttyAMA3'  
ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
ipaddread = ipadd.read().strip()
device_ids = {
    uart3_port: ipaddread+'_1',
    uart4_port: ipaddread+'_2'
}
LINE = 23
close = False
# reset_timer = False

# def handle_opendoor(statcheck,port):
#     global reset_timer
#     ser = serial.Serial(port,115200,timeout=1)
#     while True:
#         ser.write(statcheck.encode('utf-8'))
#         if reset_timer:
#             reset_timer = False
#             print("5")
#             for _ in range(5):
#                 if reset_timer:
#                     break
#                 ser.write(b"close")
#                 time.sleep(1)
#         else:
#             time.sleep(0.1)

def read_from_port(port):
    global close
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=1) 
        global reset_timer
        print(f"Listening on {port} ({device_ids[port]})...")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                with gpiod.request_lines(
                            "/dev/gpiochip4",
                            consumer="blink-example",
                            config={
                                LINE: gpiod.LineSettings(
                                direction=Direction.OUTPUT, output_value=Value.ACTIVE
                                )
                            },
                ) as request:
                    if data:
                        print(f"{device_ids[port]}:{data}")
                        if(data == "8466156136"):
                            print("Access")
                            request.set_value(LINE,Value.ACTIVE)
                            timeclose = threading.Thread(target=timesleep,args=(request))
                            timeclose.start()
                            timeclose.join()                                  
                        else:
                            request.set_value(LINE,Value.INACTIVE)
                        
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()
def timesleep():
    time.sleep(5)
def main():
    t1 = threading.Thread(target=read_from_port, args=(uart3_port,))
    t2 = threading.Thread(target=read_from_port, args=(uart4_port,))
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
