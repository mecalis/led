import re
import time


class Rezgeto():
    def __init__(self, pwm_list):
        self.t = 0 #Rezgetés ideje
        self.f = 0 #Rezgetés frekvenciája
        self.fred = 100
        self.dutyred = 60
        self.tbe = 0  #Duty time
        self.tred = 600
        self.string = ""
        self.t_stop = 0
        self.mode = 0
        
        self.pwm_list = pwm_list
        self.pwm_to_vibe = []
        
        self.debugmode = True
        
        self.regex_codes = []
        self.regex_codes.append("^E,[1-5],[0-9]*,[0-9]*,[0-9]*,[0-9]*,V$")
        self.regex_codes.append("^I,[0-9]{3}\.[0-9]{3}\.[0-9]{1,3}\.[0-9]{1,3},[0-9]{1,4},V$")
        self.regex_codes.append("^E,V,V$")
        self.regex_out = ['vibe', 'ip', 'light']
        self.codes = list(zip(self.regex_codes, self.regex_out))
        print("Rezgető modul betöltve")
    
    def print_params(self):
        print (f"Aktualis feladat: Rezgetni {self.t} sec ideig, {self.f} 1/s frekvencian, {self.tbe} kitoltesi tenyezovel, {self.tred}s csillapítási idővel. ")
        
    def set_params_by_string(self, kapott_string):
        try:
            self.mode, self.t, self.f, self.tbe, self.tred = kapott_string.split(',')[1:-1]
            self.t = int(self.t)/1000
            self.f = int(self.f)
            self.tbe = int(self.tbe)
            self.tred = int(self.tred)/1000
            self.pwm_to_vibe = []
            if self.mode == 1:
                self.pwm_to_vibe = self.pwm_list
                print("Beállítva mind!")
            if self.mode == 2:
                self.pwm_to_vibe.append(self.pwm_list[2])
                self.pwm_to_vibe.append(self.pwm_list[3])
                print("Beállítva a jobb oldal")
            if self.mode == 3:
                self.pwm_to_vibe.append(self.pwm_list[0])
                self.pwm_to_vibe.append(self.pwm_list[1])
                print("Beállítva a bal oldal")
            if self.mode == 4:
                self.pwm_to_vibe.append(self.pwm_list[1])
                self.pwm_to_vibe.append(self.pwm_list[2])
                print("Beállítva a bal oldal")
            if self.mode == 5:
                self.pwm_to_vibe.append(self.pwm_list[0])
                self.pwm_to_vibe.append(self.pwm_list[3])
                print("Beállítva a bal oldal")
                
        except:
            print("A paraméterek beállítása során valami hibára ment!")
        
        self.print_params()
    
    def set_pwm(self, pwm_list, mode):
        if mode == 'start':
            for pwm in pwm_list:
                pwm.ChangeFrequency(int(self.f))
                pwm.start(int(self.tbe))
            print("Kimenetek beállítva: START")
        if mode == 'stop':
            for pwm in pwm_list:
                pwm.stop()
            print("Kimenetek beállítva: STOP")

    #Rezgetés indul
    def vibe_start(self):
        self.debug("vibe_start")
        t = time.time()
        self.t_stop = t + self.t
        self.tred_stop = self.t_stop + self.tred
        print(f"{t} kezdő idő" )
        print(f"{self.t_stop} rezgés vége")
        print(f"{self.tred_stop} csillapítás vége")
        self.set_pwm(self.pwm_list, 'start')
        time.sleep(self.t)
        self.set_pwm(self.pwm_list, 'stop')
        self.debug("vibe_start vége ")

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