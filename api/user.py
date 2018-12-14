from resources import BaseResource
from resources.user_resource import UserResource
from werkzeug.datastructures import FileStorage
from documentation.namespaces import user_ns
from documentation.models import gallery_item, message_model, message_post, upload_img, post_response


upload_parser = user_ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)


class BaseUserResource(BaseResource):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.resource = UserResource()


@user_ns.route('/gallery')
class Gallery(BaseUserResource):
    def get(self, username):
        """Get all gallery items"""
        return self.resource.get_gallery(username)

    @user_ns.expect(message_post, validate=True)
    def post(self, username):
        """Add a new gallery item"""
        payload = user_ns.payload
        self.resource.post_message(username, payload)
        return self.resource.accessor.get_last_message(username), 201


@user_ns.route('/gallery/<string:gallery_id>')
class GalleryItem(BaseUserResource):
    def get(self, username, gallery_id):
        return self.resource.get_gallery_item(username, gallery_id)


@user_ns.route('/pending')
class Pending(BaseUserResource):
    @user_ns.produces(['application/json', 'img/*', 'image/*'])
    def get(self, username):
        return self.resource.get_pending_message(username)


@user_ns.route('/pending_json')
class PendingJson(BaseUserResource):
    @user_ns.produces(['application/json'])
    def get(self, username):
        return self.resource.get_pending_message_json(username)


@user_ns.route('/uploads')
class UserUpload(BaseUserResource):

    @user_ns.expect(upload_parser)
    def post(self, username):
        payload = upload_parser.parse_args()
        if 'file' not in payload:
            return {'message': 'A file is required!'}, 400

        upload_item = self.resource.accessor.upload_file(username, payload['file'])
        return upload_item, 201

    @user_ns.marshal_with(post_response, as_list=True)
    def get(self, username):
        return self.resource.get_uploads(username)