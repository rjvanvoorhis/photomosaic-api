import logging
from pymongo import MongoClient
import os

PROJECTION = {'_id': 0}


class Paginator(object):
    def __init__(self, collection, base_url=None):
        self.collection = collection
        self.base_url = base_url if base_url is not None else ''

    def build_results(self, query=None, projection=None, unwind=None, skip=0, limit=None, sort=None):
        match_step = {'$match': query} if query is not None else {'$match': {}}
        sort_step = {'$sort': sort} if sort is not None else {'$sort': {'_id': 1}}
        aggr = [match_step, sort_step]
        if unwind:
            aggr.append({'$unwind': unwind})
        if limit:
            paginate = [{'$skip': skip}, {'$limit': limit}]
            aggr.extend(paginate)
        if projection:
            aggr.append({'$project': projection})
        return list(self.collection.aggregate(aggr))

    def get_count(self, query, unwind):
        aggr = [{'$match': query}]
        if unwind:
            aggr.append({'$unwind': unwind})
        aggr.append({'$count': 'count'})
        result = list(self.collection.aggregate(aggr))
        count = 0 if not result else result[0].get('count', 0)
        return count

    def build_cursor(self, query=None, projection=None, unwind=None, skip=0, limit=None, sort=None):
        query = query if query else {}
        total = self.get_count(query, unwind)
        cursor = {
            'total': total,
            'results': self.build_results(query, projection, unwind, skip, limit, sort),
        }
        return cursor


class MongoDbAccessor(object):
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/')

    def __init__(self, collection_name):
        self.logger = logging.getLogger(__name__)
        self.client = MongoClient(self.MONGODB_URI)
        self.db = self.client.photomosaic
        self.collection = self.db[collection_name]
        self.collection_name = collection_name
        self.paginator = Paginator(self.collection)

    def aggregate(self, *args, **kwargs):
        return list(self.collection.aggregate(*args, **kwargs))

    def find_one(self, query=None, projection=None, **kwargs):
        projection = projection if projection else PROJECTION
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

    def get_paginated_results(self, query, projection=None, unwind=None, skip=None, limit=None, sort=None):
        return self.paginator.build_cursor(query, projection, unwind, skip, limit, sort)

    def delete_one_element(self, query, array_field, element_filter):
        self.logger.debug(f'Removing {element_filter} from {array_field}')
        to_update = {'$pull': {array_field: element_filter}}
        return self.collection.update_one(query, to_update)

    def get_array_element(self, query, array_field, element_filter):
        pipeline = [
            {'$match': query},
            {'$unwind': f'${array_field}'},
            {'$match': element_filter},
            {'$project': {'result': f'${array_field}', '_id': 0}}
        ]
        result = self.aggregate(pipeline)
        return result[0].get('result', {}) if result else {}

