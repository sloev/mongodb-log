from tornado import web, ioloop
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.gen import coroutine


from X  import DB_NAME, DB_HOST, DB_PORT, SERVER_ADDRESS, LOG_COLLECTION, LOG_CHANNEL, LOGGER_NAME
from X import DESCENDING
from X redis_subscriber import RedisSubscriber
from tornadoredis import Client as SubClient
SERVER_PORT = 8889
from motor import MotorClient
import logging


class property_mixin:
    @property
    def db(self):
        return self.settings['db']

    @property
    def redis_subscriber(self):
        return self.settings['redis_subscriber']


class IndexHandler(property_mixin, RequestHandler):
    @coroutine
    def get(self):
        cursor = self.db[LOG_COLLECTION].find({})\
                .sort([('created', DESCENDING)])\
                .limit(100)\
                .skip(0)
        docs = []
        count = yield cursor.count()
        while (yield cursor.fetch_next):
            doc = cursor.next_object()
            doc.pop('_id')
            docs += [doc]
            print doc
        d = {'count':count, 'data':docs}
        self.write(d)
        self.finish()

class RealtimeHandler(property_mixin, WebSocketHandler):
    def open(self):
        self.redis_subscriber.subscribe(LOG_CHANNEL, self)
    def on_close(self):
        self.redis_subscriber.unsubscribe(LOG_CHANNEL, self)
    @coroutine
    def on_message(self, msg):
        pass
    def on_redis_message(self, channel_name, body):
        self.write_message(body)

def run():
    """The application run method
    does not return.

    """

    io_loop = ioloop.IOLoop.instance()

    routes = [
            ('/',IndexHandler),
            ('/ws',RealtimeHandler)
            ]


    database = MotorClient(DB_HOST, DB_PORT)[DB_NAME]
    redis_subscriber = SubClient()
    redis_subscriber = RedisSubscriber(redis_subscriber)

    settings = {
            'db':database,
            'redis_subscriber':redis_subscriber
            }
    app = web.Application(
            routes,
            template_path='.',
            **settings
            )


    app.listen(address=SERVER_ADDRESS, port=SERVER_PORT)

    print "started server on:", SERVER_ADDRESS, ":", SERVER_PORT
    io_loop.start()

if __name__ == "__main__":
    run()
