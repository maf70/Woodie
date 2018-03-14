#!/usr/bin/python
import time
import sys

import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

from threading import Thread
import reglages as r
from reglages import ON as ON
from reglages import OFF as OFF

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

class Afficheur(Thread):

    """Thread affichage : track all devices change and display it when occurs"""

    def __init__(self, devices):
        Thread.__init__(self)
        self.lcd = LCD.Adafruit_CharLCD(r.lcd_rs, r.lcd_en, r.lcd_d4, r.lcd_d5, r.lcd_d6, r.lcd_d7,
                           r.lcd_columns, r.lcd_rows, r.lcd_backlight)
        self.texte = []
        for j in range(r.lcd_rows):
          self.texte.append(r.lcd_columns*[" "])
        self.devices_list = devices
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          for el in self.devices_list :
            if el[0].modif != 0 :
              el[0].modif = 0
              self.lcd.set_cursor(el[1], el[2])
              ch = el[0].affiche()
              l = el[3] - len(ch)
              if l >= 0   : self.lcd.message(ch+" "*l)
              elif l < 0  : self.lcd.message("#"*el[3])
          time.sleep(0.5)

    def etat( self, s ):
        self.dont_stop = s

class Thermo(Thread):

    """Thread : Read temperature """

    def __init__(self, device):
        Thread.__init__(self)
        self.device = device
        self.temperature = -1
        self.dont_stop = 1
        self.modif = 0
        self.valide = 0

    def run(self):
        while self.dont_stop == 1 :
          try :
            f=open("/sys/bus/w1/devices/"+self.device+"/w1_slave","r")
            line = f.readline()
            line = f.readline()
            s = line.split("=")
            self.temperature = int(s[1]) / 1000
            f.close()
            self.modif = 1
            self.valide = 1

          except KeyboardInterrupt:
            self.valide = 0

          time.sleep(3)


    def etat( self, s ):
        self.dont_stop = s

    def valeur(self):
        return self.temperature

    def affiche(self):
        return str(self.temperature)

    def log(self):
        return str(self.temperature)

class Entree():

    """Manage a GPIO as an input, and functions to check / display / log """

    def __init__(self, label, port, rebond):
        self.label = label
        self.port = port
        self.rebond = rebond
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def valeur(self):
        return GPIO.input(self.port)^1

    def affiche(self):
        return str(GPIO.input(self.port)^1)

    def log(self):
        return str(GPIO.input(self.port)^1)

class Compteur(Thread):

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, label, port, rebond):
        Thread.__init__(self)
        self.label = label
        self.port = port
        self.rebond = rebond
        self.compteur = 0
        self.modif = 0
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.eCallback, bouncetime=self.rebond) 
        self.compteur_prec = 0
        self.vitesse = 0
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          self.vitesse = self.compteur - self.compteur_prec
          self.modif = 1
          if self.vitesse == 0 : self.compteur = 0
          self.compteur_prec = self.compteur
          time.sleep(0.5)

    def eCallback(self, b):
        if (b==self.port):
          self.compteur += 1

    def tourne(self):
        return self.compteur - self.compteur_prec

    def raz(self):
        self.compteur = 0
        self.modif = 1

    def etat( self, s ):
        self.dont_stop = s

    def valeur(self):
        return self.vitesse

    def affiche(self):
        return str(self.vitesse)

    def log(self):
        return str(self.vitesse)

class Sortie():

    """Manage a GPIO as an output, and provide functions to check / display / log """


    def __init__(self, label, port):
        self.label = label
        self.port = port
        self.etat = OFF
        self.modif = 0
        GPIO.setup(self.port, GPIO.OUT)
        GPIO.output(self.port,self.etat)

    def on(self):
        self.modif = 1
        self.etat = ON
        GPIO.output(self.port,self.etat)

    def off(self):
        self.modif = 1
        self.etat = OFF
        GPIO.output(self.port,self.etat)

    def valeur(self):
        return GPIO.input(self.port)^1

    def affiche(self):
        return str(GPIO.input(self.port)^1)

    def log(self):
        return str(GPIO.input(self.port)^1)











