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

def fake_data():
    time = int(current_time())
    temperature = 75
    data_x = []
    data_y = []
    
    for x in range(1, 86400):
        data_x.append(datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))
        time = time + 1
        
    for x in range(1, 8640):
        data_y += 10 * [temperature]
        temperature = temperature+random.randint(-1, 1)
        if temperature <= 50:
            temperature = 50
        elif temperature >=100:
            temperature = 100

    return data_x, data_y

def get_data(log_file):
    with open(log_file, "r") as lines:
        data_x = []
        data_y = []
        for line in lines:
            #Test stupid pour s'assurer que la ligne est une ligne de data
            if line[0] == "2":
                data = line.split(';')
                data_x.append(data[0])
                data_y.append(data[6])

    return data_x, data_y

@app.route('/')
def home():
    data_x, data_y = get_data(config.woodie_log_directory+'2018-03-16.log')
    
    #TRY FAKE DATA TO TEST 86400 random points plots
    #data_x, data_y = get_data()
    
    return render_template('index.html', data_x=data_x, data_y=data_y)

if __name__ == '__main__':
    configure_logger()
    app.run(host='0.0.0.0', port=80)
