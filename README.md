# Woodie
Controleur de chaudiere à plaquette de bois

La chaudiere est composée de :
- un moteur entrainant une vis sans fin pour amener les plaquettes dans le corps de chauffe
- un ou plusieurs opto-coupleur(s) (LM393) pour controler la rotation de la vis
- le sens de rotation de la vis doit etre inversé en cas de blocage
- un moteur entrainant un ventilateur pour activer la combustion
- un capteur de temperature (DS18B20) de l'eau en sortie de chaudiere
- un capteur de temperature (DS18B20) de sécurité
- un thermocouple (sonde K) pour mesurer la temperature du foyer

Fonctionnement de la chaudiere:
- En debut de cycle (durée 5 minutes), la vis et le ventilateur sont actionnés
- au bout de 40 secondes, la vis d'alimentation est arretée
- au bout de 4 minutes, le ventilateur est arreté
- au bout de 5 minutes, le cycle recommence
- Si la temperature de l'eau est atteinte en fin de cycle, arret des cycles de chauffe
- Dès que la temperature redescend en dessous du seuil bas, redemarrage des cycles de chauffe
- Controle en permanance que les capteurs de temperatures sont toujours valide et que la temperature de securité n'est pas atteinte
- Controle de la temperature du foyer (sonde K) et arret de la chaudiere si en dessous d'un minimum ( = Chaudiere eteinte )
- En cas de blocage de la vis, on arrete le moteur puis on le fait tourner en sens inverse pendant quelques secondes
- Verification que le moteur tourne en sens inverse
- Gestion de la detection en cas de coupure secteur
- Gestion de la detection de la securité mécanique
- Ces parametres sont charges depuis un fichier (defaut.txt)
- Un serveur http donne l'acces a l'historique du fonctionnement (a parametrer), et le réglages des parametres.

Le controleur de la chaudiere est composé :
- D'un pi zero
- D'une carte 4 relais
- D'un LCD (HD44780 20x4 i2c 0x3F) affichant (pour l'instant) l'etat des capteurs, relais et chaudiere
- D'un module RTC DS1307 (i2c 0x68)
- De 2 modules pour detection de la presence du 220V
- D'un module MAX31855K pour gerer la sonde K, acces via SPI software
- D'un slot arduino Nano (precedement utilise comme convertisseur analogique/numerique accessible par i2c 0x08) + ampli op LM358

Pour les tests, un banc de test remplace la chaudiere :
- structure à base de jouet "Knex"
- un petit moteur 12V remplace le moteur de la vis
- celui-ci entraine un cd-rom sur lequel est positionné l'optocoupleur
- un spot à led (3 W) actionné par le relais du ventilateur simule la combustion
- la sonde temperature de l'eau est positionné sous le spot
- les consignes de temperatures sont adaptées en fonction du banc

Le logiciel est écrit en python2 et utilise notament :
GPIO : https://github.com/adafruit/Adafruit_Python_GPIO
I2C  : https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
SPI/MAX31855K  : https://github.com/adafruit/Adafruit_Python_MAX31855.git

Reste à faire:
- parametre si dernier cycle de plaquettes sans ventilateur lorsque le seuil temperature haut est atteint (en commentaire actuellement)



