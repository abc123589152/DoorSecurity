import serial
import time
import os
#Arduino AMA port
uart3_port = '/dev/ttyAMA2' 
uart4_port = '/dev/ttyAMA3'  
ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
ipaddread = ipadd.read().strip()
device_ids = {
    uart3_port: ipaddread+'_1',
    uart4_port: ipaddread+'_2'
}

def read_from_port(port):
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=1)
        
        print(f"Listening on {port} ({device_ids[port]})...")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    print(f"{device_ids[port]} {data}")
    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()

def main():
    import threading
    t1 = threading.Thread(target=read_from_port, args=(uart3_port,))
    t2 = threading.Thread(target=read_from_port, args=(uart4_port,))
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
