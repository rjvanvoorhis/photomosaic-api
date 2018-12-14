from werkzeug.security import generate_password_hash, check_password_hash
from accessors.user_accessor import UserAccessor
from redis_processor.message_processor import MessageProcessor, Message
import logging
from helpers.image_server import ImageServer


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
        return self.accessor.get_list(username, 'roles')

    def get_gallery(self, username):
        return self.accessor.get_list(username, 'gallery')

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