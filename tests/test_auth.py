# -*- coding: utf-8 *-*
import logging
import unittest

from mongolog import MongoHandler

try:
    from pymongo import MongoClient as Connection
except ImportError:
    from pymongo import Connection


class TestAuth(unittest.TestCase):

    def setUp(self):
        """ Create an empty database that could be used for logging """
        self.db_name = '_mongolog_auth'
        self.collection_name = 'log'
        self.user_name = 'MyUsername'
        self.password = 'MySeCrEtPaSsWoRd'

        self.conn = Connection()
        self.db = self.conn[self.db_name]
        self.collection = self.db[self.collection_name]

        self.conn.drop_database(self.db_name)
        self.db.add_user(self.user_name, self.password)

    def tearDown(self):
        """ Drop used database """
        self.conn.drop_database(self.db_name)

    def testAuthentication(self):
        """ Logging example with authentication """
        log = logging.getLogger('authentication')
        log.addHandler(MongoHandler(self.collection_name, self.db_name,
                                    username=self.user_name,
                                    password=self.password))

        log.error('test')

        message = self.collection.find_one({'levelname': 'ERROR',
                                            'msg': 'test'})
        self.assertEqual(message['msg'], 'test')
