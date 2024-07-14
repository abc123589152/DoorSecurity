import os
with open("relay_pin.txt",'r') as r:
    relay_pin = int(r.read())
    print(relay_pin)