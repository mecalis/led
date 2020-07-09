#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
from time import sleep
import socket
import os
from subprocess import call
import re
import asyncio



#Beallitasok
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledpin = 18
GPIO.setup(ledpin, GPIO.OUT)
pwm = GPIO.PWM(ledpin, 30)
pwm.start(0)
print('sikeres volt a setup, hálózat kiépítés kezdődik (2 sec delay)!')

class Rezgeto():
    def __init__(self):
        self.t = 0
        self.f = 0
        self.fred = 100
        self.dutyred = 60
        self.tbe = 0
        self.tred = 600
        self.string = ""
        self.t_stop = 0
        
        self.vibe_is_on = False
        self.red_is_on = False
        self.debugmode = True
        
        self.regex_codes = []
        self.regex_codes.append("^E,[1-5],[0-9]*,[0-9]*,[0-9]*,[0-9]*,V$")
        self.regex_codes.append("^I,[0-9]{3}\.[0-9]{3}\.[0-9]{1,3}\.[0-9]{1,3},[0-9]{1,4},V$")
        self.regex_codes.append("^E,V,V$")
        self.regex_out = ['vibe', 'ip', 'light']
        self.codes = list(zip(self.regex_codes, self.regex_out))
    
    def print_params(self):
        print (f"Aktualis feladat: Rezgetni {self.t} sec ideig, {self.f} 1/s frekvencian, {self.tbe} kitoltesi tenyezovel, {self.tred}s csillapítási idővel. ")
        
    def set_params_by_string(self, kapott_string):
        try:
            self.t, self.f, self.tbe, self.tred = kapott_string.split(',')[2:-1]
            self.t = int(self.t)/1000
            self.f = int(self.f)
            self.tbe = int(self.tbe)
            self.tred = int(self.tred)/1000
        except:
            pass
        pwm.ChangeDutyCycle(int(self.tbe))
        #pwm.ChangeFrequency(int(self.f))
        self.print_params()
    
    #Rezgetés indul
    def vibe_start(self):
        self.debug("vibe_start")
        t = time.time()
        self.t_stop = t + self.t
        self.tred_stop = self.t_stop + self.tred
        print(f"{t} kezdő idő\n" )
        print(f"{self.t_stop} rezgés vége")
        print(f"{self.tred_stop} csillapítás vége")
        self.vibe_is_on = True
        pwm.start(self.tbe)
        self.debug("vibe_start vége ")
        print(self.vibe_is_on)
        
    def vibe_stop(self):
        self.debug("vibe_stop")
        print("Rezgetés állj! csillapíts!")
        pwm.stop()
        self.vibe_is_on = False
        pwm.ChangeFrequency(int(self.fred))
        pwm.start(self.dutyred)
        self.red_is_on = True
        self.debug("vibe_stop vége")
    
    #Indulj újra
    def poweroff(self):
        call("sudo nohup shutdown -h now", shell=True)
        
    def reboot(self):
        call("sudo shutdown -r now")
    
    #Üzenetek ellenőrzése és kódolása
    def msg_divider(self, msg):
        self.debug("msg_divider")
        for code in self.codes:
            p = re.compile(code[0])
            talalat = p.findall(msg)
            if talalat:
                return code[1]
    #IP változtató script
    def ip_change(self, msg):
        self.debug("ip_change")
        new_ip = msg.split(',')[1]
        print("IP változtatás!")
        try:
            os.system('sudo ifconfig eth0 down')
            os.system(f"sudo ifconfig eth0 {newip}")
            os.system('sudo ifconfig eth0 up')
            print(f"IP átírva {new_ip}-ra!")
        except:
            print("Valami nem jött össze az ip átírása során!")
    
    #Világítás ki/be
    def light_onoff(self, msg):
        self.debug("light_onoff")
        print("Fény ki/be")
        
    def debug(self, mode):
        if self.debugmode == True:
            print(mode)
        
#Halozat kiepitese
WLAN = True
sleep(2)
if WLAN == False:
    se = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    se.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ipve4 = "192.168.1.150"
    ipve4 = "0.0.0.0"
    se.bind((ipve4, 8998))
    se.listen(20)
    print(f"Socket letrejott, hallgatozik a {ipve4} Ethernet cimen!")
    clientsockete, addresse = se.accept()
    print(f"Connection from {address} has been established.")
    
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
    s.bind((ipv4, 8997))
    s.listen(20)
    print(f"Socket letrejott, hallgatozik a {ipv4} WLAN cimen!")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")

rezegj = Rezgeto()



async def wait_msg(clientsocket):
    while True:
        print("wait_msg eleje")
        async def messs():
            msg_ = clientsocket.recv(1024).decode("utf-8")
            return msg_
        
        msg = await messs() 
        print("wait_msg vége")

async def mindenmas(clientsocket):
    while True:
        wait_msg(clientsocket)
        print("mindenmas elindult")
        if msg:
            print("if message")
            msg_id = rezegj.msg_divider(msg)
            
            if msg_id == 'vibe':
                #print(msg.decode("utf-8"))
                print(f"Kapott anyag {msg}")
                rezegj.set_params_by_string(msg)
                rezegj.vibe_start()
                end_message_1100 = bytes('1100', "utf-8")
                try:
                    clientsocket.sendto(end_message_1100, address)
                    print("Az 1100-as uzenet visszament a kliensnek!")
                except:
                    print("Az 1100-as uzenetet nem tudta visszakuldeni a kliensnek!")
                msg = False
                print("msg id msg törlés")

            #IP átírás
            if msg_id == 'ip':
                rezegj.ip_change(msg)
                msg = False
                
            #Fény ki/be    
            if msg_id == 'light':
                rezegj.light_onoff(msg)
                msg = False
                
        #Rezgés leállítása időre   
        if rezegj.vibe_is_on == True:
            print("if vibe is on")
            print(time.time())
            print(rezegj.t_stop)
            if time.time() > rezegj.t_stop:
                print("time.time >")
                pwm.stop()
                msg = False
                rezegj.vibe_stop()
            
        #Csillapítás leállítása időre
        if rezegj.red_is_on == True:
            if time.time() > rezegj.tred_stop:
                pwm.stop()
                msg = False
                rezegj.red_is_on = False
                
        # PI kikapcsolás        
        if msg == "E,poweroff,V":
            rezegj.poweroff()
            
        if msg == "E,reboot,V":
            rezegj.reboot()
        print("main ciklus vége")
        await asyncio.sleep(0.1)
            

async def MAIN():
    await asyncio.gather(mindenmas(clientsocket))

asyncio.run(MAIN())

#pwm.stop()

#GPIO.cleanup()

