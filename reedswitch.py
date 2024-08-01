import serial
import time
import os
import threading
import gpiozero
from gpiozero import event
import db_model.dbConnection as db
from db_model.dbConnection_new import dbConnect
from mysql.connector import Error
from db_model.dbconnect_query import dbConnect_query
from db_model.get_now_time import get_now_date_time
lock = threading.Lock()
CheckPermition = False
reedswitch_check_change= []
def door_statue(uartport,controlip):
    global reedswitch_check_change
    reedswitch_noconvert = db.dbConnect("select door_sensor from doorsetting where wiegand = %s and control = %s", (uartport,controlip,), controlip)
    if type(reedswitch_noconvert) is not type(None) and reedswitch_noconvert!='' and reedswitch_noconvert!=[]:
        reedswitch_pin = int(reedswitch_noconvert[0][0])
        reedswitch_check_change.append(reedswitch_pin)
        reedswitch_uart_pin = gpiozero.Button(reedswitch_pin)
        return reedswitch_uart_pin
    else:
        reedswitch_check_change.append(reedswitch_noconvert)
        return ''
    
def getnewpin(uartport,controlip):
    reedswitchpin_noconvert = db.dbConnect("select door_sensor from doorsetting where wiegand = %s and control = %s", (uartport,controlip,), controlip)
    if type(reedswitchpin_noconvert) is not type(None) and reedswitchpin_noconvert!='' and reedswitchpin_noconvert!=[]:
        return int(reedswitchpin_noconvert[0][0])
    else:
        return ''
def update_reedswitch_pin(new_pin, uartport):
    try:
        if uartport == 'uart2':
            global relay_uart2
            with lock:
                if relay_uart2!='':
                    relay_uart2.close()  # Close the old relay object
                relay_uart2 = gpiozero.Button(new_pin)  # Initialize the new relay object
        elif uartport == 'uart1':
            global reedswitch_uart1
            with lock:
                if reedswitch_uart1!='':
                    reedswitch_uart1.close()  # Close the old relay object
                reedswitch_uart1 = gpiozero.Button(new_pin)  # Initialize the new relay object
        elif uartport == 'uart3':
            global relay_uart3
            with lock:
                if relay_uart3!='':
                    relay_uart3.close()  # Close the old relay object
                relay_uart3 = gpiozero.Button(new_pin)  # Initialize the new relay object
        elif uartport == 'uart4':
            global relay_uart4
            with lock:
                if relay_uart4!='':
                    relay_uart4.close()  # Close the old relay object
                relay_uart4 = gpiozero.Button(new_pin)  # Initialize the new relay object
    except event as e:
        print(f"gpio pin has error,please check error event:{event}")
#check door status function
def checkdoorstatus(input_sensor):
    global CheckPermition
    global reedswitch_check_change
    # read status for input  
    if input_sensor.wait_for_press():
        print("Close door")
        time.sleep(1)
    if input_sensor.wait_for_release():
        if CheckPermition:
            print("open door")
            CheckPermition = False
            time.sleep(1)
        else:
            print("Force Open")
def checkdoorsensor(checkpermition):
    
    #First Get reedswitch pin
    reedswitch_uart1 = door_statue('uart1','172.16.1.186')
    reedswitch_uart1_orignal = getnewpin('uart1','172.16.1.186')
    #Get reedswitch pin
    while True:
        global CheckPermition
        CheckPermition = checkpermition
        print(CheckPermition)
        print(reedswitch_check_change)
        reedswitch_uart1_pin_ischange = getnewpin('uart1','172.16.1.186')
        #check now pin
        if reedswitch_uart1_pin_ischange in reedswitch_check_change and reedswitch_uart1_pin_ischange!='':
            checkdoorstatus(reedswitch_uart1)
        else:
            #change reedswitch port
            reedswitch_check_change.remove(reedswitch_uart1_orignal)
            reedswitch_uart1_orignal = reedswitch_uart1_pin_ischange
            reedswitch_check_change.append(reedswitch_uart1_pin_ischange)
            update_reedswitch_pin(reedswitch_uart1_pin_ischange,'uart1')
            checkdoorstatus(reedswitch_uart1)
        
        
        

    






