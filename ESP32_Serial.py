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
from datetime import date, datetime

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
todaystr =str(today)

start = time.time()
end = time.time()

MACT = ""
vez = 1 

#os.mkdir("MAC/" + todaystr)
#filename = "MAC/"+todaystr+"/capture.txt"

#os.mkdir("Reportes" )
filename = "Reportes/capture.txt"


#Paquete desde la ESP32
#SMAC= 90:63:3B:9E:2D:27, RSSI= -32 
try:
    while True:
        while (today == date.today()):
            maclist = []
            timestartlist = []
            timefinallist = []
            
            vez = vez+1
            initialtime = "/CALLE45/" + str(vez+1)
            initialtime = todaystr + initialtime
            #print (initialtime)
            
            filename = filename + str(datetime.now())
            f = open(filename,'w')
            while (end-start) < 900:
                
                Datos = ser.readline()
                Datos = Datos.decode("ascii")
                  
                MAC = Datos[Datos.index("SMAC= ") + 6:Datos.index(", RSSI")] 
                #print(MAC)
                RSSI = Datos[Datos.index("RSSI= ") + 6:Datos.index("\r\n")]
                #print(RSSI)
                                                                        
                if (MAC != MACT):
                                                          
                    MACT = MAC                   
                    print(MACT)
                    Time = datetime.now().time()
                    Timestr = str(Time)
                    
                    if (MAC in maclist):  

                        position = maclist.index(MAC)
                        #print(position)
                        starttime = timestartlist[position]
                        timefinallist[position] = Time
                        
                        
                        durationtime = datetime.combine(today, Time) - datetime.combine(today, starttime)
                        durationtime = str(durationtime.total_seconds())
                        print(durationtime) 
                                             
                        #Save txt file
                        f.write(Timestr +", ")
                        f.write(MAC +", "+ RSSI +" \n")
                        f.flush()
                        
                        #Update Firebase                        
                        db.child(initialtime).child(MAC).child("Final_time").update({"Time": Timestr})
                        db.child(initialtime).child(MAC).child("Duration_time").set({"Time": durationtime +" s"})
                   
                    else:
                        
                        maclist.append(MAC)
                        timestartlist.append(Time)
                        timefinallist.append(Time)
                        
                        #Save txt file
                        f.write(Timestr +", ")
                        f.write(MAC +", "+ RSSI +", First \n")
                        f.flush()
                        
                        #Send to Firebase
                        db.child(initialtime).child(MAC).child("Start_time").set({"Time": Timestr})
                        db.child(initialtime).child(MAC).child("Final_time").set({"Time": Timestr})
                        db.child(initialtime).child(MAC).child("Duration_time").set({"Time": "0 s"})
                                
                end = time.time()
            start = time.time()  
            f.close()
            filename = "Reportes/capture.txt"
               
        vez = 0
        today = date.today()
        todaystr = str(date.today())
            
except KeyboardInterrupt:
    print("[+] Stopping...")
        
ser.close()
print("[+] Done.")
