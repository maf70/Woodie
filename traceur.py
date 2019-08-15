#!/usr/bin/python
import time
import sys

import os.path 

from threading import Thread


class Traceur(Thread):

    """Thread Traceur : Record all parameters each second"""

    def __init__(self, dt, devices, periode="D", freq=1, repertoire="/mnt/data/LOGS/"):
        Thread.__init__(self)
        self.dt = dt
        self.devices_list = devices
        self.nbElem = len(devices)
        self.periode = periode
        self.freq = freq
        self.rep = repertoire
        self.dont_stop = 1
        self.active = 1
        self.activeReq = 1

    def run(self):

        f = 0
        fichier = ""
        compteur = 1

        while self.dont_stop == 1 :
          compteur -= 1
          if compteur == 0 :

            if self.active == 1 or self.activeReq == 1:
              self.active = self.activeReq

              # Changement de fichier ?
              if self.periode == "D" and self.dt.newDateF() == 1:
                fichier = self.rep+self.dt.date+".log"
              elif self.periode == "M" and self.dt.newMonthF() == 1:
                fichier = self.rep+self.dt.YearMonth+".log"
              elif self.periode == "Y" and self.dt.newYearF() == 1:
                fichier = self.rep+self.dt.Year+".log"
              elif self.periode == "A" and not f :
                fichier = self.rep+"all.log"

              if fichier != "" :
                if f :
                  f.close()
                fe = os.path.isfile(fichier)
                f=open(fichier,"a")
                fichier = ""

                if fe == 0 :
                  for el in self.devices_list :
                    f.write(el[1]+";")
                  f.write("\n\n")

              for el in self.devices_list :
                f.write(el[0]()+";")
              f.write("\n")

              compteur = self.freq

          time.sleep(1)

        f.close()

    def off( self ):
        self.activeReq = 0

    def on( self ):
        self.activeReq = 1

    def etat( self, s ):
        self.dont_stop = s

def logErreur(dt, erreur, rep="/mnt/data/LOGS/") :
    f=open(rep+dt.date+".err","a")
    f.write(dt.time+"\t"+erreur+"\n")
    f.close()
