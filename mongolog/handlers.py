# -*- coding: utf-8 *-*
import sys
import getpass
import logging

from bson       import InvalidDocument
from datetime   import datetime
from socket     import gethostname
from motor      import MotorClient, MotorCollection

if sys.version_info[0] >= 3:
    unicode = str

class MongoFormatter(logging.Formatter):
    def format(self, record):
        """Format exception object as a string"""
        data = record.__dict__.copy()

        if record.args:
            msg = record.msg % record.args
        else:
            msg = record.msg

        data.update(
            username=getpass.getuser(),
            time=datetime.now(),
            host=gethostname(),
            message=msg,
            args=tuple(unicode(arg) for arg in record.args)
        )
        if 'exc_info' in data and data['exc_info']:
            data['exc_info'] = self.formatException(data['exc_info'])
        return data


class MongoHandler(logging.Handler):
    """ Custom log handler

    Logs all messages to a mongo collection. This  handler is
    designed to be used with the standard python logging mechanism.
    """
    def __init__(self, collection='central_log', db='mongolog', host='localhost', port=27017,
        username=None, password=None, level=logging.NOTSET, redis_client=None, redis_channel="/syslog"):
        """ Init log handler and store the collection handle """
        logging.Handler.__init__(self, level)
        if isinstance(collection, str):
            connection = MotorClient(host, port)
            if username and password:
                connection[db].authenticate(username, password)
            self.collection = connection[db][collection]
        elif isinstance(collection, MotorCollection):
            self.collection = collection
        else:
            raise TypeError('collection must be an instance of basestring or '
                             'MotorCollection')
        self.redis_client = redis_client
        self.redis_channel = redis_channel
        self.formatter = MongoFormatter()

    def log_callback(self,result, error):
        print "callback:", result, error

    def emit(self, record):
        """ Store the record to the collection. Async insert """
        try:
            doc = self.format(record)
            self.collection.insert(doc, callback=self.log_callback)
            if self.redis_client:
                self.redis_client.publish(self.redis_channel, doc)
        except InvalidDocument as e:
            logging.error("Unable to save log record: %s", e.message,
                exc_info=True)

