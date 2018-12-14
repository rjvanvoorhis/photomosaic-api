import os
import jwt
import time
import logging
from accessors.user_accessor import UserAccessor


class AuthorizationError(Exception):
    pass


class AuthResource(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.accessor = UserAccessor()
        self.secret = os.environ.get('SECRET_KEY')

    @staticmethod
    def bytes_to_bearer(token):
        return {'Authorization': f'Bearer {token.decode()}'}

    @staticmethod
    def bearer_to_bytes(header):
        header_str = header.get('Authorization', '')
        return header_str[7:].encode()

    def get_roles(self, username):
        return self.accessor.get_list(username, 'roles')

    def build_token(self, username):
        payload = {
            'username': username,
            'roles': self.get_roles(username),
            'expire_at': time.time() + (30 * 60)
        }
        token = jwt.encode(payload, self.secret)
        return self.bytes_to_bearer(token)

    def verify_token(self, token, username, allowed_roles):
        if isinstance(token, dict) and 'Authorization' in token:
            token = self.bearer_to_bytes(token)
        elif isinstance(token, str) and token.startswith('Bearer'):
            token = token[7:].encode()
        payload = jwt.decode(token, self.secret)
        if 'ADMIN' not in allowed_roles:
            allowed_roles.append('ADMIN')
        try:
            if (payload.get('expire_at') - time.time()) < 0:
                raise AuthorizationError('Token expired')
            elif payload.get('username') != username and 'ADMIN' not in payload.get(['roles'], []):
                raise AuthorizationError('Username does not match')
            elif not any(role in allowed_roles for role in payload.get('roles', [])):
                raise AuthorizationError('User does not have the required roles')
        except AuthorizationError as e:
            return {'message': str(e)}, 403
        return {'message': 'Success'}, 200

    def get_auth(self, username, password):
        if not self.accessor.check_password(username, password):
            raise AuthorizationError('Not Authorized')
        return self.build_token(username)
