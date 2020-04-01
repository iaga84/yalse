#!/usr/bin/env python3

import logging

import connexion

logging.basicConfig(level=logging.INFO)

app = connexion.App(__name__)
app.add_api('../swagger.yml')


def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    return response


app.app.after_request(after_request)

application = app.app
