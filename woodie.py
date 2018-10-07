#!/usr/bin/python
import time
import sys

import chaudiere as ch
import serveur.main as serv

# Creation & demarrage du serveur http
woodieS = serv.WServeur ()
woodieS.start()

# Creation & demarrage de la chaudiere !
woodie = ch.chaudiere ( "config.json" )
woodie.start()

# On attend ...
while True:
  try :
    time.sleep(2)
    if serv.redemarrage == 1:
      serv.redemarrage = 0
      woodie.etat(0)
      print "Re-demarrage en cours ..."

      woodie.join()
      print "Chaudiere arretee"

      woodie = ch.chaudiere ( "config.json" )
      woodie.start()
      print "Chaudiere redemarree"


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


