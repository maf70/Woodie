#!/usr/bin/python
import time
import sys
import os

import RPi.GPIO as GPIO
import smbus

import Adafruit_MAX31855.MAX31855 as MAX31855

from threading import Thread
import reglages as r
from reglages import ON as ON
from reglages import OFF as OFF

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

import RPi_I2C_driver

# Bus i2c
i2cBus = smbus.SMBus(r.i2cBusNum)
GPIO.cleanup()

class Afficheur():

    """Classe affichage : track all devices change and display it when occurs"""

    def __init__(self, c, l, defaut, devices):
        self.devices_list = devices
        self.defaut_list = defaut
        self.ligne = l
        self.col = c
        self.shadow = defaut
        self.etat = 0
        self.dont_stop = 1
        i = 0
        while i < self.ligne:
          self.shadow[i] = list( self.defaut_list[i] + (self.col-len(self.shadow[i])) * " ")
          i += 1

    def go(self):
          if self.etat == 0 :
            try:
              self.lcd = RPi_I2C_driver.lcd(i2cBus, r.i2cLCD)
              self.etat = 1
            except :
              self.etat = 0

          if self.etat == 1 :
            try:
              self.lcd.lcd_reinit()
              self.lcd.lcd_clear()
              self.etat = 2
            except :
              self.etat = 1
            i = 1
            for el in self.defaut_list :
              try:
                self.lcd.lcd_display_string_pos(el,i,0)
              except :
                self.etat = 1
              i += 1

          for el in self.devices_list :
            if el[0].modif != 0 :
              el[0].modif = 0
              ch = el[1]()
              l = el[4] - len(ch)
              if l >= 0   : txt=ch+" "*l
              elif l < 0  : txt="#"*el[4]
              i = 0
              while i < len(txt):
                self.shadow[el[3]][el[2]+i] = txt[i]
                i += 1
              if self.etat > 1 :
                try:
                  self.lcd.lcd_display_string_pos(txt,el[3]+1,el[2])
                except :
                  self.etat = 1

class AfficheurUnique():

    """Affichage : affichage d'un seul message"""

    def __init__(self, message):
        self.lcd = RPi_I2C_driver.lcd(r.i2cBusNum, r.i2cLCD)
        self.lcd.lcd_display_string_pos(message,4, 0)
        self.lcd.message(message)


class Thermo():

    """Thread : Read temperature """

    def __init__(self, device):
        self.device = device
        self.temperature = -1
        self.modif = 0
        self.valide = 0

    def go(self):
          try :
            f=open("/sys/bus/w1/devices/"+self.device+"/w1_slave","r")
            line = f.readline()
            line = f.readline()
            s = line.split("=")
            self.temperature = int(s[1]) / 1000
            f.close()
            self.modif = 1
            self.valide = 1

          except IOError:
            self.valide = 0

    def valeur(self):
        return self.temperature

    def affiche(self):
        return str(self.temperature)

    def log(self):
        return str(self.temperature)

class Entree():

    """Manage a GPIO as an input, and functions to check / display / log """

    def __init__(self, port, rebond):
        self.port = port
        self.val = 2
        self.rebond = rebond
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.modif = 0
        self.prec  = 0

    def valeur(self):
        self.val = GPIO.input(self.port)^1
        if self.val != self.prec : self.modif = 1
        self.prec = self.val
        return self.val

    def affiche(self):
        return str(self.val)

    def log(self):
        return str(GPIO.input(self.port)^1)

class Compteur(Thread):

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, port, vMin, rebond):
        Thread.__init__(self)
        self.port = port
        self.vMin = vMin
        self.nbBlock = 0
        self.rebond = rebond
        self.compteur = 0
        self.modif = 0
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        self.compteur_prec = 0
        self.vitesse = 0
        self.valide = 0
        self.on()
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          self.vitesse = self.compteur - self.compteur_prec
          self.modif = 1
          if self.vitesse == 0 : self.compteur = 0
          self.compteur_prec = self.compteur
          time.sleep(0.5)
          self.valide += 0.5

    def eCallback(self, b):
        if (b==self.port):
          self.compteur += 1

    def on(self):
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.eCallback, bouncetime=self.rebond) 
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.eCallback, bouncetime=self.rebond)
        self.compteur_prec = 0
        self.vitesse = 0
        self.valide = 0

    def off(self):
        GPIO.remove_event_detect(self.port)

    def tourne(self):
        return self.compteur - self.compteur_prec

    def incBlock(self):
        self.nbBlock += 1
        self.modif = 1

    def razBlock(self):
        self.nbBlock = 0

    def raz(self):
        self.compteur = 0
        self.compteur_prec = 0
        self.valide = 0
        self.modif = 1

    def etat( self, s ):
        self.dont_stop = s

    def valeur(self):
        return self.vitesse

    def affiche(self):
        return str(self.vitesse)+"/"+str(self.nbBlock)

    def log(self):
        return str(self.vitesse)

