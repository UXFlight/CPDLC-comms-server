#!/bin/bash

cd /var/www/CPDLC-comms-server

source venv/bin/activate

exec gunicorn \
    -k eventlet \
    -w 1 \
    -b 127.0.0.1:5321 \
    main:app