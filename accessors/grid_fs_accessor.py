import logging
from pymongo import MongoClient
import gridfs
from helpers.image_streamer import ImageStreamer
from uuid import uuid4
import os


class GridFsAccessor(object):
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/')

    def __init__(self, db=None, logger=None, streamer=None):
        db = db if db is not None else MongoClient(self.MONGODB_URI).photomosaic
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.streamer = streamer if streamer is not None else ImageStreamer()
        self.db = db
        self.fs = gridfs.GridFS(self.db)

    def get(self, file_id):
        return self.fs.get(file_id)

    def put(self, data, **kwargs):
        file_id = self.fs.put(data, **kwargs)
        self.logger.debug(f'Saved file with file_id: {file_id}')
        return file_id

    def find_one(self, query=None, session=None, *args, **kwargs):
        item = self.fs.find_one(filter=query, session=session, *args, **kwargs)
        return item

    def delete(self, file_id):
        self.logger.debug(f'Removing file with file_id: {file_id}')
        self.fs.delete(file_id)

    def insert_image(self, img, file_id=None):
        file_id = file_id if file_id is not None else str(uuid4())
        img_format = img.format
        mimetype = f'image/{img_format.lower()}' if img_format is not None else 'image/jpg'
        data = self.streamer.dump_image_data(img)
        self.put(data, _id=file_id, filename=img.filename, mimetype=mimetype)
        return file_id

    def insert_thumbnail(self, img, file_id=None):
        file_id = file_id if file_id is not None else str(uuid4())
        img_format = img.format
        mimetype = f'image/{img_format.lower()}' if img_format is not None else 'image/jpg'
        data = self.streamer.dump_thumbnail_data(img)
        self.put(data, _id=file_id, filename=img.filename, mimetype=mimetype)
        return file_id

    def insert_image_file(self, path, file_id=None):
        file_id = file_id if file_id is not None else str(uuid4())
        img_format = (path.split('.')[-1]).lower()
        mimetype = f'image/{img_format.lower()}' if img_format is not None else 'image/jpg'
        with open(path, 'rb') as fn:
            data = fn.read()
        self.put(data, _id=file_id, filename=path, mimetype=mimetype)
        return file_id