class Sortie():

    """Manage a GPIO as an output, and provide functions to check / display / log """


    def __init__(self,  port):
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

class Led():

    """Manage a GPIO to pilot a led. Active state is 0 """


    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT)
        GPIO.output(self.port,0)

    def on(self):
        GPIO.output(self.port,1)

    def off(self):
        GPIO.output(self.port,0)


class DetectSecteur(Thread):

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, port):
        Thread.__init__(self)
        self.port = port
        self.rebond = 500
        self.secteur = 0
        self.modif = 0
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          time.sleep(1)
          compteur = 40
          while compteur > 0 :
            compteur -= 1
            if GPIO.input(self.port) == 0 :
              if self.secteur == 0 :
                self.modif = 1
              self.secteur = 1
              break
            time.sleep(0.001)
          if compteur == 0 :
            self.secteur = 0
            self.modif = 1

    def etat( self, s ):
        self.dont_stop = s

    def valeur(self):
        return self.secteur

    def affiche(self):
        if self.secteur > 0 : return "1"
        return "0"

    def log(self):
        return str(self.secteur)

class SpiSondeK(Thread):

    """Compteur : this object is a thread which access thermocouple sensor via software SPI"""

    def __init__(self, CLK, CS, DO):
        Thread.__init__(self)
        self.CLK = CLK
        self.CS = CS
        self.DO = DO
        self.val = 0
        self.modif = 0
        self.valide = 0
        self.dont_stop = 1
        self.lastT = []
        self.mm = 0
        self.sensor = MAX31855.MAX31855(self.CLK, self.CS, self.DO)

    def run(self):
        while self.dont_stop == 1 :
          valeur = self.val
          try :
            val = int(self.sensor.readTempC())
            self.valide = 1

          except :
            self.valide = 0

          if self.valide and val > 0 :

            # Limit variation at a max of 50 degrees each second
            if val > self.val + 50 :
              val = self.val + 50
            if val < self.val - 50 :
              val = self.val - 50

            self.val = val
            self.lastT.append(val)
            l = len(self.lastT)
            if l > 5 :
              self.lastT.pop(0)
              l -= 1
            s = 0
            for v in self.lastT:
              s += v
            self.mm = s / l

          if valeur != self.val :
            self.modif = 1


          time.sleep(1)

    def valeur(self):
        return self.mm

    def affiche(self):
        return str(self.mm)

    def log(self):
        return str(self.val)+";"+str(self.mm)

    def etat( self, s ):
        self.dont_stop = s


class I2cAnalog():

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, address):
        self.address = address
        self.valeur = 0
        self.modif = 0
        self.valide = 0

    def go(self):
          valeur = self.valeur
          try :
            self.valeur = i2cBus.read_byte_data(self.address, 1)
            self.valide = 1

          except IOError:
            self.valide = 0

          if valeur != self.valeur :
            self.modif = 1

    def valeur(self):
        return self.valeur

    def affiche(self):
        return str(self.valeur)

    def log(self):
        return str(self.valeur)

class I2cManager(Thread):

    """Thread : Give the go for each i2c device to access the bus"""

    def __init__(self, devices):
        Thread.__init__(self)
        self.devices = devices
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          for el in self.devices :
            el[0].go()
            time.sleep(el[1])
          try :
            f = open("/mnt/data/info_i2c.txt"  "r")
            f.close
          except IOError :
            os.system("i2cdetect -y 1 > /mnt/data/info_i2c.txt")
            time.sleep(0.1)

    def etat( self, s ):
        self.dont_stop = s


class DallasManager(Thread):

    """Thread : Give the go for each Dallas device to access the bus"""

    def __init__(self, devices):
        Thread.__init__(self)
        self.devices = devices
        self.dont_stop = 1

    def run(self):
        while self.dont_stop == 1 :
          for el in self.devices :
            el[0].go()
            time.sleep(el[1])

    def etat( self, s ):
        self.dont_stop = s


