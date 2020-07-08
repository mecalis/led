import socket
from queue import Queue
from threading import Thread
import datetime
import time
from time import sleep
import RPi.GPIO as GPIO
import re
from rezgeto import Rezgeto
from rezgeto import *
import os

#Beallitasok
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledpin = 18
ledpin2 = 23
ledpin3 = 25
ledpin4 = 27

GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(ledpin2, GPIO.OUT)
GPIO.setup(ledpin3, GPIO.OUT)
GPIO.setup(ledpin4, GPIO.OUT)
pwm = GPIO.PWM(ledpin, 30)
pwm2 = GPIO.PWM(ledpin2, 30)
pwm3 = GPIO.PWM(ledpin3, 30)
pwm4 = GPIO.PWM(ledpin4, 30)

pwm_list = [pwm,pwm2,pwm3,pwm4]
print('Sikeres volt a setup!!')

"""
#Ethernet
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 8998))
s.listen(20)
print(f"Socket letrejott, hallgatozik a LAN cimen!")
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")
"""
#Halozat kiepitese      
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
port = 8998
s.bind((ipv4, port))
s.listen(20)
print(f"Socket letrejott, hallgatozik a {ipv4}:{port} cimen!")
rezegj = Rezgeto(pwm_list)
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")


def get_message(q,clientsocket,rezegj):
    while True:
        msg = clientsocket.recv(1024).decode("utf-8")
        #print("msg ciklus eleje msg")
        if msg:
            print("if message ", msg, " ", datetime.datetime.now())
            if msg == "1000":
                pass #Feladat: Pong visszaüzenetet küldeni
            ##################################
            else:
                q.put(msg)
                msg = False
        
def mainloop(q,clientsocket,rezegj):
    while True:
        if q.empty() == True:
            pass
        else:
            qmsg = q.get()
            print (qmsg, "main loop")
            code = rezegj.msg_divider(qmsg)
            print(f"Aktuális kód: {code}")
            if code == "vibe":
                rezegj.set_params_by_string(qmsg)
                rezegj.vibe_start()
                
    
""" 
# A thread that produces data 
def producer(out_q): 
    while True: 
        # Produce some data 
        ... 
        out_q.put(data) 
        
# A thread that consumes data 
def consumer(in_q): 
    while True: 
        # Get some data 
        data = in_q.get() 
        # Process the data 
        ... 
"""     

q = Queue() 
t1 = Thread(target = get_message, args =(q,clientsocket, rezegj)) 
t2 = Thread(target = mainloop, args =(q,clientsocket, rezegj)) 
t1.start() 
t2.start() 

s.close()
pwm.stop()

GPIO.cleanup()