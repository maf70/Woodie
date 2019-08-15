#!/usr/bin/python
import time
import os
import sys

from threading import Thread

import reglages
from reglages import ON as ON
from reglages import OFF as OFF
import hw
import logic
import controleurs
import traceur as trace
import serveur.serveur as serv

import json

class woodie_legacy(Thread):

    """woodie_legacy : Chaudiere inside ! """

    def __init__(self, fichier_param = "config.json"):
        Thread.__init__(self)

        self.phase = "not set"
        self.fichier_param = fichier_param

        # Lecture fichier config
        try :
          self.conf=json.load(open(fichier_param))

        except IOError:
          self.setPhase("E:ConfFile")
          afficheurU = hw.AfficheurUnique(self.phase)
          # On ne sort pas ...
          while 1:
            time.sleep(3)

        self.rep      = "/mnt/data/LOGS/WOODIE/"

        self.dateur   = logic.dateur()

        self.ventilo  = hw.Sortie( reglages.r1)
        self.moteur   = hw.Sortie( reglages.r2)
        self.inverse  = hw.Sortie( reglages.r3)
# pas utilise, force la sortie a OFF
        self.reserve  = hw.Sortie( reglages.r4)

        self.listeCapteurs = []
        self.capteurVis  = hw.Compteur( reglages.b1, self.config( "vMinVis" ), 10)
        if self.config( "vMinVis" ) > 0 :
          self.listeCapteurs.append(self.capteurVis)
        self.capteurTremie = hw.Compteur( reglages.b2, self.config( "vMinTremie" ), 10)
        if self.config( "vMinTremie" ) > 0 :
          self.listeCapteurs.append(self.capteurTremie)

        self.t_eau = hw.Thermo( self.config( "sondeTempEau" ))
        self.t_secu = hw.Thermo( self.config( "sondeTempMot" ))
        self.dallasManager = hw.DallasManager( [ [self.t_eau, 3 ], [self.t_secu, 3 ] ] )


        self.d_secteur = hw.DetectSecteur( reglages.d1)
        self.d_secuMeca = hw.DetectSecteur( reglages.d2)

