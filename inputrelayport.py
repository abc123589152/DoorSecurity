import os
while True:
    pin = input("pin?")
    with open("relay_pin.txt",'w') as wrrelay_pin:
        wrrelay_pin.write(pin)