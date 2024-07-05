import serial
import time
import threading

cardnum = ''
last_sent = ''  # ???????????

ser = serial.Serial('/dev/ttyAMA2', 115200, timeout=1)

def read_from_arduino():
    global cardnum
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                cardnum = data
                print(f"Raspberry Pi received: {data}")

def main():
    global last_sent
    while True:
        if cardnum == "8466156136" and last_sent != "Access":
            ser.write(b"Access\n")
            last_sent = "Access"
            print("Sent: Access")
            time.sleep(1)
        elif cardnum != "8466156136" and last_sent != "Deny":
            ser.write(b"Deny\n")
            last_sent = "Deny"
            print("Sent: Deny")
        time.sleep(0.1)  # ???????????

if __name__ == "__main__":
    # ??????????
    thread = threading.Thread(target=read_from_arduino)
    thread.daemon = True
    thread.start()

    main()
