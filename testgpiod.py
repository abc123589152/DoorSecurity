import time
import os
import serial
from gpiod.line import Direction, Value
import gpiod
uart3_port = '/dev/ttyAMA2' 
uart4_port = '/dev/ttyAMA3'  
ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
ipaddread = ipadd.read().strip()
device_ids = {
    uart3_port: ipaddread+'_1',
    uart4_port: ipaddread+'_2'
}
LINE = 23

def read_from_port(port):
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=1)       
        global reset_timer
        print(f"Listening on {port} ({device_ids[port]})...")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    print(f"{device_ids[port]}:{data}")
                    if(data == "8466156136"):
                        ser.write(b'test ok')
                        #request.set_value(LINE,Value.ACTIVE)
                        #time.sleep(5)
                        #request.set_value(LINE,Value.INACTIVE)
                        #ser.write(b'close')
                        
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()
read_from_port(uart4_port)