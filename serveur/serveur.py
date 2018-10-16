# -*- coding: utf-8 -*-

from flask import (
    Flask, jsonify, request, url_for, redirect, send_from_directory,
    render_template
)

import logging
import logging.handlers
import random
import json
from datetime import datetime
from time import time as current_time
import config
import os
import fnmatch
from collections import OrderedDict

from threading import Thread

redemarrage = 0
gl = []
titre = "Test serveur"
log_nbCol = 3
log_check = 'T'
lcd = [ [ ' ' * 16],  [ ' ' * 16] ]


app                                         = Flask(__name__)
app.config['DEBUG']                         = False



class axe :

    """Classe axe : Description d'un axe"""

    def __init__(self, type, label, colNom):
        self.type = type
        self.label = label
        self.colNom = colNom
        self.col = 0
        self.pts = []

class courbe :

    """Classe courbe : Description d'une courbe"""

    def __init__(self, nom, colNom, axe, offset):
        self.nom = nom
        self.colNom = colNom
        self.col = 0
        self.axe = axe
        self.offset = offset
        self.pts = []

class graphe :

    """Classe graphe : Description complete d'un graphe"""

    def __init__(self, titre, x, y1, y2, courbes):
        self.titre = titre
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.courbes = courbes




def configure_logger():
    logging.basicConfig(level=config.log_level, format=config.log_format)
    handler = logging.handlers.RotatingFileHandler(config.log_name, maxBytes=config.log_max_size, backupCount=config.log_backup_count)
    handler.setLevel(config.log_level)
    formatter = logging.Formatter(config.log_format)
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

LOGGER = logging.getLogger(__name__)


def get_data(log_file, gr):
    global log_nbCol
    global log_check
    with open(log_file, "r") as lines:
        gr.x.pts = []
        for c in gr.courbes:
          c.pts = []
        for line in lines:
            data = line.split(';')
            if line[0] != log_check :
                if len(data) >= log_nbCol:
                    gr.x.pts.append(data[gr.x.col])
                    for c in gr.courbes:
#                      c.pts.append(int(data[c.col])+c.offset)
                      c.pts.append(data[c.col])
            else:
              for c in gr.courbes:
                c.col = data.index(c.colNom)
              gr.x.col = data.index(gr.x.colNom)

    return gr

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

@app.route('/', methods=['GET', 'POST'])
def index():
    global redemarrage
    try:
        if request.method == 'GET':
          logs = fnmatch.filter(os.listdir(config.woodie_log_directory), '*.log')
          logs.sort(reverse=True)
          errs = fnmatch.filter(os.listdir(config.woodie_log_directory), '*.err')
          errs.sort(reverse=True)
          list = []
          for f in errs :
            sublist = []
            with open(config.woodie_log_directory+f, "r") as lines:
              for line in lines :
                sublist.append(line)
            sublist.reverse()
            sublist.insert(0,f.split('.')[0])
            list.append(sublist)

          fs_info = os.statvfs(config.woodie_log_directory)
          fs = str((fs_info.f_bsize * fs_info.f_bfree) / (1024*1024)) + " Mo"

          return render_template('index.html', titre=titre, fs=fs, logs=logs, errs=list)

        else:
          redemarrage = 1
          return render_template('reboot.html', titre=titre)

    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return render_template('error.html', titre=titre, error=str(e))


@app.route('/lcd', methods=['GET'])
def lcd():
    global gl
    global lcd

    mylcd = []
    for el in lcd:
        mylcd.append( "".join(el) )

    try:
        return render_template('lcd.html', titre=titre, lcd=lcd )

    except Exception as e:
        LOGGER.error("error in lcd(): "+str(e))
        return render_template('error.html', titre=titre, error=str(e))

@app.route('/graph', methods=['POST'])
def graph():
    global gl
    try:
        log_file = request.form['log_radio']
        jour = log_file.split('.')[0]
        list = []
        try :
          lines = open(config.woodie_log_directory+jour+".err", "r")
          for line in lines :
            list.append(line)
          list.reverse()

        except :
          lines = []

        for g in gl:
          g = get_data(config.woodie_log_directory+log_file, g)
          g.x.label = jour
        return render_template('graph.html', titre=titre, dt=datetime.now(), log_file=jour, errs=list, gl=gl )

    except Exception as e:
        LOGGER.error("error in graph(): "+str(e))
        return render_template('error.html', titre=titre, error=str(e))


@app.route('/conf', methods=['GET', 'POST'])
def conf():
    try:
        if request.method == 'GET':
            jsonFile = open(config.woodie_config, "r")
            conf = json.load(jsonFile, object_pairs_hook=OrderedDict)
            jsonFile.close()
            return render_template('conf.html', titre=titre, conf=conf)
        else:
            jsonFile = open(config.woodie_config, "r")
            conf = json.load(jsonFile, object_pairs_hook=OrderedDict)
            jsonFile.close()
            for parameter in conf:
                if conf[parameter]['modifiable']:
                    if isint(request.form[parameter]):
                        conf[parameter]['valeur'] = int(request.form[parameter])
                    elif isfloat(request.form[parameter]):
                        conf[parameter]['valeur'] = float(request.form[parameter])
                    else:
                        conf[parameter]['valeur'] = request.form[parameter]
            jsonFile = open(config.woodie_config, "w+")
            jsonFile.write(json.dumps(conf, ensure_ascii=False, indent=4, sort_keys=False).encode('utf8'))
            jsonFile.close()
            return redirect(url_for('conf'))
    except Exception as e:
        LOGGER.error("error in conf(): "+str(e))
        return render_template('error.html', titre=titre, error=str(e))


class Serveur(Thread):

    """Thread : Manage serveur task"""

    def __init__(self, source):
        global gl
        global titre
        global log_nbCol
        global log_check
        global lcd
        Thread.__init__(self)
        self.dont_stop = 1
        self.source = source
        gl = source.graphList
        titre = source.label
        log_nbCol = source.trace.nbElem
        log_check = source.trace.devices_list[0][1][0]
        lcd = source.ecran.shadow

    def run(self):
        configure_logger()
        app.run(host='0.0.0.0', port=config.http_port)
        while self.dont_stop == 1 :
          time.sleep(1)

    def etat( self, s ):
        self.dont_stop = s

if __name__ == '__main__':
    ax = axe ( 0, "", 'Time')
    ay1 = axe ( 1, "Temperature", 0)
    ay2 = axe ( 2, "Relais", 0)
    ct = courbe ( "Temperature eau", 'Te', 'y1' ,0)
    r1 = courbe ( "Ventilateur", 'V', 'y2' ,0)
    g1 = graphe("Temperature et relais", ax, ay1, ay2, [ct, r1])

    configure_logger()
    gl = [g1]
    app.run(host='0.0.0.0', port=config.http_port)
