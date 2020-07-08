#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
from time import sleep
import socket
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

class Rezgeto():
    def __init__(self, t=5000, f=25, tbe=35):
        self.t = t/1000
        self.f = f
        self.tbe = tbe
        self.string = ""
        self.t_stop = 0
    
    def print_params(self):
        print (f"Aktualis feladat: Rezgetni {self.t} sec ideig {self.f} 1/s frekvencian {self.tbe}  kitoltesi tenyezovel")
        
    def set_params_by_string(self, kapott_string):
        try:
            self.t, self.f, self.tbe = kapott_string.split(',')[2:-2]
            self.t = int(self.t)/1000
            self.f = int(self.f)
            self.tbe = int(self.tbe)
        except:
            pass
        pwm.ChangeDutyCycle(int(self.tbe))
        pwm.ChangeFrequency(int(self.f))
        pwm2.ChangeDutyCycle(int(self.tbe))
        pwm2.ChangeFrequency(int(self.f))
        pwm3.ChangeDutyCycle(int(self.tbe))
        pwm3.ChangeFrequency(int(self.f))
        pwm4.ChangeDutyCycle(int(self.tbe))
        pwm4.ChangeFrequency(int(self.f))
        self.print_params()
    
    def blink(self):
        t = time.time()
        self.t_stop = t + self.t
        print(f"{t} kezdő idő\n" )
        print(f"{self.t_stop} rezgés vége {self.tbe} ")
        pwm.start(self.tbe)
        pwm2.start(self.tbe)
        pwm3.start(self.tbe)
        pwm4.start(self.tbe)
        while time.time() < self.t_stop:
            sleep(0.1)
        pwm.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()
        
#Halozat kiepitese      
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((socket.gethostname(), 8991))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.bind(("169.254.229.228", 8991))
ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
#s.bind(("192.168.1.161", 8991))
port = 8998
s.bind((ipv4, port))
s.listen(20)
print(f"Socket letrejott, hallgatozik a {ipv4}:{port} cimen!")
rezegj = Rezgeto()
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")

while True:
    msg = clientsocket.recv(1024).decode("utf-8")
    if msg:
        #print(msg.decode("utf-8"))
        print(f"Kapott anyag {msg}")
        rezegj.set_params_by_string(msg)
        rezegj.blink()
        msg = False
        print("Rezges vege!")
        end_message_1100 = bytes('1100', "utf-8")
        try:
            clientsocket.sendto(end_message_1100, address)
            print("Az 1100-as uzenet visszament a kliensnek!")
        except:
            print("Az 1100-as uzenetet nem tudta visszakuldeni a kliensnek!")
        
        
    
pwm.stop()

GPIO.cleanup()
