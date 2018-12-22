from flask import Flask
from api import api
from flask_cors import CORS


def initialize_app():
    application = Flask(__name__)
    api.init_app(application)
    application.config['CORS_HEADERS'] = 'Content-Type'
    cors = CORS(application, resorces={r'/api/*': {"origins": '*'}})
    return application


if __name__ == '__main__':
    app = initialize_app()
    app.run('0.0.0.0')

