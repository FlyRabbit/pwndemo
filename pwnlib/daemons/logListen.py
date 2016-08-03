import json
from base64 import b64decode

from pwnlib import sqllog
from pwnlib.daemons import listened
from pwnlib.logdata import logdata


class logListen():
    def __init__(self, port=0, bindaddr="0.0.0.0",
                 fam="any", typ="tcp",
                 timeout=90):

        self.port = port
        self.bindaddr = bindaddr
        self.fam = fam
        self.typ = typ
        self.Timeout = timeout


    def set_sql(self, sqluser, sqlpwd, host='localhost', database='pwnlog'):
        sqllog.set_sql(sqluser, sqlpwd, host, database)
        sqllog.sql_on = True


    def __call__(self):
        with listened(self.port, self.bindaddr, self.fam, self.typ, self.Timeout) as listen:
            if listen == None:
                return

            listen.close_info_log(True)
            token = listen.recvline()[:-1]
            if token == 'misaka':
                data = listen.recvline()[:-1]
                dict = json.loads(b64decode(data))
                logData = logdata(dict)
                if logData.level() >= 0:
                    logData.show()
                sqllog.updata_sql()
                sqllog.sql.logFromPack(logData)
            listen.close()
