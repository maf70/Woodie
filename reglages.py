#!/usr/bin/python

import json


################################
#  Reglages de fonctionnement
################################

class Params():

    """Recuperation / sauvegarde parametres """

    def __init__(self, fichier = "defaut.json"):
      self.fichier = fichier

      self.etat = ""

      try :
        conf=json.load(open(fichier))

      except IOError:
        self.etat = "E:ConfFile"

      else :
        try :
          # Temperature demarrage / arret cycle de chauffe
          self.tStart = conf["tStart"]["valeur"]
          self.tStop  = conf["tStop"]["valeur"]

          # Temperature vis securite
          self.tSecu  = conf["tSecu"]["valeur"]

          # Duree d'un cycle en seconde
          self.dCycle   = conf["dCycle"]["valeur"]
          self.dVentilo = conf["dVentilo"]["valeur"]
          self.dMoteur  = conf["dMoteur"]["valeur"]

          # Parametres moteur
          self.cycleMoteur = conf["cycleMoteur"]["valeur"]
          self.vMin        = conf["vMin"]["valeur"]
          self.dInverse    = conf["dInverse"]["valeur"]
          self.nInverse    = conf["nInverse"]["valeur"]
          self.dDecalage   = conf["dDecalage"]["valeur"]

          # Specifique
          self.sondeTempEau = conf["sondeTempEau"]["valeur"]
          self.sondeTempMot = conf["sondeTempMot"]["valeur"]

        except KeyError:
          self.etat = "E:ConfErr"



################################
#  "Constantes communes"
################################

ON=0
OFF=1
PAUSE=2

################################
#  Cablage. Non modifiable.
################################

# Configuration des gpio pour la commande des relais
# !! Numerotation Broadcom !!
# Board equivalent : 12 11 13 15
r1 = 25
r2 = 24
r3 = 23
r4 = 18

# Software SPI configuration.
# !! Numerotation Broadcom !!
SpiCLK = 10     # r8
SpiCS  =  9     # r7
SpiDO  = 11     # r6

# Configuration des gpio pour les compteurs
# !! Numerotation Broadcom !!
# Board equivalent : 37 18
b1 = 20
b2 = 21

# Configuration des gpio pour les detecteurs secteur
# !! Numerotation Broadcom !!
# Board equivalent : 21 19
d1 = 16
d2 = 12

# Configuration gpio led
# !! Numerotation Broadcom !!
l1 = 26

# Configuration gpio poussoir
# !! Numerotation Broadcom !!
p1 = 8

# Configuration des gpio  du lcd
# !! Numerotation Broadcom !!
#lcd_rs        = 20
#lcd_en        = 16
#lcd_d4        = 19
#lcd_d5        = 13
#lcd_d6        = 12
#lcd_d7        = 5
#lcd_backlight = 21

# Bus i2c & addresses
i2cBusNum = 1
i2cNano   = 0x08
i2cLCD    = 0x3f



