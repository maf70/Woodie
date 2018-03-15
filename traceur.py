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

    def run(self):

        dt = datetime.now()
        tt=dt.timetuple()
        f=open("LOGS/"+str(dt.date())+".log","a")
        f.write("\nDate_Time;")

        for el in self.devices_list :
          f.write(el.label+";")
        f.write("\n")

        while self.dont_stop == 1 :
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

    def etat( self, s ):
        self.dont_stop = s





