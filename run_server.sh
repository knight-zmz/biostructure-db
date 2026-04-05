#!/bin/bash
cd app
python3 run.py &
echo $! > ../server.pid
