#!/usr/bin/python
import time
import sys

import chaudiere as ch

# Creation & demarrage de la chaudiere !
woodie = ch.chaudiere ( "defaut.txt" )
woodie.start()

# On attend ...
while True:
  try :
    time.sleep(2)

# ... jusqu'a interruption manuelle
  except KeyboardInterrupt:

    woodie.etat(0)
    print ""
    print "Arret en cours ..."

    woodie.join()
    print "Chaudiere arretee"

    time.sleep(0.2)
    break

print "Bye !"
exit()


