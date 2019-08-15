#!/usr/bin/python

from datetime import datetime
from threading import Thread
import time

class dateur(Thread):

    """Classe dateur : Manage date and time for LCD / Traceur"""

    def __init__(self):
        Thread.__init__(self)
        self.modif = 0
        self.dont_stop = 1
        self.dateAffiche = ""
        self.timeAffiche = ""
        self.date = ""
        self.time = ""
        self.newDate = ""
        self.newMonth = ""
        self.newYear = ""

    def run(self):
        tt0_prev = 0
        tt1_prev = 0
        tt2_prev = 0
        while self.dont_stop == 1 :
          dt = datetime.now()
          tt=dt.timetuple()

          if tt0_prev != tt[0]:
            self.newYear = 1
            tt0_prev = tt[0]
            self.Year   = dt.strftime("%Y")
          if tt1_prev != tt[1]:
            self.newMonth = 1
            tt1_prev = tt[1]
            self.YearMonth   = dt.strftime("%Y-%m")
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

    def newYearF(self):
	if self.newYear == 1:
          self.newYear = 0
          return 1
        return 0

    def newMonthF(self):
	if self.newMonth == 1:
          self.newMonth = 0
          return 1
        return 0

    def newDateF(self):
	if self.newDate == 1:
          self.newDate = 0
          return 1
        return 0

    def affiche(self):
        return self.dateAffiche+" "+self.timeAffiche

    def log_date(self):
        return self.date

    def log_time(self):
        return self.time

    def log_datetime(self):
        return self.date+"_"+self.time

class stats(Thread):

    """Statistic module, typically average time for Repos/Chauffe phases"""

    def __init__(self ):
        Thread.__init__(self)
        self.on = 0
        self.valeur = 0
        self.modif = 0
        self.valide = 0
        self.dont_stop = 1
        self.phase = 99
        self.compteur = 0
        self.valeurs = [0, 0, 0]

    def run(self):
        while self.dont_stop == 1 :
          self.compteur += 1

          time.sleep(1)

    def status(self, s):
        if s >= 2 :
          return
        if self.phase == 99 :
          self.phase = s
        if self.phase != s :
          self.valeurs[self.phase] = self.compteur
          self.modif = 1
          self.compteur = 0
          self.phase = s

    def raz(self):
        self.valeur += 1

    def valeur(self):
        return self.valeurs[0]

    def affiche(self):
        return str(self.valeurs[0])+":"+str(self.valeurs[1])

    def log(self):
        return self.affiche()

    def etat( self, s ):
        self.dont_stop = s



