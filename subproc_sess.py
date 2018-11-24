#!/usr/bin/env python
import queue
import subprocess
from threading import Thread

class SubprocSession(object):
    """ An interactive session with a subprocess. The subprocess is held open
        while input may be passed to it and resulting lines received via
        SubprocSession.post(input).
        To close the session, call SubproceSession.close()
    """ 
    def __init__(self, proc_path='bash', verbose=False, shell=True):
        """ Accepts:
                proc_path (str) :
                verbose (bool)  : Denotes verbose output
                shell   (bool)  : Denotes subprocess runs in shell. Has
                                  security risks (see python docs) but allows
                                  usage of pipe commands, etc.
        """
        # Init the subprocess, stdout watcher, and stdout return queue
        self.return_q = queue.Queue()
        self.stdout_watcher = Thread(target=self.watch_stdout)
        self.shell = subprocess.Popen([proc_path],
                                      shell=shell,
                                      encoding='utf8',
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        
        self.running = True          # Denote stdout watcher is running
        self.verbose = verbose       # Denote verbose output option

        self.stdout_watcher.start()  # Start the stdout watcher thread

    def _print(self, s):
        """ Prints the given string to the console iff self.verbose.
        """
        if self.verbose:
            print(s)

    def post(self, s):
        """ Posts the input string s to the process and returns the resulting
            terminal lines as a list.
        """
        result_lines = [s]
        self._print('Results for "%s":' % s)

        if s[:-1] != '\n':  # Ensure nl ending
            s += '\n'

        self.shell.stdin.write(s)  # Post to shell's stdin
        self.shell.stdin.flush()

        # Get response lines
        while True:
            try:
                line = self.return_q.get(timeout=.1)
                result_lines.append(line)
                self._print(line)
            except queue.Empty:
                result_lines.append('\n')
                self._print('\n')
                break

        return result_lines

    def close(self):
        self._print('Quitting shell...')
        self.running = False
        self.shell.stdin.close()
        self.shell.wait()
        self.stdout_watcher.join()
        self._print('Done - exit code = %d' % self.shell.returncode)

    def watch_stdout(self):
        """ Watches the shell's stdout and pushes each line to self.return_q
            for receipt in self.post.
        """
        while self.running:
            output = self.shell.stdout.readline()
            if output:
                self.return_q.put_nowait(output.strip())


if __name__ == '__main__':
    """ Example module usage - runs three seperate commands inside a single
        bash session and prints results to the console.
    """
    p = SubprocSession('bash')
    test_cmds = ['ls', 'pwd', 'ps aux']

    for cmd in test_cmds:
        lines = p.post(cmd)
        for line in lines:
            print(line)

    p.close()
