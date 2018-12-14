import logging
from pymongo import MongoClient
import os

PROJECTION = {'_id': 0}


class MongoDbAccessor(object):
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/')

    def __init__(self, collection_name):
        self.logger = logging.getLogger(__name__)
        self.client = MongoClient(self.MONGODB_URI)
        self.db = self.client.photomosaic
        self.collection = self.db[collection_name]
        self.collection_name = collection_name

    def find_one(self, query=None, projection=PROJECTION, **kwargs):
        self.logger.debug('Retrieving document from {cn} with query: {query}'.format(
            cn=self.collection_name, query=query))
        doc = self.collection.find_one(query, projection, **kwargs)
        return doc

    def update_one(self, query, update, **kwargs):
        self.logger.debug('Updating document from {cn} with query: {query}, '
                          'with update: {update}'.format(
                           cn=self.collection_name, query=query, update=update))
        self.collection.update_one(query, update, **kwargs)

    def replace_one(self, query, replacement, **kwargs):
        self.logger.debug('Replacing document from {cn} with query: {query}, '
                          'with: {replacement}'.format(
                           cn=self.collection_name, query=query, replacement=replacement))
        self.collection.replace_one(query, replacement, **kwargs)
