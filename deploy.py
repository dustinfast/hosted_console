#!/usr/bin/env python
""" A simulated console, for use in hosting console applications.

    Author: Dustin Fast, 2018
"""

import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    """ Serves home.html, the main console interface.
    """

    # TODO: Get contents of terminal for initial web echo

    return flask.render_template('home.html',
                                 title_string='hosted_console',
                                 home_text='home_text',
                                 desc_string='desc_string',
                                 year_string='year_string',
                                 author_string='author_string',
                                 copyright_link='copywrite_link',
                                 copyright_link_text='copyright_link_text')


@app.route('/_process_user_input', methods=['POST'])
def _home_get_async_content():
    """ Receives user's textual input from the client and serves response.
    """
    user_input = flask.request.json['user_input']
    print('USER INPUT= %s' % user_input)

    return flask.jsonify(term_response=user_input)


def console_interact(post):
    """ 
        Submits the given string (post) to the console and returns the results.
        Returns:

    """
    # Get tty ID, so caller doesn't see itself.
    pts = subprocess.Popen(post, shell=True, stdout=subprocess.PIPE)
    console_response = pts.stdout.read()[:-1]  # Exclude newline char
    print(console_response)

    pts.stdout.close()
    pts.terminate()

    print(console_response)


if __name__ == '__main__':
    app.run(debug=True)
