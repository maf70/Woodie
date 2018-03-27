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
        data_y = []
        for line in lines:
            #Test stupid pour s'assurer que la ligne est une ligne de data
            if line[0] == "2":
                data = line.split(';')
                if len(data) > 6:
                    data_x.append(data[0])
                    data_y.append(data[6])

    return data_x, data_y


@app.route('/', methods=['GET'])
def index():
    try:
        logs = os.listdir(config.woodie_log_directory)
        return render_template('index.html', logs=logs)
    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return str(e), 500


@app.route('/graph', methods=['POST'])
def graph():
    try:
        log_file = request.form['log_radio']
        data_x, data_y = get_data(config.woodie_log_directory+log_file)
        return render_template('graph.html', data_x=data_x, data_y=data_y)
    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return str(e), 500


@app.route('/conf', methods=['GET', 'POST'])
def conf():
    try:
        conf = json.load(open(config.woodie_config))
        return render_template('conf.html', conf=conf)
    except Exception as e:
        LOGGER.error("error in index(): "+str(e))
        return str(e), 500


if __name__ == '__main__':
    configure_logger()
    app.run(host='0.0.0.0', port=8081)
