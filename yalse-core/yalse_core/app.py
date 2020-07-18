#!/usr/bin/env python3

import logging

import connexion
from sqlalchemy_utils import create_database, database_exists
from yalse_core.database import db

logging.basicConfig(level=logging.INFO)


def create_app():
    app = connexion.App(__name__)
    app.add_api('../swagger.yml')

    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://docker:docker@db:5432/yalse'
    app.app.after_request(after_request)

    return app


def register_extensions(app):
    db.init_app(app)


def setup_database(app):
    print("Setting up database..")
    with app.app_context():
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
            db.create_all()



def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    return response


app = create_app()
application = app.app
register_extensions(application)
setup_database(application)
