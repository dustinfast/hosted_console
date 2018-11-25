#!/usr/bin/env python
import queue
import subprocess
from threading import Thread

class SubprocSession(object):
    """ An interactive session with a specificed subprocess. 
        Input may be passed to, and feedback received from, the suborocess.
        To close the session, call SubproceSession.close().
    """ 
    __author__ = 'Dustin Fast (dustin.fast@outlook.com)'

    def __init__(self, path, verbose=False, timeout=.1, lines=100, sep='', 
                 shell=False):
        """ Stats an interactive session with the process given by path.
            Accepts:
                path    (str)   : Path to process to run (file name)
                verbose (bool)  : Denotes verbose output
                timeout (float) : Time to wait for input response
                lines   (int)   : Number of stdout lines to keep in mem
                sep     (str)   : Output line seperator
                shell   (bool)  : Denotes subprocess runs in shell - has
                                  security risks (see python docs) but allows
                                  usage of pipe commands, etc.
        """
        # A representation of the input/output w/the process (by line)
        self._termlines = ShoveQueue(maxsize=lines)

        # Init the instance
        self._return_q = queue.Queue()
        self._stdout_watcher = Thread(target=self._watch_stdout)
        self._shell = subprocess.Popen([path],
                                       shell=shell,
                                       encoding='utf8',
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
        
        self.verbose = verbose        # Denote verbose output option
        self._seperator = sep         # Denote line seperator
        self._timeout = timeout       # Wait time before assuming input 

        self._running = True          # Denote stdout watcher is running
        self._stdout_watcher.start()  # Start the stdout watcher thread

    def __str__(self):
        return str(self._termlines)

    def _watch_stdout(self):
        """ Watches the shell's stdout and pushes each line to self._return_q
            for receipt in self.post. Intended to be called as a thread.
        """
        while self._running:
            output = self._shell.stdout.readline()
            if output:
                self._return_q.put_nowait(output.strip())

    def _print(self, s):
        """ Prints the given string iff self.verbose.
        """
        if self.verbose:
            print(s)

    def _add_termline(self, s):
        """ Appends a new line to the termlines list followed by the
            predefined seperator (if any).
        """
        self._termlines.shove(s)

        if self._seperator:
            self._termlines.shove(self._seperator)

    def post(self, s, prompt='$ '):
        """ Writes string s to the session's stdin & returns resulting lines.
        """
        if type(s) is not str:
            raise TypeError

        self._print('Results for "%s":' % s)

        s_disp = prompt + s             # s w/ prompt string prefixed
        self._add_termline(s_disp)      # Update termlines with s

        if s[:-1] != '\n':              # Ensure s has newline ending
            s += '\n'

        self._shell.stdin.write(s)       # Post s to process' stdin
        self._shell.stdin.flush()

        # Get response from process' stdout
        while True:
            try:
                line = self._return_q.get(timeout=self._timeout)
                self._add_termline(line)    # Update termlines with response
                self._print(line)           # Print verbose output to console
            except queue.Empty:
                self._print('\n')
                break

    def console_lines(self):
        """ Returns a string representation of the session's inputs/outputs.
        """
        return str(self)

    def flush(self):
        """ Flushes all lines from the console representation.
        """
        self._termlines

    def is_alive(self):
        """ Returns true iff the shell is still alive.
        """
        return {None : True,
                0    : False}.get(self._shell.poll()) 

    def close(self):
        self._print('Quitting subprocess...')
        self._running = False
        self._shell.stdin.close()
        try:
            self._shell.wait()
            self._stdout_watcher.join()
            self._print('Done - exit code = %d' % self._shell.returncode)
        except subprocess.TimeoutExpired:
            self._print('ERROR: Timed out waiting for subprocess to quit.')
            exit()


class ShoveQueue:
    """ A "ShoveQueue" data structure. I.e. A queue that, on shove(d) to a 
        full queue, pops the oldest item from the queue before enqueing d.
    """
    __author__ = 'Dustin Fast (dustin.fast@outlook.com)'

    def __init__(self, maxsize=None):
        self._items = []             # Queue container
        self._maxsize = maxsize      # Max items allowed in queue

        if maxsize and maxsize < 0:
                raise Exception('Invalid maxsize parameter.')

    def __str__(self):
        return '\n'.join(self._items)

    def __len__(self):
        return len(self._items)

    def reset(self):
        """ Clear/reset queue items.
        """
        self._items = []

    def shove(self, item):
        """ Adds an item to the back of queue. If queue already full, makes
            room for it by removing the item at front. If an item is removed
            in this way, is returned.
        """
        removed = None
        if self.is_full():
            removed = self.pop()
        self._items.append(item)
        return removed

    def pop(self):
        """ Removes front item from queue and returns it.
        """
        if self.is_empty():
            raise Exception('Attempted to pop from an empty queue.')
        d = self._items[0]
        self._items = self._items[1:]
        return d

    def is_empty(self):
        """ Returns true iff queue empty.
        """
        return len(self) == 0

    def is_full(self):
        """ Returns true iff queue at max capacity.
        """
        return self._maxsize and len(self) >= self._maxsize


if __name__ == '__main__':
    """ Example module usage - runs three seperate commands inside a single
        bash session and prints the interaction to the console.
    """
    p = SubprocSession('bash', verbose=True)
    cmds = ['ls', 'pwd']

    for cmd in cmds:
        p.post(cmd)

    p.close()
