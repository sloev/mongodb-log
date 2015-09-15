# -*- coding: utf-8 *-*
import sys
sys.path.append('..')

import logging

from mongolog       import MongoHandler
from tornado.ioloop import IOLoop
from redis          import Redis

if __name__ == '__main__':

    log = logging.getLogger('example')
    log.setLevel(logging.DEBUG)
    redis_client = Redis()
    log.addHandler(MongoHandler(redis_client=redis_client))

    log.debug("1 - debug message")
    log.info("2 - info message")
    log.warn("3 - warn message")
    log.error("4 - error message")
    log.critical("5 - critical message")

    IOLoop.instance().start()
