from werkzeug.security import generate_password_hash, check_password_hash
from accessors.user_accessor import UserAccessor
from redis_processor.message_processor import MessageProcessor, Message
import logging
from helpers.image_server import ImageServer
import os


class UserException(Exception):
    pass


class UserResource(object):
    def __init__(self):
        self.accessor = UserAccessor()
        self.processor = MessageProcessor()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def set_password(password):
        psw_hash = generate_password_hash(password)
        return psw_hash

    @staticmethod
    def check_password(psw_hash, password):
        return check_password_hash(psw_hash, password)

    def get_roles(self, username):
        query = {'username': username}
        projection = {'roles': 1, '_id': 0}
        return self.accessor.collection.find(query, projection)

    def get_gallery(self, username, skip=0, limit=None, sort=None):
        return self.accessor.get_paginated_list(username, 'gallery', skip, limit, sort)

    def get_gallery_item(self, username, gallery_id):
        return self.accessor.get_list_item(username, 'gallery', gallery_id)

    def insert_gallery_item(self, username, gallery_item):
        self.accessor.insert_list_item(username, 'gallery', gallery_item)
        return gallery_item

    def create_user(self, username, email, password):
        return self.accessor.create_user(username, email, password)

    def insert_message(self, username, message):
        self.accessor.insert_message(username, message)

    def post_message(self, username, form_content):
        message = self.processor.create_message(username, **form_content)
        self.accessor.insert_message(username, message)

    def get_pending_message(self, username):
        message = self.accessor.get_last_message(username)
        if not message:
            return message, 404
        message = Message.load_from_document(message)
        path = message.current
        resp = ImageServer().serve_thumbnail_from_path(path, 300)
        return resp

    def get_pending_message_json(self, username):
        message = self.accessor.get_last_message(username)
        if not message:
            return message, 404
        message = Message.load_from_document(message)
        return message.jsonify()

    def get_uploads(self, username):
        return self.accessor.get_list(username, 'uploads')

    def get_upload(self, username, file_id):
        return self.accessor.get_array_element({'username': username}, 'uploads', {'uploads.file_id': file_id})

    def delete_uploads_item(self, username, upload):
        file_id = upload.get('file_id')
        return self.delete_upload_by_id(username, file_id)

    def delete_upload_by_id(self, username, file_id):
        if not file_id:
            return {'message': 'No file_id provided'}, 400
        upload = self.get_upload(username, file_id)
        if upload:
            self._remove_files(upload)
            self.accessor.delete_one_element({'username': username}, 'uploads', upload)
            return {'message': f'Successfully deleted {file_id} for {username}'}, 200
        return {'message': f'No file to Remove'}, 200

    def _remove_files(self, upload_item):
        file_path = upload_item.get('img_path', '')
        if os.path.exists(file_path):
            os.remove(file_path)
        self.accessor.fs_accessor.delete(upload_item.get('file_id'))
        self.accessor.fs_accessor.delete(upload_item.get('thumbnail_id'))


"""
python
from resources.user_resource import UserResource
foo = UserResource()
foo.get_upload('rjvanvoorhis', '9ab159cb-474f-4be2-963e-3e20da872886')
"""