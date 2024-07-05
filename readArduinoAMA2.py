import serial

ser = serial.Serial('/dev/ttyAMA2', 115200, timeout=1)
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print("By AMA2")
            print("Received: " + line)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
