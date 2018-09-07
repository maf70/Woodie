#!/usr/bin/python
import time
import sys

from threading import Thread

import reglages
from reglages import ON as ON
from reglages import OFF as OFF
import hw
import logic
import controleurs
import traceur as trace


class chaudiere(Thread):

    """Chaudiere """

    def __init__(self, fichier_param = "defaut.txt"):
        Thread.__init__(self)

        self.r = reglages.Params (fichier_param)

        if self.r.etat != "" :
          # Parse error
          afficheurU = hw.AfficheurUnique(self.r.etat)
          # On ne sort pas ...
          while 1:
            time.sleep(3)

        self.dateur   = logic.dateur()

        self.ventilo  = hw.Sortie("V", reglages.r1)
        self.moteur   = hw.Sortie("M", reglages.r2)
        self.inverse  = hw.Sortie("I", reglages.r3)
# pas utilise, force la sortie a OFF
        self.reserve  = hw.Sortie(" ", reglages.r4)

        self.listeCapteurs = []
        self.capteurVis  = hw.Compteur("C1", reglages.b1, self.r.vMinVis, 10)
        if self.r.vMinVis > 0 :
          self.listeCapteurs.append(self.capteurVis)
        self.capteurTremie = hw.Compteur("C2", reglages.b2, self.r.vMinTremie, 10)
        if self.r.vMinTremie > 0 :
          self.listeCapteurs.append(self.capteurTremie)

        self.t_eau = hw.Thermo("Te", self.r.sondeTempEau)
        self.t_secu = hw.Thermo("Ts", self.r.sondeTempMot)
        self.dallasManager = hw.DallasManager( [ [self.t_eau, 3 ], [self.t_secu, 3 ] ] )


        self.d_secteur = hw.DetectSecteur("Ds", reglages.d1)
        self.d_secuMeca = hw.DetectSecteur("Dm", reglages.d2)

#        self.analog = hw.I2cAnalog("A0", reglages.i2cNano)
        self.sondeK = hw.SpiSondeK("K", reglages.SpiCLK, reglages.SpiCS, reglages.SpiDO)

        self.ctrlVentilo = controleurs.controleur(self.ventilo, 0.5, 0)
        self.ctrlMoteur = controleurs.controleurMoteur(self.moteur, self.listeCapteurs ,
                          self.inverse, 0.5, self.r.dInverse, self.r.nInverse, self.r.dDecalage)

        self.ledError = hw.Led(reglages.l1)
        self.poussoirReprise = hw.Entree("Pr",reglages.p1,200)

        self.ecran    = hw.Afficheur( [ "T   Ct", "", "", "" ], [
          # [ object , colonne , ligne, longueur ],
          [ self.dateur  , 9, 0, 11 ],
          [ self.ventilo , 14, 3, 1 ],
          [ self.moteur  , 15, 3, 1 ],
          [ self.inverse , 16, 3, 1 ],
          # [ self.reserve , 3, 0, 1 ],
          [ self.capteurVis , 4, 1, 5 ],
          [ self.capteurTremie , 4, 2, 5 ],
#          [ self.ctrlMoteur , 7, 2, 2],
          [ self.t_eau , 0, 1, 3 ],
          [ self.t_secu , 0, 2, 3 ],
          [ self.d_secteur , 18, 3, 1 ],
          [ self.d_secuMeca , 19, 3, 1 ],
          [ self.poussoirReprise, 12, 3, 1 ],
          [ self , 9, 1, 11 ],
          [ self.sondeK , 0, 3, 4 ]
          ] )

        self.i2cManager = hw.I2cManager( [ [self.ecran, 0.5 ] ] )

        self.trace    = trace.Traceur( self.dateur, [
          # [ object ],
          self.dateur,
          self.ventilo,
          self.moteur,
          self.inverse,
          # self.reserve,
          self.poussoirReprise,
          self.capteurVis,
          self.capteurTremie,
          self.t_eau,
          self.t_secu,
          self.d_secteur,
          self.d_secuMeca,
          self.sondeK,
          self ])

        self.dont_stop = 1
        self.modif = 1
        self.setPhase("Start")
        self.label = "Woodie"

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

        # Arret par defaut
        ventilo_etat = moteur_etat = anomalie = 0
        anomalie_foyer = 0
        t=0

        time.sleep(2)

        while self.dont_stop == 1 :

              if self.r.tMinFoyer != 0 and ventilo_etat == 1 and t > self.r.dChauffe and self.r.tMinFoyer > self.sondeK.valeur() :
                anomalie_foyer = 1

              # Controle temperature moteur / coupure secteur / ...
              if self.t_eau.valide != 1 :
                self.setPhase("E:Capt E")
                anomalie = 1
              elif self.t_secu.valide != 1 :
                self.setPhase("E:Capt M")
                anomalie = 2
              elif self.t_secu.temperature >= self.r.tSecu:
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
                self.setPhase("Reprise")
                anomalie = 0
                self.ledError.off()
                self.trace.on()

              # Lecture etat poussoir(s)
              poussoirReprise = self.poussoirReprise.valeur()
              if poussoirReprise == 1 :
                # Remise a zero des compteurs blocage
                for c in self.listeCapteurs :
                  c.razBlock()


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
                  t = self.r.dCycle

              # Sinon cycle normal
              else :

                # Si pause alors reprise (sinon pas d'effet)
                self.ctrlVentilo.pause(0)
                self.ctrlMoteur.pause(0)

                # Si Repos et temperature seuil bas, redemarrage cycle de chauffe
                if ventilo_etat == 0 and moteur_etat == 0 and self.t_eau.temperature <= self.r.tStart:
                  ventilo_etat = moteur_etat = 1
                  self.setPhase("Chauffe")
                  t=0

                # Debut de cycle : test temperature et demarrage si besoin
                if t==0 :
                  if ventilo_etat > 0 : self.ctrlVentilo.demarre(self.r.dVentilo)
                  if moteur_etat  > 0 : self.ctrlMoteur.demarre(self.r.dMoteur)

                t += 1

                # Fin de cycle : test temperature et arret si besoin
                if t >= self.r.dCycle :
                  if ventilo_etat == 1 and self.t_eau.temperature >= self.r.tStop:
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
        print "Arret dateur"

    def etat( self, s ):
        self.dont_stop = s
        self.setPhase("Arret")

    def affiche(self):
        return self.phase

    def log(self):
        return self.phase

    def setPhase(self, p):
        self.phase = p
        self.modif = 1


