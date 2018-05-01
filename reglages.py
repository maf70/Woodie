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
r1 = 18
r2 = 17
r3 = 27
r4 = 22

# Configuration des gpio pour les compteurs
# !! Numerotation Broadcom !!
# Board equivalent : 37 18
b1 = 26
b2 = 24

# Configuration des gpio pour les detecteurs secteur
# !! Numerotation Broadcom !!
# Board equivalent : 21 19
d1 = 9
d2 = 10

# Configuration des gpio  du lcd
# !! Numerotation Broadcom !!
lcd_rs        = 20
lcd_en        = 16
lcd_d4        = 19
lcd_d5        = 13
lcd_d6        = 12
lcd_d7        = 5
lcd_backlight = 21

# 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2


