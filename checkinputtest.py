from gpiozero import Button
from signal import pause
import time
button = Button(24)
while True:
    if button.wait_for_press():
        print("Close door")
        time.sleep(1)
    if button.wait_for_release():
        print("open door")
        time.sleep(1)
    