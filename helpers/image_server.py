from flask import make_response
from helpers.image_streamer import ImageStreamer
from accessors.grid_fs_accessor import GridFsAccessor


class ImageServer(object):
    def __init__(self):
        self.streamer = ImageStreamer()

    @staticmethod
    def get_mimetype_from_image(img):
        img_format = img.format if img.format else 'jpg'
        return f'image/{img_format}'

    @staticmethod
    def get_mimetype_from_path(path):
        img_format = path.split('.')
        img_format = img_format[-1] if img_format else 'jpg'
        return f'image/{img_format}'

    def serve_image(self, img):
        img_data = self.streamer.dump_image_data(img)
        resp = make_response(img_data)
        resp.content_type = self.get_mimetype_from_image(img)
        return resp

    def serve_thumbnail(self, img, max_dim=None):
        size = (max_dim, max_dim) if max_dim is not None else (300, 300)
        img_data = self.streamer.dump_thumbnail_data(img, size)
        resp = make_response(img_data)
        resp.content_type = self.get_mimetype_from_image(img)
        return resp

    def serve_from_path(self, path):
        img_data = self.streamer.get_image_data(path)
        resp = make_response(img_data)
        resp.content_type = self.get_mimetype_from_path(path)
        return resp

    def serve_thumbnail_from_path(self, path, max_dim=None):
        size = (max_dim, max_dim) if max_dim is not None else (300, 300)
        img_data = self.streamer.get_image_thumbnail_data(path, size)
        resp = make_response(img_data)
        resp.content_type = self.get_mimetype_from_path(path)
        return resp

    @staticmethod
    def serve_from_mongodb(file_id):
        img = GridFsAccessor().get(file_id)
        resp = make_response(img.read())
        resp.content_type = img.mimetype
        return resp
