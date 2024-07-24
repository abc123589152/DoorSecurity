import gpiozero
from time import sleep

# ?? LED ?? GPIO 17
led = gpiozero.LED(23)
# ? LED ? 1 ??? 1 ???? 10 ?
for i in range(10):
    led.on()
    sleep(5)
    led.off()
    sleep(5)