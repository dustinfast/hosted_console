#!/usr/bin/env python
""" A simulated console, for use in hosting console applications.

    Author: Dustin Fast, 2018
"""

import flask
from datetime import datetime
from subproc_sess import SubprocSession

BASH_CMD = 'bash'
TITLE = 'Hosted Console'
DESC = 'Hosted Console'
AUTHOR = 'Dustin Fast'
COPY_LINK = 'https://github.com/dustinfast'
COPY_TEXT = 'https://github.com/dustinfast'

# Globals
app = flask.Flask(__name__)
sess = SubprocSession(BASH_CMD, sep='<br />', lines=52, shell=True)

@app.route('/')
def home():
    """ Serves home.html, the main console interface.
    """
    # Get console contents for initial web display
    term_text = sess.console_lines()

    return flask.render_template('home.html',
                                 title_string=TITLE,
                                 terminal_text=term_text,
                                 desc_string=DESC,
                                 year_string=str(datetime.now().year),
                                 author_string=AUTHOR,
                                 copyright_link=COPY_LINK,
                                 copyright_link_text=COPY_TEXT)


@app.route('/_process_user_input', methods=['POST'])
def _process_user_input():
    """ Receives user's textual input from the client and serves response.
    """
    user_input = flask.request.json['user_input']
    print('---- USER INPUT= %s' % user_input)  # debug

    response = ''
    if user_input:
        # Post the input to the process session
        sess.post(user_input)
        print('---- RESPONSE = %s' % response)  # debug

    response = sess.console_lines()

    return flask.jsonify(term_response=response)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    sess.close()
