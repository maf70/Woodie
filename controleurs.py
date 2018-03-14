#!/usr/bin/python
import time
import sys
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

from threading import Thread
import reglages as r
from reglages import ON as ON
from reglages import OFF as OFF


class controleur(Thread):

    """Simple control for fire fan: 1 output without feedback"""

    def __init__(self, sortie, tCycle, tDecale):
        Thread.__init__(self)
        self.sortie = sortie
        self.tCycle = tCycle
        self.tDecale = tDecale
        self.commande = OFF
        self.dont_stop = 1
        self.arret()

    def run(self):
        while self.dont_stop == 1 :
          if self.commande == ON :
            if self.tDecale > 0 : time.sleep(self.tDecale)
            while self.duree > 0 and self.dont_stop == 1:
              time.sleep(self.tCycle)
              self.duree -= self.tCycle
              if self.duree < 0 : self.duree = 0
            self.arret()
          time.sleep(self.tCycle)
          
    def demarre(self, duree):
        self.commande = ON
        self.duree = duree
        self.marche()
          
    def stoppe(self):
        self.commande = OFF
        self.duree = 0
        self.arret()

    def marche(self):
        self.sortie.on()

    def arret(self):
        self.sortie.off()

    def etat( self, s ):
        self.dont_stop = s

    def affiche( self ):
        return ""

    def log( self ):
        return self.commande


class controleurMoteur(Thread):

    """Feedbak control (for motor) :
            1 output for normal direction
            1 output for reverse direction when a blocking state is detected (need 2 pulses counters)
            Stop and alert if motor completely blocked """

    def __init__(self, sortie, compteur, vMin, inverse, tCycle, tInverse, nInverse, tDecale):
        Thread.__init__(self)
        self.cmd = sortie
        self.cmdInverse = inverse
        self.compteur = compteur
        self.vMin = vMin
        self.tCycle = tCycle
        self.tInverse = tInverse
        self.nInverse = nInverse
        self.tDecale = tDecale
        self.commande = OFF
        self.duree = 0
        self.arret()

        self.dont_stop = 1
        self.vitesse = 0
        self.phase = 0

    def run(self):
        while self.dont_stop == 1 :
          if self.commande == ON :
            self.compteur.raz()
            self.phase = 0
            if self.tDecale > 0 : time.sleep(self.tDecale)
            self.marche()
            while self.duree > 0  and self.dont_stop == 1:
              time.sleep(self.tCycle)
              self.duree -= self.tCycle
              if self.phase == 0 : self.phase = 1      # on laisse 1 cycle pour que le moteur demarre
              else :
                if self.duree < 0 : self.duree = 0
                if self.compteur.valeur() < self.vMin :
                  # Detection d'un blocage
                  # print "Detection blocage"
                  self.arret()
                  time.sleep(3)

                  self.inverse()
                  time.sleep(self.tInverse)

                  self.arret()
                  time.sleep(3)

                  self.marche()

                  # 1 cycle pour redemarrage moteur
                  self.phase = 0

            self.arret()
            self.commande = OFF
          time.sleep(self.tCycle)

    # Commandes venant de la chaudiere
    def demarre(self, duree):
        self.commande = ON
        self.duree = duree

    def stoppe(self):
        self.commande = OFF
        self.duree = 0
        self.arret()

    def etat( self, s ):
        self.dont_stop = s

    # Commandes appelees par le controleur lui-meme
    def marche(self):
        # On met toujours toutes les sorties a OFF avant de commuter la derniere
        self.cmdInverse.off()
        self.cmd.on()

    def arret(self):
        self.cmd.off()
        self.cmdInverse.off()

    def inverse(self):
        self.cmd.off()
        self.cmdInverse.on()

    # Affichage et log
    def affiche( self ):
        return ""

    def log( self ):
        if self.commande == OFF :
          return "0"
        elif self.cmd.valeur() == 1 and self.cmdInverse.valeur() == 0:
          return "1"
        elif self.cmd.valeur() == 0 and self.cmdInverse.valeur() == 0:
          return "B"
        elif self.cmd.valeur() == 0 and self.cmdInverse.valeur() == 1:
          return "I"
        else :
          # On ne doit pas arriver ici : les 2 relais sont actifs ou les GPIOS ont un pb !!!!!
          # On coupe tout
          self.stoppe()
          return "E"









