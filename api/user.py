from resources import BaseResource
from resources.user_resource import UserResource
from flask import request
from werkzeug.datastructures import FileStorage
from documentation.namespaces import user_ns
from documentation.models import gallery_item, message_model, message_post, upload_img, post_response

upload_parser = user_ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

paging_parser = user_ns.parser()
paging_parser.add_argument('skip', type=int)
paging_parser.add_argument('limit', type=int)


class BaseUserResource(BaseResource):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.resource = UserResource()


@user_ns.route('/gallery')
class Gallery(BaseUserResource):
    @user_ns.expect(paging_parser)
    def get(self, username):
        args = paging_parser.parse_args()
        """Get all gallery items"""
        results = self.resource.get_gallery(username, **args)
        self.page_builder.add_navigation(results, request.base_url, **args)
        return results

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

    @user_ns.expect(post_response)
    def delete(self, username):
        payload = user_ns.payload
        return self.resource.delete_uploads_item(username, payload)


@user_ns.route('/uploads/<string:file_id>')
class UserUploadItem(BaseUserResource):

    @user_ns.marshal_with(post_response)
    def get(self, username, file_id):
        return self.resource.get_upload(username, file_id)

    def delete(self, username, file_id):
        return self.resource.delete_upload_by_id(username, file_id)


