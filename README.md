# Woodie
Controleur de chaudiere à plaquette de bois

La chaudiere est composée de :
- un moteur entrainant une vis sans fin pour amener les plaquettes dans le corps de chauffe
- un opto-coupleur (LM393) pour controler la rotation de la vis
- le sens de rotation de la vis doit etre inversé en cas de blocage
- un moteur entrainant un ventilateur pour activer la combustion
- un capteur de temperature (DS18B20) de l'eau en sortie de chaudiere
- un capteur de temperature (DS18B20) de sécurité

Fonctionnement de la chaudiere:
- En debut de cycle (durée 5 minutes), la vis et le ventilateur sont actionnés
- au bout de 40 secondes, la vis d'alimentation est arretée
- au bout de 4 minutes, le ventilateur est arreté
- au bout de 5 minutes, le cycle recommence
- Si la temperature de l'eau est atteinte en fin de cycle, arret des cycles de chauffe
- Dès que la temperature redescend en dessous du seuil bas, redemarrage des cycles de chauffe
- on controle en permanance que les capteurs de temperatures sont toujours valide et que la temperature de securité n'est pas atteinte
- en cas de blocage de la vis, on arrete le moteur puis on le fait tourner en sens inverse pendant quelques secondes

Le controleurs de la chaudiere est composé :
- d'un pi zero
- d'une carte 4 relais
- d'un LCD (HD44780 16x2) affichant (pour l'instant) l'etat des capteurs, relais et chaudiere

Pour les tests, un banc de test remplace la chaudiere :
- structure à base de jouet "Knex"
- un petit moteur 12V remplace le moteur de la vis
- celui-ci entraine un cd-rom sur lequel est positionné l'optocoupleur
- un spot à led (3 W) actionné par le relais du ventilateur simule la combustion
- la sonde temperature de l'eau est positionné sous le spot
- les consignes de temperatures sont adaptées en fonction du banc

Le logiciel est écrit en python.

Reste à faire:
- parametre si dernier cycle de plaquettes sans ventilateur lorsque le seuil temperature haut est atteint (en commentaire actuellement)
- gerer un deuxieme capteur dans le controleur moteur (décale par raport au premier et evite les fausses detections lorsque le capteur est en limite
- verifier que le moteur tourne en sens inverse
- gestion de la detection en cas de coupure secteur
- gestion de la detection de la securité mécanique
- gestion d'un thermocouple pour mesurer la temperature du foyer
- charger les parametres de la chaudiere depuis un fichier (defaut.txt)
- enregistrer les etats des relais et capteurs periodiquement, et stocker sur la carte SD.
- serveur http pour afficher l'etat, l'historique du fonctionnement, et le réglages des parametres.



