import threading
import time
import serial
reset_timer = False

def handle_opendoor():
    global reset_timer
    ser = serial.Serial("/dev/ttyAMA2",115200,timeout=1)
    while True:
        ser.write(b"opendoor")
        if reset_timer:
            reset_timer = False
            print("5")
            for _ in range(5):
                if reset_timer:
                    break
                ser.write(b"close")
                time.sleep(1)
        else:
            time.sleep(0.1)

def main():
    global reset_timer
    threading.Thread(target=handle_opendoor, daemon=True,args=(command)).start()
    
    while True:
        command = input("Enter command: ")
        if command == "opendoor":
            reset_timer = True
            

if __name__ == "__main__":
    main()
