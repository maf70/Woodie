#!/usr/bin/python

from datetime import datetime
from threading import Thread
import time

class dateur(Thread):

    """Classe affichage : track all devices change and display it when occurs"""

    def __init__(self):
        Thread.__init__(self)
        self.label = "Time"
        self.modif = 0
        self.dont_stop = 1
        self.dateAffiche = ""
        self.timeAffiche = ""
        self.date = ""
        self.time = ""
        self.newDate = ""

    def run(self):
        tt2_prev = 0
        while self.dont_stop == 1 :
          dt = datetime.now()
          tt=dt.timetuple()

          if tt2_prev != tt[2]:
            self.dateAffiche = dt.strftime("%m/%d")
            self.date        = dt.strftime("%Y-%m-%d")
            self.newDate = 1
            tt2_prev = tt[2]
          self.timeAffiche   = dt.strftime("%H:%M")
          self.time          = dt.strftime("%H:%M:%S")
          self.modif = 1
          time.sleep(1) 

    def etat( self, s ):
        self.dont_stop = s

    def newDateF(self):
	if self.newDate == 1:
          self.newDate = 0
          return 1
        return 0

    def affiche(self):
        return self.dateAffiche+" "+self.timeAffiche

    def log(self):
        return self.time



