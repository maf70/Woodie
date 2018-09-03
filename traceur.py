#!/usr/bin/python
import time
import sys
from datetime import datetime

from threading import Thread


class Traceur(Thread):

    """Thread Traceur : Record all parameters each second"""

    def __init__(self, devices):
        Thread.__init__(self)
        self.devices_list = devices
        self.dont_stop = 1
        self.active = 1
        self.activeReq = 1

    def run(self):

        dt = datetime.now()
        tt=dt.timetuple()
        f=open("LOGS/"+str(dt.date())+".log","a")
        f.write("\nDate_Time;")

        for el in self.devices_list :
          f.write(el.label+";")
        f.write("\n")

        while self.dont_stop == 1 :
         if self.active == 1 or self.activeReq == 1:
          self.active = self.activeReq
          dt = datetime.now()
          tt=dt.timetuple()
          # Changement de fichier ?
          if tt[3] == 0 and tt[4] == 0 and tt[5] == 0:
            f.close()
            f=open("LOGS/"+str(dt.date())+".log","a")
            f.write("\nDate_Time;")

            for el in self.devices_list :
              f.write(el.label+";")
            f.write("\n")

          f.write(str(dt.date())+"_"+str(dt.time()).split(".")[0]+";") 
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





