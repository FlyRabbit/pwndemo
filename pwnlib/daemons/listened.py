import time

from ..tubes.listen import listen
from ..timeout import Timeout
import os


class listened():
    def __init__(self, port=0, bindaddr="0.0.0.0",
                 fam="any", typ="tcp",
                 timeout=Timeout.default):
        self.port = port
        self.bindaddr = bindaddr
        self.fam = fam
        self.typ = typ
        self.timeout = timeout

        self.listen_handle = listen(port, bindaddr, fam, typ, timeout)

    def __enter__(self):
        try:
            while True:
                self.listen_handle.wait_for_connection()
                pid = os.fork()
                if pid == 0:
                    return self.listen_handle
                else:
                    self.listen_handle = listen(self.port, self.bindaddr, self.fam, self.typ, self.timeout)
        except KeyboardInterrupt:
            self.listen_handle.close()
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.listen_handle.close()
