import serial

def read_from_arduino(port='/dev/ttyAMA1', baudrate=9600, timeout=1):
    try:
        # ��l�Ʀ�f
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Listening on {port}...")

        while True:
            # ?��?�u
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    print(f"Received data: {data}")

    except (OSError, serial.SerialException) as e:
        print(f"Error reading from {port}: {e}")
    finally:
        if ser.is_open:
            ser.close()

if __name__ == "__main__":
    try:
        read_from_arduino()
    except KeyboardInterrupt:
        print("Program terminated")
