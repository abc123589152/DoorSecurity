import serial

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print("By AMA2")
            print("Received: " + line)
            if line == '2291941972':
                ser.write(b'1')
                print("1")
            else:
                ser.write(b'0')
                print("0")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
