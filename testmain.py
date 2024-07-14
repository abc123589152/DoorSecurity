from gpiozero import LED
from time import sleep, time
from threading import Thread, Event

# ��??�O�A����?�d?�C��
permit_card_numbers = ["123456", "654321", "111111"]
checkpin = []
# ��l��GPIO 25?LED
with open('relay_pin.txt','r') as readpin:
    relay_pin = int(readpin.read())
    checkpin.append(relay_pin)
    relay = LED(relay_pin)

# ����ƥ�Τ_�����???�{
stop_event = Event()

# ���m��??����?
def reset_timer():
    global stop_event
    # ����?�e??��?�{
    stop_event.set()
    stop_event = Event()
    # ?�طs��??��?�{
    Thread(target=timer_thread, args=(stop_event,)).start()

# ??��?�{��?
def timer_thread(stop_event):
    start_time = time()
    while time() - start_time < 5:
        if stop_event.is_set():
            return
        sleep(0.1)
    relay.off()
    print("Relay deactivated")

# ??��srelay?�H��GPIO��?
def update_relay_pin(new_pin):
    global relay
    relay.close()  # ???�erelay?�H�A?��GPIO��?
    relay = LED(new_pin)  # ��l�Ʒs��relay?�H

def main():
    global relay_pin
    while True:
        # ��??�J�d?
        card_number = input("Enter card number: ")

        # ?�d�d?�O�_�b��?�C����
        if card_number in permit_card_numbers:
            with open('relay_pin.txt','r') as readpin:
                relay_pin = int(readpin.read())
                if relay_pin == checkpin[0]:
                    print("Card permitted, activating relay")
                    relay.on()
                    reset_timer()
                    # ??��srelay?�H��GPIO��?�]�ܨҡ^
                else:
                    with open('relay_pin.txt','r') as readpin:
                        checkpin[0] = int(readpin.read())
                        update_relay_pin(relay_pin)
        else:
            print("Card not permitted")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        relay.off()
        relay.close()
        print("Program terminated")
