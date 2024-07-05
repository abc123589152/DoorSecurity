import serial
import time
ser = serial.Serial("/dev/ttyAMA2",115200,timeout=1)
ser1 = serial.Serial("/dev/ttyAMA3",115200,timeout=1)
time.sleep(5)
while True:
   with open('CardNumber','r') as r:
      card = r.read()
      if card == '671158927':
         ser1.write(b'Access')
         print("Raspberry pi say Access")
         time.sleep(1)