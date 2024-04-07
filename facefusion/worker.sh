#!/bin/bash

update-ca-certificates

python /usr/src/app/worker.py &

python /usr/src/app/api.py
