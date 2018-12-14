from flask import Flask
from api import api


def initialize_app():
    application = Flask(__name__)
    api.init_app(application)
    return application


if __name__ == '__main__':
    app = initialize_app()
    app.run('0.0.0.0')

