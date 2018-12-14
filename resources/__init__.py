import logging
from flask_restplus import Resource


class BaseResource(Resource):

    def __init__(self, api=None):
        super().__init__(api=api)
        self.logger = logging.getLogger(__name__)
