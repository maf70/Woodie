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

app                                         = Flask(__name__)
app.config['DEBUG']                         = False

def create_logger(log_lvl):
    logging.basicConfig(level=log_lvl, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.handlers.RotatingFileHandler("woodie-server.log", maxBytes=10000000, backupCount=10)
    handler.setLevel(log_lvl)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)

LOGGER = logging.getLogger(__name__)

@app.route('/')
def home():
    #HERE RETRIEVE REAL DATA FROM FILE
    time = int(current_time())
    temperature = 75
    data_x = []
    data_y = []
    
    for x in range(1, 86400):
        data_x.append(datetime.datetime.fromtimestamp(time).strftime('%H:%M:%S %Y-%m-%d '))
        time = time + 1
        
    for x in range(1, 8640):
        data_y += 10 * [temperature]
        temperature = temperature+random.randint(-1, 1)
        if temperature <= 50:
            temperature = 50
        elif temperature >=100:
            temperature = 100            
            
    return render_template('index.html', data_x=map(json.dumps, data_x), data_y=data_y)

if __name__ == '__main__':
    create_logger("DEBUG")
    app.run(host='0.0.0.0', port=80)




