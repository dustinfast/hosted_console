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

    # TODO: Get contents of terminal for web echo

    return flask.render_template('home.html',
                                 title_string='title_string',
                                 title_msg='title_msg',
                                 desc_string='desc_string',
                                 year_string='year_string',
                                 author_string='author_string',
                                 copyright_link='copywrite_link',
                                 copyright_link_text='copyright_link_text')
