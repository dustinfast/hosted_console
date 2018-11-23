#!/usr/bin/env python
""" A simulated console, for use in hosting console applications.

    Author: Dustin Fast, 2018
"""

import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    """ Serves home.html, the main console interface
    """
    return 'Deploy Test'
