#!/bin/bash

export PYTHONPATH=${PYTHONPATH}:${PWD}
twistd web --port tcp:5000 --wsgi app.app
cd ffmpegScripts
python3 worker.py > /dev/null &
disown
cd ..
