import serial

def main():
    # ??????????9600
    ser = serial.Serial('/dev/ttyAMA2', 115200, timeout=1)
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print("Received: " + line)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
