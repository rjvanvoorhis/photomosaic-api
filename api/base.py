import os
from resources import BaseResource
from resources.user_resource import UserException, UserAccessor
from resources.auth_resource import AuthResource, AuthorizationError
from helpers.image_server import ImageServer

from documentation.namespaces.base import base_ns, user_model, registration_model, login_model


@base_ns.route('/healtcheck')
class HealthCheck(BaseResource):
    def get(self):
        self.logger.debug('Getting env variables')
        redis_host = os.environ.get('RHOST', 'redis')
        server_root = os.environ.get('SERVER_ROOT', 'http://127.0.0.1:5000')
        mongodb_uri = os.environ.get('MONGODB_URI', '')
        return {'redis_host': redis_host,
                'mongodb_uri': mongodb_uri,
                'server_root': server_root}, 200


@base_ns.route('/register')
class Registration(BaseResource):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.accessor = UserAccessor()

    @base_ns.expect(registration_model)
    def post(self):
        payload = base_ns.payload
        try:
            user = self.accessor.create_user(**payload)
        except UserException as e:
            self.logger.exception(str(e))
            return {'message': str(e)}, 401
        return user


@base_ns.route('/login')
class Login(BaseResource):

    def __init__(self, api=None):
        super().__init__(api=api)
        self.resource = AuthResource()

    @base_ns.expect(login_model)
    def post(self):
        payload = base_ns.payload
        try:
            header = self.resource.get_auth(**payload)
        except AuthorizationError as e:
            self.logger.exception(str(e))
            return {'message': str(e)}, 403
        return header


@base_ns.route('/users')
class Users(BaseResource):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.accessor = UserAccessor()

    @base_ns.doc(user_model)
    def get(self):
        return list(self.accessor.collection.find({}, None))


@base_ns.route('/images/<string:file_id>')
class Images(BaseResource):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.image_server = ImageServer()

    @base_ns.produces(['image/*'])
    def get(self, file_id):
        return self.image_server.serve_from_mongodb(file_id)
