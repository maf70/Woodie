# -*- coding: utf-8 -*-

from flask import (
    Flask, jsonify, request, url_for, redirect, send_from_directory,
    render_template
)

import logging
import logging.handlers
import random
import json
import datetime
from time import time as current_time
import config
import os
from collections import OrderedDict


app                                         = Flask(__name__)
app.config['DEBUG']                         = False

def configure_logger():
    logging.basicConfig(level=config.log_level, format=config.log_format)
    handler = logging.handlers.RotatingFileHandler(config.log_name, maxBytes=config.log_max_size, backupCount=config.log_backup_count)
    handler.setLevel(config.log_level)
    formatter = logging.Formatter(config.log_format)
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

LOGGER = logging.getLogger(__name__)


def get_data(log_file):
    with open(log_file, "r") as lines:
        data_x = []
        data_y_te = []
        data_y_t2 = []
        data_y_rV = []
        data_y_rM = []
        data_y_rI = []
        data2_y_c1 = []
        data2_y_c2 = []
        data2_y_k = []
        for line in lines:
            if line[0] != 'D' :
                data = line.split(';')
                if len(data) > 12:
                    data_x.append(data[0])
                    data_y_te.append(data[7])
                    data_y_t2.append(data[8])
                    data_y_rV.append(data[1])
#                    data_y_rM.append(data[2])
#                    data_y_rI.append(data[3])
                    data_y_rM.append(int(data[2])+1.2)
                    data_y_rI.append(int(data[3])+2.4)
                    data2_y_c1.append(data[5])
                    data2_y_c2.append(data[6])
                    data2_y_k.append(data[11])

    return data_x, data_y_te, data_y_t2, data_y_rV, data_y_rM, data_y_rI, data2_y_c1, data2_y_c2, data2_y_k

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

@app.route('/', methods=['GET'])
def index():
    try:
        logs = os.listdir(config.woodie_log_directory)
        logs.sort(reverse=True)
        return render_template('index.html', logs=logs)
    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return render_template('error.html', error=str(e))


@app.route('/graph', methods=['POST'])
def graph():
    try:
        log_file = request.form['log_radio']
        jour = log_file.split('.')[0]
        data_x, data_y_te, data_y_t2, data_y_rV, data_y_rM, data_y_rI, data2_y_c1, data2_y_c2, data2_y_k = get_data(config.woodie_log_directory+log_file)
        return render_template('graph.html', log_file=jour, data_x=data_x, data_y_te=data_y_te, data_y_t2=data_y_t2, data_y_rV=data_y_rV, data_y_rM=data_y_rM, data_y_rI=data_y_rI, data2_y_c1=data2_y_c1, data2_y_c2=data2_y_c2, data2_y_k=data2_y_k)
    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return render_template('error.html', error=str(e))


@app.route('/conf', methods=['GET', 'POST'])
def conf():
    try:
        if request.method == 'GET':
            jsonFile = open(config.woodie_config, "r")
            conf = json.load(jsonFile, object_pairs_hook=OrderedDict)
            jsonFile.close()
            return render_template('conf.html', conf=conf)
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
        LOGGER.error("error in index(): "+str(e))
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    configure_logger()
    app.run(host='0.0.0.0', port=config.http_port)
