import subprocess
import os
#ipadd = os.popen("ip -br add | grep wlan | awk '{print $3}' | cut -d '/' -f1")
#app =  ipadd.read().strip()
#print(f"{app}_1")
with open('/home/master/getip/controlip','r') as re:
    onlyipaddress = re.read().strip()
print(onlyipaddress)