from flask_restplus import Api
from api.base import Login, HealthCheck, Images, Registration
from api.user import UserUpload, GalleryItem, Gallery, Pending, PendingJson
from documentation.namespaces import base_ns
from documentation.namespaces import user_ns

api = Api(title='Photomosaic API',
          description='A photomosaic API',
          prefix='/api/v1/photomosaic')

api.add_namespace(base_ns)
api.add_namespace(user_ns)
