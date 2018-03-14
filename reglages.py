#!/usr/bin/python

################################
#  Reglages de fonctionnement
################################

class Params():

    """Recuperation / sauvegarde parametres """

    def __init__(self, fichier = "defaut.txt"):
      self.fichier = fichier

      # Temperature demarrage / arret cycle de chauffe
      self.tStart = 58
      self.tStop  = 60

      # Temperature vis securite
      self.tSecu  = 60

      # Duree d'un cycle en seconde
      self.dCycle   = 300
      self.dVentilo = 240
      self.dMoteur  = 40

      # Parametres moteur
      self.cycleMoteur = 1
      self.vMin        = 2      # impulsion minimum par temps de cycle
      self.dInverse    = 3      # Duree inversion (s)
      self.nInverse    = 3      # Nombre max d'inversion
      self.dDecalage   = 0.2    # Duree avant demarrage, decale les demarrages des differents moteurs

      # Specifique
      self.sondeTempEau = "28-0417c1418bff"
      self.sondeTempMot = "28-0517c1392fff"


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


