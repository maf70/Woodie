#!/usr/bin/python

import ConfigParser


################################
#  Reglages de fonctionnement
################################

class Params():

    """Recuperation / sauvegarde parametres """

    def __init__(self, fichier = "defaut.txt"):
      self.fichier = fichier

      self.etat = ""

      config = ConfigParser.ConfigParser()
      config.read(fichier)

      try :
        # Temperature demarrage / arret cycle de chauffe
        self.tStart = config.getint('DEFAULT','tStart')
        self.tStop  = config.getint('DEFAULT','tStop')

        # Temperature vis securite
        self.tSecu  = config.getint('DEFAULT','tSecu')

        # Duree d'un cycle en seconde
        self.dCycle   = config.getint('DEFAULT','dCycle')
        self.dVentilo = config.getint('DEFAULT','dVentilo')
        self.dMoteur  = config.getint('DEFAULT','dMoteur')

        # Parametres moteur
        self.cycleMoteur = config.getint('DEFAULT','cycleMoteur')
        self.vMin        = config.getint('DEFAULT','vMin')
        self.dInverse    = config.getint('DEFAULT','dInverse')
        self.nInverse    = config.getint('DEFAULT','nInverse')
        self.dDecalage   = config.getfloat('DEFAULT','dDecalage')

        # Specifique
        self.sondeTempEau = config.get('DEFAULT','sondeTempEau')
        self.sondeTempMot = config.get('DEFAULT','sondeTempMot')

      except ConfigParser.NoOptionError:
        self.etat = "E:Config"



################################
#  "Constantes communes"
################################

ON=0
OFF=1

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


