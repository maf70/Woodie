#!/usr/bin/python
import time
import sys

from threading import Thread

import reglages
from reglages import ON as ON
from reglages import OFF as OFF
import hw
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

        self.ventilo  = hw.Sortie("V", reglages.r1)
        self.moteur   = hw.Sortie("M", reglages.r2)
        self.inverse  = hw.Sortie("I", reglages.r3)
# pas utilise, force la sortie a OFF
        self.reserve  = hw.Sortie(" ", reglages.r4)

        self.capteur_moteur  = hw.Compteur("C1", reglages.b1, 10)
        self.capteur_moteur2 = hw.Compteur("C2", reglages.b2, 10)

        self.t_eau = hw.Thermo("Te", self.r.sondeTempEau)
        self.t_secu = hw.Thermo("Ts", self.r.sondeTempMot)

        self.ctrlVentilo = controleurs.controleur(self.ventilo, 0.5, 0)
        self.ctrlMoteur = controleurs.controleurMoteur(self.moteur, [ self.capteur_moteur, self.capteur_moteur2] , self.r.vMin,
                          self.inverse, 0.5, self.r.dInverse, self.r.nInverse, self.r.dDecalage)

        self.ecran    = hw.Afficheur( [
          # [ object , colonne , ligne, longueur ],
          [ self.ventilo , 0, 0, 1 ],
          [ self.moteur  , 1, 0, 1 ],
          [ self.inverse , 2, 0, 1 ],
          # [ self.reserve , 3, 0, 1 ],
          [ self.capteur_moteur , 0, 1, 2 ],
          [ self.capteur_moteur2 , 3, 1, 2 ],
          [ self.t_eau , 6, 1, 3 ],
          [ self.t_secu , 10, 1, 3 ],
          [ self , 4, 0, 8 ],
          ] )

        self.trace    = trace.Traceur( [
          # [ object ],
          self.ventilo,
          self.moteur,
          self.inverse,
          # self.reserve,
          self.capteur_moteur,
          self.capteur_moteur2,
          self.t_eau,
          self.t_secu,
          self ])

        self.dont_stop = 1
        self.phase = "Off"
        self.modif = 1
        self.label = "Woodie"

    def run(self):

        # Start all
        self.capteur_moteur.start()
        self.capteur_moteur2.start()

        self.t_eau.start()
        self.t_secu.start()

        self.ctrlVentilo.start()
        self.ctrlMoteur.start()

        self.ecran.start()
        self.trace.start()

        # Arret par defaut
        ventilo_etat = moteur_etat = anomalie = 0
        t=0

        while self.dont_stop == 1 :

              # Controle temperature moteur / coupure secteur / ...
              if self.t_eau.valide != 1 :
                self.phase = "E:Capt E"
                self.modif = anomalie = 1
              elif self.t_secu.valide != 1 :
                self.phase = "E:Capt M"
                self.modif = anomalie = 2
              elif self.t_secu.temperature >= self.r.tSecu:
                self.phase = "E:Secu"
                self.modif = anomalie = 3
              elif anomalie != 0:
                self.phase = "Reprise"
                self.modif = 1
                anomalie = 0

              # Si anomalie, on arrete tout :
              if anomalie != 0:
                self.ctrlVentilo.stoppe()
                self.ctrlMoteur.stoppe()
              # Sinon cycle normal
              else :

                # Si Repos et temperature seuil bas, redemarrage cycle de chauffe
                if ventilo_etat == 0 and moteur_etat == 0 and self.t_eau.temperature <= self.r.tStart:
                  ventilo_etat = moteur_etat = 1
                  self.phase = "Chauffe"
                  self.modif = 1
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
#                    self.phase = "Fin ch."
#                    self.modif = 1
#                  elif ventilo_etat == 0 and moteur_etat == 1 :
                    moteur_etat = ventilo_etat = 0
                    self.phase = "Repos"
                    self.modif = 1
                  t=0

              time.sleep(1)

        # Stoppe les taches
        self.trace.etat(0)
        self.t_eau.etat(0)
        self.t_secu.etat(0)
        self.ecran.etat(0)
        self.capteur_moteur.etat(0)
        self.capteur_moteur2.etat(0)
        self.ctrlVentilo.etat(0)
        self.ctrlMoteur.etat(0)

        # Attente fin des taches
        self.trace.join()
        print "Arret logs"
        self.ecran.join()
        print "Arret ecran"

        self.t_eau.join()
        self.t_secu.join()
        print "Arret capteurs temperature"
        self.capteur_moteur.join()
        print "Arret capteur moteur 1"
        self.capteur_moteur2.join()
        print "Arret capteur moteur 2"
        self.ctrlVentilo.join()
        print "Arret controle ventilo"
        self.ctrlMoteur.join()
        print "Arret controle moteur"

    def etat( self, s ):
        self.dont_stop = s
        self.phase = "Arret"

    def affiche(self):
        return self.phase

    def log(self):
        return self.phase


