#!/bin/bash

/usr/bin/python2 -c "import flask"

if [ $? -eq 1 ]
    then
        echo "Flask installation needed!"
        sudo -E /usr/bin/python2 -m pip -U Flask
    else
        echo "Flask already installed!"
fi

sudo /usr/bin/python2 main.py
