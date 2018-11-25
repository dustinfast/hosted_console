#!/usr/bin/env python
""" Web display with simulated console, for use in console application hosting.

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
# TODO: STARTUP_CMDS ex: 'compile/run'

# Globals
app = flask.Flask(__name__)
_sess = None
# _sess = SubprocSession(BASH_CMD, sep='<br />', lines=52, shell=True)

@app.route('/')
def home():
    """ Serves home.html, the main console interface.
    """
    return flask.render_template('home.html',
                                 title_string=TITLE,
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
        _sess.post(user_input)

    response = str(_sess)
    print('---- RESPONSE = %s' % response)  # debug

    return flask.jsonify(term_response=response)

class OutterSession(object):
    """ A SubprocSession wrapper class. Coordinates inner subproc session(s)
        output and prompt behavior.
    """
    def __init__(self, prompt='$ ', inner_prompt='>> ', line_sep='',
                 shell=False):
        self._inner = None          # Inner session
        self.is_active = True       # Denotes session process alive
        self._inner_lines = None    # Ref to self._inner._termlines  
        self._lines = []            # Aggregated inner lines
        self._shell = shell         # Denotes bash shell context
        self._prompt = prompt
        self._inner_prompt = inner_prompt
        self._line_seperator = line_sep

    def __str__(self):
        """ Returns a string representation of the console's lines.
        """
        # Build a list of the previous & current session's lines (if any)
        # ret_lines = [l for l in self._lines]
        # if self._inner_lines:
        #     ret_lines += [l for l in self._inner_lines.items()]

        # Aggregated lines
        ret_str = '\n'.join(self._lines)

        # Inner session lines
        if self._inner_lines:
            ret_str += '\n'.join(self._inner_lines.items())

        return ret_str
        # return '\n'.join(ret_lines)

    def _new_inner(self, cmd):
        """ Starts a new inner subprocesses session and aggregates lines.
        """
        print('STARTED NEW INNER')
        # Concatenate previous inner lines w/aggregated lines
        if self._inner_lines:
                self._lines += self._inner_lines.items()

        # Add current line
        self._lines.append(self._prompt + cmd)
        if self._line_seperator:
            self._lines.append(self._line_seperator)

        self._inner = SubprocSession(cmd,
                                     sep=self._line_seperator,
                                     shell=self._shell,
                                     lines=0,
                                     verbose=True)
                                     
    def post(self, s):
        """ Writes string s to the session's stdin & returns resulting lines.
        """
        # If the inner session's subprocess is alive, business is good
        if self._inner and self._inner.is_alive():
            self._inner.post(s, self._inner_prompt)
            self._inner_lines = self._inner._termlines  # Establish ref

        # Else, we start a new inner session and fenangle the line handling
        else:
            self._new_inner(s)  # New inner session

    def close(self):
        """ Closes any open sessions and does cleanup.
        """
        if self._inner:
            self._inner.close()
    

_sess = OutterSession(line_sep='<br />')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    _sess.close()
