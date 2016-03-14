import base64
from hashlib import md5

import  MySQLdb
import  traceback
import time
import  log

logger = log.getLogger('sqllog')
recv = 1
send = 0

class sqllog(object):
    _consqlstr  = 'INSERT INTO pwnlog.connections(con_hash,token,host,port,con_time,fin_time,target) VALUES("%s","%s","%s",%d,%f,%f,"%s");'
    _dsqlstr = 'INSERT INTO pwnlog.flow(con_hash,time,flag,data) VALUES("%s",%f,%d,"%s");'
    _find_table = 'SELECT table_name FROM information_schema.TABLES WHERE table_name ="%s";'

    _creat_connections = 'create table if not exists connections( ' \
                            'con_id INT(11) NOT NULL AUTO_INCREMENT ,' \
                            'con_hash CHAR(45) NOT NULL , ' \
                            'token VARCHAR(100) DEFAULT NULL ,' \
                            'host CHAR(16) NOT NULL , ' \
                            'port INT(11) NOT NULL , ' \
                            'con_time DOUBLE NOT NULL , ' \
                            'fin_time DOUBLE NOT NULL , ' \
                            'target VARCHAR(1024) DEFAULT NULL ,' \
                            'PRIMARY KEY (con_id)' \
                         ');'

    _flow = 'create table if not exists flow(' \
                'id INT(11) NOT NULL AUTO_INCREMENT,' \
                'con_hash CHAR(45) NOT NULL , ' \
                'time DOUBLE NOT NULL , ' \
                'flag INT(11) NOT NULL , ' \
                'data MEDIUMTEXT, ' \
                'PRIMARY KEY (id)' \
            ');'

    recv = 1
    send = 0

    def __init__(self, sqluser, sqlpwd, host='localhost', database='pwnlog'):
        self._db = MySQLdb.connect(host, sqluser, sqlpwd,'pwnlog')
        csr = self._db.cursor()

        tstr = self._find_table%('connections',)
        csr.execute(tstr)

        if len(csr.fetchall()) == 0:
            self.creat_table('connections')

        tstr = self._find_table%('flow',)
        csr.execute(tstr)
        if len(csr.fetchall()) == 0:
            self.creat_table('flow')
        csr.close()
        self.is_init = False

    def log_new_connection(self,client,target='',t=time.time()):
        self._con_time = t
        self._host, self._port, self._token = client
        self._token = base64.b64encode(self._token)
        self._con_hash = md5('%s:%d-%f'%(self._host,self._port,self._con_time)).hexdigest()
        self._target = target
        self.is_init = True

    def log_data(self, data, flag, t = time.time()):
        if self.is_init == False:
            logger.error('Please call log_new_connection method before')

        tstr = self._dsqlstr%(self._con_hash, t, flag, base64.b64encode(data))
        try:
            csr = self._db.cursor()
            csr.execute(tstr)
            self._db.commit()
            csr.close()
        except:
            traceback.print_exc()
            self._db.rollback()

    def log_finish(self, t = time.time()):
        tstr = self._consqlstr%(self._con_hash, self._token, self._host, self._port, self._con_time, t, self._target)
        try:
            csr = self._db.cursor()
            csr.execute(tstr)
            self._db.commit()
            csr.close()
            self.close()
        except:
            traceback.print_exc()
            self._db.rollback()

    def creat_table(self, table='connections'):

        if table == 'connections':
            tstr = self._creat_connections
        elif table == 'flow':
            tstr = self._flow
        else:
            return
        try:
            csr = self._db.cursor()
            csr.execute(tstr)
            self._db.commit()
            csr.close()
        except:
            traceback.print_exc()
            self._db.rollback()

    def close(self):
        self._db.close()

    def update_handle(self,  sqluser, sqlpwd, host='localhost'):
        self._db = MySQLdb.connect(host, sqluser, sqlpwd)


sql = None
sql_on = False
sql_info = {}
def set_sql(sqluser, sqlpwd, host='localhost', database='pwnlog'):
    global sql
    global sql_on
    global sql_info
    sql_info['sqluser'] = sqluser
    sql_info['sqlpwd'] = sqlpwd
    sql_info['host'] = host

    sql = sqllog(sqluser, sqlpwd, host, database)
    sql_on = True
    return sql

def updata_sql():
    global sql
    global sql_info
    sql.update_handle(sql_info['sqluser'], sql_info['sqlpwd'], sql_info['host'])
    return sql