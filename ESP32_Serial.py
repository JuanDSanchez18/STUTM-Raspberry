""" 
Hecho por Juan Diego Sánchez
Ingenier�a electr�nica
PUJ

"""
import serial
import io
import os
import subprocess
import signal
import time
from datetime import date
from datetime import datetime

import pyrebase

config = {
  "apiKey": "AIzaSyDmuMezNODQFRpu-Qd7scaNNmqLXURZtjI ",
  "authDomain": "rapberry-stutm-a0c0e.firebaseapp.com",
  "databaseURL": "https://rapberry-stutm.firebaseio.com/",
  "storageBucket": "rapberry-stutm.appspot.com" 
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

serialport = "/dev/ttyUSB0"
boardRate = 115200
        
canBreak = False
while not canBreak:
    try:
        ser = serial.Serial(serialport, boardRate)
        canBreak = True
    except KeyboardInterrupt:
        print("\n[+] Exiting...")
        exit()
    except:
        print("[!] Serial connection failed... Retrying...")
        time.sleep(2)
        continue

print("[+] Serial connected. Name: " + ser.name)

today = date.today()

#Datos = "Type= MGMT, Channel= 07, RSSI= -88, Length= 278, SMAC= BC:CA:B5:D7:26:40, Time= 100"
try:
    while True:
        while (today == date.today()):
            #print("sirve")
            Datos = ser.readline()
            Datos = Datos.decode("ascii")
            #Datos = Datos.rstrip("\r\n") 
            RSSI = Datos[Datos.index("RSSI= ") + 6:Datos.index(", Length")]
            #print(RSSI)
            MAC = Datos[Datos.index("SMAC= ") + 6:Datos.index(", Time")] 
            #print(MAC)
            TIME = Datos[Datos.index("Time= ") + 6:Datos.index("\r\n")] 
            #print(TIME)
            
            db.child(str(today)).child("DATA_Serial1").child(MAC).child("Time").push(str(datetime.now().time()))
            db.child(str(today)).child("DATA_Serial1").child(MAC).child("RSSI").push(RSSI)
            db.child(str(today)).child("DATA_Serial1").child(MAC).child("Count").update({"Count": TIME}) 
        
        today = date.today()             
            

except KeyboardInterrupt:
    print("[+] Stopping...")
        
ser.close()
print("[+] Done.")