#        self.analog = hw.I2cAnalog( reglages.i2cNano)
        self.sondeK = hw.SpiSondeK( reglages.SpiCLK, reglages.SpiCS, reglages.SpiDO)

        self.stats    = logic.stats( )

        self.ctrlVentilo = controleurs.controleur(self.ventilo, 0.5, 0)
        self.ctrlMoteur = controleurs.controleurMoteur(self.moteur, self.listeCapteurs ,
                          self.inverse, 0.5,
                          self.config( "dInverse" ), self.config( "nInverse" ),
                          self.config( "dDecalage" ))

        self.ledError = hw.Led(reglages.l1)
        self.poussoirWifi= hw.Entree( reglages.p3,200)
        self.poussoirReprise = hw.Entree( reglages.p2,200)
        self.poussoirHalt = hw.Entree( reglages.p1,200)

        self.ecran    = hw.Afficheur( 20, 4, [ "T   Ct", "", "", "" ], [
          # [ object, display fct, colonne, ligne, longueur ],
          [ self.dateur           , self.dateur.affiche          , 9  , 0 , 11 ],
          [ self.ventilo          , self.ventilo.affiche         , 14 , 3 , 1  ],
          [ self.moteur           , self.moteur.affiche          , 15 , 3 , 1  ],
          [ self.inverse          , self.inverse.affiche         , 16 , 3 , 1  ],
          # [ self.reserve        , self.reserve.affiche         , 3  , 0 , 1  ],
          [ self.capteurVis       , self.capteurVis.affiche      , 4  , 1 , 5  ],
          [ self.capteurTremie    , self.capteurTremie.affiche   , 4  , 2 , 5  ],
#          [ self.ctrlMoteur      , self.ctrlMoteur.affiche      , 7  , 2 , 2  ],
          [ self.t_eau            , self.t_eau.affiche           , 0  , 1 , 3  ],
          [ self.t_secu           , self.t_secu.affiche          , 0  , 2 , 3  ],
          [ self.d_secteur        , self.d_secteur.affiche       , 18 , 3 , 1  ],
          [ self.d_secuMeca       , self.d_secuMeca.affiche      , 19 , 3 , 1  ],
          [ self.poussoirReprise  , self.poussoirReprise.affiche , 12 , 3 , 1  ],
          [ self.poussoirHalt     , self.poussoirHalt.affiche    , 11 , 3 , 1  ],
          [ self.poussoirWifi     , self.poussoirWifi.affiche    , 10 , 3 , 1  ],
          [ self                  , self.affiche                 , 9  , 1 , 11 ],
          [ self.stats            , self.stats.affiche           , 9  , 2 , 11 ],
          [ self.sondeK           , self.sondeK.affiche          , 0  , 3 , 4  ]
          ] )

        self.i2cManager = hw.I2cManager( [ [self.ecran, 0.5 ] ] )

        self.trace    = trace.Traceur( self.dateur, [
          # [ object , label ],
          [ self.dateur.log_time     , "Time" ],
          [ self.ventilo.log         , "V" ],
          [ self.moteur.log          , "M" ],
          [ self.inverse.log         , "I" ],
          # self.reserve.log , "" ],
          [ self.poussoirReprise.log , "Pr" ],
          [ self.capteurVis.log      , "C1" ],
          [ self.capteurTremie.log   , "C2" ],
          [ self.t_eau.log           , "Te" ],
          [ self.t_secu.log          , "Ts" ],
          [ self.d_secteur.log       , "Ds" ],
          [ self.d_secuMeca.log      , "Dm" ],
          [ self.sondeK.log          , "K;Kmm5" ],
          [ self.log                 , "Etat" ],
          [ self.stats.log           , "Stats" ],
          ],
          "D",
          1,
          self.rep
          )

        # Define below the graphics list in html serveur
        ax = serv.axe ( 0, "", 'Time')
        ay1 = serv.axe ( 1, "Temperature", 0)
        ay2 = serv.axe ( 2, "Relais", 0)
        t1 = serv.courbe ( "Temperature eau", 'Te', 'y1' ,0)
        t2 = serv.courbe ( "Temperature moteur", 'Ts', 'y1' ,0)
        r1 = serv.courbe ( "Ventilateur", 'V', 'y2' ,0)
        r2 = serv.courbe ( "Moteur", 'M', 'y2' , 1.2)
        r3 = serv.courbe ( "Moteur", 'I', 'y2' , 2.4)
        g1 = serv.graphe("Temperature et relais", ax, ay1, ay2, [t1, t2, r1, r2, r3])

        ay1_2 = serv.axe ( 1, "Capteurs optique", 0)
        ay2_2 = serv.axe ( 2, "Sonde K", 0)
        cv = serv.courbe ( "Vis", 'C2', 'y1' ,0)
        ct = serv.courbe ( "Tremie", 'C1', 'y1' ,0)
        ck = serv.courbe ( "Sonde K", 'K', 'y2' ,0)
        ckm = serv.courbe ( "Sonde K mm", 'Kmm5', 'y2' ,0)
        g2 = serv.graphe("Compteurs et Sonde K", ax, ay1_2, ay2_2, [cv, ct, ck, ckm])

        ay1_3 = serv.axe ( 1, "On / Off", 0)
        Ds = serv.courbe ( "Secteur", 'Ds', 'y1' ,0)
        Dm = serv.courbe ( "Mecanique", 'Dm', 'y1' ,0)
        g3 = serv.graphe("Detecteur 220v", ax, ay1_3, '', [Ds, Dm])

        self.graphList = [g1, g2, g3]

        self.label = "WOODIE"

        self.dont_stop = 1
        self.halt = 0
        self.modif = 1
        self.wifi = 0
        os.system("systemctl stop hostapd")

    def run(self):

        # Start all
        self.dateur.start()

        self.capteurVis.start()
        self.capteurTremie.start()

        self.d_secteur.start()
        self.d_secuMeca.start()

        self.ctrlVentilo.start()
        self.ctrlMoteur.start()

        self.i2cManager.start()
        self.dallasManager.start()

        self.sondeK.start()

        self.trace.start()
        self.stats.start()

        self.setPhase("I:Start")
        self.lastEvent="None"

        # Arret par defaut
        ventilo_etat = moteur_etat = anomalie = 0
        anomalie_foyer = 0
        t=0

        time.sleep(2)

        while self.dont_stop == 1 :

              if self.config( "tMinFoyer" ) != 0 and ventilo_etat == 1 and t > self.config( "dChauffe" ) and \
                 self.config( "tMinFoyer" ) > self.sondeK.valeur() :
                anomalie_foyer = 1

              # Controle temperature moteur / coupure secteur / ...
              if self.t_eau.valide != 1 :
                self.setPhase("E:Capt E")
                anomalie = 1
              elif self.t_secu.valide != 1 :
                self.setPhase("E:Capt M")
                anomalie = 2
              elif self.t_secu.temperature >= self.config( "tSecu" ) :
                self.setPhase("E:Secu")
                anomalie = 3
              elif self.d_secteur.valeur() == 0:
                self.setPhase("E:Secteur")
                anomalie = 4
                self.trace.off()
              elif self.d_secuMeca.valeur() == 0:
                self.setPhase("E:SecuMec")
                anomalie = 5
              elif self.sondeK.valide == 0:
                self.setPhase("E:Sonde K")
                anomalie = 6
              elif self.ctrlMoteur.estBloque() != 0 :
                self.setPhase("E:Blocage")
                anomalie = 7
              # Controle de la temperature foyer
              elif anomalie_foyer != 0 :
                # Attendre que le foyer monte en temperature
                self.setPhase("E:Foyer")
                anomalie = 8
              elif anomalie != 0:
                self.setPhase("I:Reprise")
                anomalie = 0
                self.ledError.off()
                self.trace.on()

              if self.ctrlMoteur.estInverse() != 0 :
                self.logMessage("I:Inverse")
              else :
                self.lastEvent="None"

              # Lecture etat poussoir(s)
              poussoirReprise = self.poussoirReprise.valeur()
              if poussoirReprise == 1 :
                # Remise a zero des compteurs blocage
                for c in self.listeCapteurs :
                  c.razBlock()

              self.halt = self.poussoirHalt.valeur()
              if self.halt == 1 :
                self.dont_stop = 0

              if self.poussoirWifi.valeur() == 1 :
                self.wifi = 600
                os.system("systemctl start hostapd")
                self.logMessage("I:AP on")

              # Check wifi timeout
              if self.wifi > 0 :
                self.wifi -= 1
                if self.wifi == 0 :
                  os.system("systemctl stop hostapd")
                  self.logMessage("I:AP off")

              # Si anomalie, on arrete tout :
              if anomalie != 0:
                self.ctrlVentilo.pause(1)
                self.ctrlMoteur.pause(1)
                self.ledError.on()

                if anomalie >= 7 and poussoirReprise == 1 :
                  # Deblocage moteur
                  self.ctrlMoteur.debloque()

                  # Fin de cycle et tentative reprise
                  anomalie_foyer = 0
                  ventilo_etat = moteur_etat = 0
                  t = self.config( "dCycle" )

              # Sinon cycle normal
              else :

                # Si pause alors reprise (sinon pas d'effet)
                self.ctrlVentilo.pause(0)
                self.ctrlMoteur.pause(0)

                # Si Repos et temperature seuil bas, redemarrage cycle de chauffe
                if ventilo_etat == 0 and moteur_etat == 0 and self.t_eau.temperature <= self.config( "tStart" ):
                  ventilo_etat = moteur_etat = 1
                  self.setPhase("Chauffe")
                  t=0

                # Debut de cycle : test temperature et demarrage si besoin
                if t==0 :
                  if ventilo_etat > 0 : self.ctrlVentilo.demarre(self.config( "dVentilo" ))
                  if moteur_etat  > 0 : self.ctrlMoteur.demarre(self.config( "dMoteur" ))

                t += 1

                # Fin de cycle : test temperature et arret si besoin
                if t >= self.config( "dCycle" ) :
                  if ventilo_etat == 1 and self.t_eau.temperature >= self.config( "tStop" ):
