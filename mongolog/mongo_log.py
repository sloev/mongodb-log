# -*- coding: utf-8 *-*
import sys
import getpass
import logging

from bson       import InvalidDocument
from datetime   import datetime
from socket     import gethostname
from motor      import MotorClient, MotorCollection
import sys
import traceback 

import json
def make_log_request_method(log_name):
    def log_request(handler):
        logger = logging.getLogger(log_name)

        status = handler.get_status()
        if status < 400:
            log_method = logger.info
        elif status < 500:
            log_method = logger.warning
        else:
            log_method = logger.error

        summary = handler._request_summary()
        user = handler.current_user
        user_string = ""
        if user:
            user_string = "[auth user=%s]" % user.username
        #lav fikumdik med at forksellige status gir forskellige log methods
        request_time = 1000 * handler.request.request_time()

        msg = "HTTP: %d %s %.2fms %s" % (status, summary, request_time, user_string)
        log_method(msg)

    return log_request

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
            #time=datetime.now(),
            host=gethostname(),
            message=msg,
            args=tuple(unicode(arg) for arg in record.args)
        )
        if 'exc_info' in data and data['exc_info']:
            data['exc_info'] = str(self.formatException(data['exc_info']))
        return data


class MongoLogging(logging.Handler):
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

        print "logger_redis:", self.redis_client, self.redis_channel
    def log_callback(self,result, error):
        print "callback:", result, error

    def emit(self, record):
        """ Store the record to the collection. Async insert """
        try:
            print type(record)
            doc = self.format(record)
            print "_id in record:", '_id' in doc
            self.collection.insert(doc)
            if '_id' in doc:
                doc.pop('_id')
            if self.redis_client:
                try:
                    self.redis_client.publish(self.redis_channel,json.dumps(doc))
                except Exception,e:
                    msg =  "Mongo_log_json_dumps_error:"
                    type_, value_, traceback_ = sys.exc_info()
                    t =  msg, type_, value_, traceback.format_tb(traceback_)
                    print str(t)

        except InvalidDocument as e:
            logging.error("Unable to save log record: %s", e.message,
                exc_info=True)

