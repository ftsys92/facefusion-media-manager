#!/usr/bin/env python
from redis import Redis
from rq import Worker

# Preload libraries
import api

# Provide the worker with the list of queues (str) to listen to.
w = Worker(['default'], connection=Redis(host='redis', port=6379))
w.work()