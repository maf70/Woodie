#!/usr/bin/python
import time
import sys

import RPi.GPIO as GPIO
import smbus

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

    def __init__(self, devices):
        self.lcd = RPi_I2C_driver.lcd(i2cBus, r.i2cLCD)
        self.devices_list = devices
        self.dont_stop = 1

    def go(self):
          for el in self.devices_list :
            if el[0].modif != 0 :
              el[0].modif = 0
              ch = el[0].affiche()
              l = el[3] - len(ch)
              if l >= 0   : self.lcd.lcd_display_string_pos(ch+" "*l,el[2]+1,el[1])
              elif l < 0  : self.lcd.lcd_display_string_pos("#"*el[3],el[2]+1,el[1])

class AfficheurUnique():

    """Affichage : affichage d'un seul message"""

    def __init__(self, message):
        self.lcd = RPi_I2C_driver.lcd(r.i2cBusNum, r.i2cLCD)
        self.lcd.lcd_display_string_pos(message,4, 0)
        self.lcd.message(message)


class Thermo():

    """Thread : Read temperature """

    def __init__(self, label, device):
        self.device = device
        self.temperature = -1
        self.modif = 0
        self.label = label
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
        GPIO.remove_event_detect(self.port)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback=self.eCallback, bouncetime=self.rebond)
        self.compteur_prec = 0
        self.vitesse = 0
        self.valide = 0
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

    def tourne(self):
        return self.compteur - self.compteur_prec

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


class DetectSecteur(Thread):

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, label, port):
        Thread.__init__(self)
        self.label = label
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

class I2cAnalog():

    """Compteur : this object is a thread which count pulse from optical sensor"""

    def __init__(self, label, address):
        self.label = label
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


