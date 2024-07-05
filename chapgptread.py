import serial
import time
import threading
import gpiod
cardnum = ''
# ????
ser = serial.Serial('/dev/ttyAMA2', 115200, timeout=1)

# ??????????
def read_from_arduino():
    global cardnum
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            cardnum = data
            if data:
                print(f"Raspberry Pi received: {data}")

# ??????????
thread = threading.Thread(target=read_from_arduino)
thread.daemon = True
thread.start()

while True:
    if cardnum == "8466156136":
        ser.write(b"Access\n")
        time.sleep(1)  # ??????
    else:
        ser.write(b'Deny')