# Decommenter si besoin dernier cycle sans ventilo
#                    ventilo_etat = 0
#                    self.setPhase("Fin ch.")
#                  elif ventilo_etat == 0 and moteur_etat == 1 :
                    moteur_etat = ventilo_etat = 0
                    self.setPhase("Repos")
                  t=0

              time.sleep(1)

        self.ledError.off()

        # Stoppe les taches
        self.trace.etat(0)
        self.d_secteur.etat(0)
        self.d_secuMeca.etat(0)
        self.dallasManager.etat(0)
        self.i2cManager.etat(0)
        self.sondeK.etat(0)
        self.capteurVis.etat(0)
        self.capteurTremie.etat(0)
        self.ctrlVentilo.etat(0)
        self.ctrlMoteur.etat(0)
        self.dateur.etat(0)
        self.stats.etat(0)

        # Attente fin des taches
        self.trace.join()
        print "Arret logs"
        self.dallasManager.join()
        self.i2cManager.join()
        self.sondeK.join()
        print "Arret bus managers"

        self.d_secteur.join()
        self.d_secuMeca.join()
        print "Arret detecteurs 220 V"
        self.capteurVis.join()
        print "Arret capteur vis"
        self.capteurTremie.join()
        print "Arret capteur tremie"
        self.ctrlVentilo.join()
        print "Arret controle ventilo"
        self.ctrlMoteur.join()
        print "Arret controle moteur"
        self.dateur.join()
        self.stats.join()
        print "Arret dateur et stats"

        if self.halt == 1 :
          print "HALT system"
          os.system("sync")
          time.sleep(2)
          os.system("halt")

    def etat( self, s ):
        self.dont_stop = s
        self.setPhase("I:Arret")

    def affiche(self):
        return self.phase

    def config(self, cle):
        return self.conf[cle]["valeur"]

    def log(self):
        return self.phase

    def setPhase(self, p):
        if self.phase != p :
          self.phase = p
          self.modif = 1
          if p[1] == ":" :
            self.stats.status(2)
            trace.logErreur(self.dateur, p, self.rep)
          elif p == "Chauffe" :
            self.stats.status(1)
          else :
            self.stats.status(0)

    def logMessage(self, p):
        if self.lastEvent != p :
          self.lastEvent = p
          trace.logErreur(self.dateur, p, self.rep)


if __name__ == '__main__':

  # Creation & demarrage de la chaudiere !
  woodie_instance = woodie_legacy ()

  # Creation & demarrage du serveur http
  http_serveur = serv.Serveur ( woodie_instance )
  http_serveur.start()

  # Creation & demarrage de l'instance !
  woodie_instance.start()

  # On attend ...
  while True:
    try :
      time.sleep(2)
      if serv.redemarrage == 1:
        serv.redemarrage = 0
        woodie_instance.etat(0)
        print "Re-demarrage en cours ..."

        woodie_instance.join()
        print "Instance arretee"

        woodie_instance = woodie_legacy ()
        woodie_instance.start()
        http_serveur.majSource( woodie_instance )
        print "Instance redemarree"


  # ... jusqu'a interruption manuelle
    except KeyboardInterrupt:

      woodie_instance.etat(0)
      print ""
      print "Arret en cours ..."

      woodie_instance.join()
      print "Chaudiere arretee"

      time.sleep(0.2)
      break

  print "Bye !"
  exit()
