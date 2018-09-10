#!/usr/bin/python
import time
import sys
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

from threading import Thread
import reglages as r
from reglages import ON as ON
from reglages import OFF as OFF
from reglages import PAUSE as PAUSE


class controleur(Thread):

    """Simple control for fire fan: 1 output without feedback"""

    def __init__(self, sortie, tCycle, tDecale):
        Thread.__init__(self)
        self.sortie = sortie
        self.tCycle = tCycle
        self.tDecale = tDecale
        self.commande = OFF
        self.duree = 0
        self.dont_stop = 1
        self.arret()

    def run(self):
        while self.dont_stop > 0 :
          if self.commande == ON :
            self.marche()
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

    def pause(self, p):
      if self.commande != OFF :
        if p == 1 :
          self.dont_stop = 2
          self.commande = PAUSE
          self.arret()
        elif self.commande == PAUSE :
          self.dont_stop = 1
          self.commande = ON

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

    def __init__(self, sortie, compteurs, inverse, tCycle, tInverse, nInverse, tDecale):
        Thread.__init__(self)
        self.cmd = sortie
        self.cmdInverse = inverse
        self.compteur_list = compteurs
        self.tCycle = tCycle
        self.tInverse = tInverse
        self.nInverse = nInverse
        self.tDecale = tDecale
        self.commande = OFF
        self.duree = 0
        self.blocage = 0
        self.arret()

        self.dont_stop = 1
        self.vitesse = 0
        self.phase = 0
        self.StatNbBlocages = 0
        self.modif = 1

    def run(self):
        while self.dont_stop > 0 :
          if self.commande == ON and self.blocage == 0:
            for el in self.compteur_list :
              el.raz()
            self.phase = 0
            nbBlocage = 0
            if self.tDecale > 0 : time.sleep(self.tDecale)
            self.marche()
            compteur_local = 0
            while self.duree > 0  and self.dont_stop == 1:
              time.sleep(self.tCycle)

              if self.phase == 0 :        ### Tempo : attend validite des compteurs (1s)
                self.duree -= self.tCycle
                compteur_local += self.tCycle
                if  compteur_local >= 1 :
                  self.phase = 1

              elif self.phase == 1 :      ### Rotation normale
                self.duree -= self.tCycle
                blocage = 0
                for el in self.compteur_list :
                  if el.valeur() < el.vMin :
                    el.incBlock()
                    blocage = 1
                if blocage :
                  # Detection d'un blocage
                  nbBlocage += 1
                  self.StatNbBlocages += 1
                  self.modif = 1
                  self.arret()
                  compteur_local = 0
                  self.phase = 2
                if nbBlocage >= self.nInverse :
                  self.phase = 10

              elif self.phase == 2 :      ### Tempo avant inversion
                compteur_local += self.tCycle
                if  compteur_local > 2 :
                  self.inverse()          # Demarrage inverse 1s avant fin tempo
                if  compteur_local > 3 :
                  self.phase = 3
                  compteur_local = 0

              elif self.phase == 3 :      ### Rotation inverse
                blocage = 0
                for el in self.compteur_list :
                  if el.valeur() < el.vMin :
                    el.incBlock()
                    blocage = 1
                if blocage :
                  # Detection d'un blocage
                  nbBlocage += 1
                  self.StatNbBlocages += 1
                  self.modif = 1
                  self.arret()
                  compteur_local = 0
                  self.phase = 4
                compteur_local += self.tCycle
                if compteur_local > self.tInverse :
                  self.arret()
                  compteur_local = 0
                  self.phase = 4
                if nbBlocage >= self.nInverse :
                  self.phase = 10

              elif self.phase == 4 :      ### Tempo avant reprise
                compteur_local += self.tCycle
                if  compteur_local > 3 :
                  self.phase = 0
                  compteur_local = 0
                  self.marche()

              elif self.phase >= 5 :      ### Blocage general
                  self.arret()
                  self.blocage = 1
                  self.duree = 0

            self.arret()
            if self.duree == 0 : self.commande = OFF
          time.sleep(self.tCycle)

    # Commandes venant de la chaudiere
    def estBloque(self):
        return self.blocage

    def estInverse(self):
        if self.phase >= 2 :
          return 1
        return 0

    def debloque(self):
        self.blocage = 0

    def demarre(self, duree):
        self.commande = ON
        self.duree = duree

    def stoppe(self):
        self.commande = OFF
        self.duree = 0
        self.arret()

    def pause(self, p):
      if self.commande != OFF :
        if p == 1 :
          self.dont_stop = 2
          self.commande = PAUSE
          self.arret()
        elif self.commande == PAUSE :
          self.dont_stop = 1
          self.commande = ON

    def etat( self, s ):
        self.dont_stop = s

    # Commandes appelees par le controleur lui-meme
    def marche(self):
        # On met toujours toutes les sorties a OFF avant de commuter la derniere
        self.cmdInverse.off()
        self.cmd.on()
#        for el in self.compteur_list :
#          el.on()

    def arret(self):
#        for el in self.compteur_list :
#          el.off()
        self.cmd.off()
        self.cmdInverse.off()

    def inverse(self):
        self.cmd.off()
        self.cmdInverse.on()
#        for el in self.compteur_list :
#          el.on()

    # Affichage et log
    def RazStats( self ):
        self.StatNbBlocages = 0
        self.modif = 1

    def affiche( self ):
        return str(self.StatNbBlocages)

    def log( self ):
        if self.commande == OFF :
          return "0"
        elif self.phase == 10 :
          return "B"
        elif self.cmd.valeur() == 1 and self.cmdInverse.valeur() == 0:
          return "1"
        elif self.cmd.valeur() == 0 and self.cmdInverse.valeur() == 0:
          return "t"
        elif self.cmd.valeur() == 0 and self.cmdInverse.valeur() == 1:
          return "I"
        else :
          # On ne doit pas arriver ici : les 2 relais sont actifs ou les GPIOS ont un pb !!!!!
          # On coupe tout
          self.stoppe()
          return "E"









