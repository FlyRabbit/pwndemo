import time

import subprocess

from .. import context
from ..timeout import Timeout
from .listened import listened
from .. import tubes
from ..tubes.process import PIPE,PTY,STDOUT
from .. import timeout


class daemon(Timeout):
    def __init__(self, timeout = 90):
        super(daemon, self).__init__(timeout)

    def setlisten(self,port=0, bindaddr = "0.0.0.0",
                 fam = "any", typ = "tcp",
                 timeout = Timeout.default):
        self.port = port
        self.bindaddr = bindaddr
        self.fam = fam
        self.typ = typ
        self.Timeout = timeout


    def setprocess(self, argv,
                 shell = False,
                 executable = None,
                 cwd = None,
                 env = None,
                 timeout = Timeout.default,
                 stdin  = PIPE,
                 stdout = PTY,
                 stderr = STDOUT,
                 close_fds = True,
                 preexec_fn = lambda: None):
        self.argv = argv
        self.shell =shell
        self.executable =executable
        self.cwd = cwd
        self.env = env
        self.out = timeout
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.close_fds = close_fds
        self.preexec_fn = preexec_fn

    def __call__(self):
        with listened(self.port, self.bindaddr, self.fam, self.typ, self.Timeout) as listen:
            try:
                if listen == None:
                    return
                process = tubes.process.process(self.argv,
                                                self.shell,
                                                self.executable,
                                                self.cwd,
                                                self.env,
                                                self.out,
                                                self.stdin,
                                                self.stdout,
                                                self.stderr,
                                                self.close_fds,
                                                self.preexec_fn)
                process.set_info_log(True)
                process.connect_both(listen)
                with self.countdown():
                    while self.countdown_active():
                        time.sleep(0.1)
                        if process.poll() != None:
                            break
                    if not self.countdown_active():
                        listen.sendline('Sorry timeout')
                process.close()
            except KeyboardInterrupt:
                exit(0)


