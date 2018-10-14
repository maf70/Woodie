#!/usr/bin/python
import time
import sys

import os.path 

from threading import Thread


class Traceur(Thread):

    """Thread Traceur : Record all parameters each second"""

    def __init__(self, dt, devices):
        Thread.__init__(self)
        self.dt = dt
        self.devices_list = devices
        self.dont_stop = 1
        self.active = 1
        self.activeReq = 1

    def run(self):

        f = 0

        while self.dont_stop == 1 :
         if self.active == 1 or self.activeReq == 1:
          self.active = self.activeReq

          # Changement de fichier ?
          if self.dt.newDateF() == 1:
            if f :
              f.close()
            fichier = "/mnt/data/LOGS/"+self.dt.date+".log"
            fe = os.path.isfile(fichier)
            f=open(fichier,"a")

            if fe == 0 :
              for el in self.devices_list :
                f.write(el.label+";")
              f.write("\n")
            f.write("\n")

          for el in self.devices_list :
            f.write(el.log()+";")
          f.write("\n")
         time.sleep(1)

        f.close()

    def off( self ):
        self.activeReq = 0

    def on( self ):
        self.activeReq = 1

    def etat( self, s ):
        self.dont_stop = s

def logErreur( dt, erreur) :
    f=open("/mnt/data/LOGS/"+dt.date+".err","a")
    f.write(dt.time+"\t"+erreur+"\n")
    f.close()
