from accessors.mongo_db_accessor import MongoDbAccessor
from accessors.grid_fs_accessor import GridFsAccessor
from objects.message import Message
from PIL import Image
import uuid
import os
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4


class UserException(Exception):
    pass


def set_password(password):
    psw_hash = generate_password_hash(password)
    return psw_hash


class UserAccessor(MongoDbAccessor):
    API_PREFIX = f'{os.environ.get("SERVER_ROOT", "http://127.0.0.1:5000")}/api/v1/photomosaic'
    MEDIA_FOLDER = 'uploads'

    def __init__(self):
        super().__init__('users')
        self.fs_accessor = GridFsAccessor(db=self.db, logger=self.logger)

    def check_password(self, username, password):
        projection = {'_id': 0, 'username': 1, 'password_hash': 1}
        query = {'username': username}
        user = self.find_one(query, projection)
        if not user or not user.get('password_hash'):
            return False
        return check_password_hash(user['password_hash'], password)

    def get_paginated_list(self, username, field, skip=0, limit=None, sort=None):
        projection = {'_id': 0, field: 1}
        query = {'username': username}
        unwind = f'${field}'
        cursor = self.get_paginated_results(query, projection, unwind, skip, limit, sort)
        results = [item.get(field, {}) for item in cursor.get('results', [])]
        cursor['results'] = results
        return cursor

    def get_list(self, username, field):
        projection = {'_id': 0, field: 1}
        query = {'username': username}
        results = self.collection.find_one(query, projection)
        return results.get(field, [])

    def get_list_item(self, username, field, field_id):
        items = self.get_list(username, field)
        default = {}
        for item in items:
            if item.get(field) == field_id:
                return item
        return default

    def insert_list_item(self, username, field_name, item):
        query = {'username': username}
        to_update = {'$push': {field_name: item}}
        self.update_one(query, to_update)

    def insert_image_and_thumbnail(self, path):
        img = Image.open(path)
        img_id = self.fs_accessor.insert_image_file(path)
        thumbnail_id = self.fs_accessor.insert_thumbnail(img)
        return img_id, thumbnail_id

    def create_gallery_item(self, username, path):
        img_id, thumbnail_id = self.insert_image_and_thumbnail(path)
        gallery_item = {
            'username': username,
            'gallery_id': str(uuid.uuid4()),
            'mosaic_url': f'{self.API_PREFIX}/images/{img_id}',
            'alternate_url': f'{self.API_PREFIX}/images/{img_id}',
            'thumbnail_url': f'{self.API_PREFIX}/images/{thumbnail_id}',
            'alternate_thumbnail_url': f'{self.API_PREFIX}/images/{thumbnail_id}',
            'toggle_on': True,
        }
        gif_path = path.split('.')[0] + '.gif'
        if not path.endswith('gif') and os.path.exists(gif_path):
            alternate_id, alternate_thumbnail = self.insert_image_and_thumbnail(gif_path)
            gallery_item['alternate_url'] = f'{self.API_PREFIX}/images/{alternate_id}'
            gallery_item['alternate_thumbnail_url'] = f'{self.API_PREFIX}/images/{alternate_thumbnail}'
        self.insert_list_item(username, 'gallery', gallery_item)
        return gallery_item

    def insert_message(self, username, message):
        if not isinstance(message, dict):
            message = message.jsonify()
        to_update = {'$push': {'messages': message}}
        query = {'username': username}
        print(f'query: {query}, to update: {to_update}')
        self.collection.update_one(query, to_update)

    def get_messages(self, username):
        projection = {'_id': 0, 'messages': 1}
        query = {'username': username}
        gallery = self.find_one(query, projection)
        return gallery.get('messages', [])

    def get_last_message(self, username):
        messages = self.get_messages(username)
        return messages[-1] if messages else {}

    def get_message(self, username, message_id):
        messages = self.get_messages(username)
        message = {}
        for item in messages:
            if item.get('message_id') == message_id:
                message = item
                break
        return message

    def update_message(self, username, message):
        if isinstance(message, Message):
            message = message.jsonify()
        message_id = message.get('message_id')
        query = {'username': username, 'message.message_id': message_id}
        to_update = {'$set': {'messages.$': message}}
        self.collection.update_one(query, to_update)

    def refresh_last_message(self, username):
        last_message = self.get_last_message(username)
        message = Message.load_from_document(last_message)
        self.update_message(username, message)

    def make_upload_path(self, path):
        prefix = str(uuid.uuid4())
        return os.path.join(self.MEDIA_FOLDER, f'{prefix}_{path}')

    def upload_file(self, username, img_file):
        path = self.make_upload_path(img_file.filename)
        img_file.save(path)
        img_id, thumbnail_id = self.insert_image_and_thumbnail(path)
        upload_object = {
            'img_path': path,
            'file_id': img_id,
            'thumbnail_id': thumbnail_id
        }
        self.insert_list_item(username, 'uploads', upload_object)
        return upload_object

    def create_user(self, username, email, password):
        user = {
            'password_hash': set_password(password),
            'username': username,
            'email': email,
            'gallery': [],
            'uploads': [],
            'messages': [],
            'friends': [],
            'roles': ['USER'],
            '_id': str(uuid4())
        }
        query = {'$or': [{'email': user['email']}, {'username': user['username']}]}
        if self.collection.count(query):
            raise UserException(f'Error: username {username} or email {email} are already associated with an account')
        self.collection.insert_one(user)
        return user

