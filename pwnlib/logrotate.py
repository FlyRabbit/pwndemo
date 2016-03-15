import json
import string
from base64 import b64encode, b64decode
from time import ctime

from pwnlib import sqllog
from pwnlib.util import fiddling

from .log import getLogger

import  MySQLdb
import  traceback
import  logging

log = getLogger('pwnlib.rotate')

class logrotate(object):
    _sql = 'SELECT * FROM connections '
    _sql_id = 'con_id = %d '
    _sql_hash = 'con_hash = "%s" '
    _sql_token = 'token = "%s" '
    _sql_host = 'host = "%s" '
    _sql_port = 'port = %d '
    _sql_con_time = 'con_time > %d '
    _sql_fin_time = 'fin_time < %d '
    _sql_target = 'target = "%s" '

    _sql_flow = 'SELECT * FROM flow WHERE con_hash = "%s" '

    def __init__(self, sqluser, sqlpwd, host='localhost', database='pwnlog'):
        self._db = MySQLdb.connect(host, sqluser, sqlpwd, database)

    def find(self, **kwargs):
        tstr = self.make_sql(**kwargs)
        all_data = None
        try:
            csr = self._db.cursor()
            csr.execute(tstr)
            print tstr
            all_data = csr.fetchall()
            csr.close()
        except:
            traceback.print_exc()
            self._db.rollback()

        return self.pack(all_data)

    def make_sql(self, **kwargs):
        dataList = []
        dataList.append((self._sql_id, kwargs.get('con_id',None)))
        dataList.append((self._sql_hash, kwargs.get('con_hash', None)))
        token = kwargs.get('token', None)
        if token != None:
            token = b64encode(token)
        dataList.append((self._sql_token, token))
        dataList.append((self._sql_host, kwargs.get('host', None)))
        dataList.append((self._sql_port, kwargs.get('port', None)))
        dataList.append((self._sql_con_time, kwargs.get('con_time', None)))
        dataList.append((self._sql_fin_time, kwargs.get('fin_time', None)))
        dataList.append((self._sql_target, kwargs.get('target', None)))

        flag = False
        tstr = self._sql
        for data in dataList:
            if data[1] != None:
                if flag == False:
                    tstr += 'WHERE '
                    flag = True
                else:
                    tstr += 'AND '
                tstr += data[0] % data[1]

        return tstr

    def pack(self, allData):
        dataList = []
        for row in allData:
            IO_data = self.get_IO_data(row[1])
            temp_dict = {}
            temp_dict['con_id'] = row[0]
            temp_dict['con_hash'] = row[1]
            temp_dict['token'] = b64decode(row[2])
            temp_dict['host'] = row[3]
            temp_dict['port'] = row[4]
            temp_dict['con_time'] = row[5]
            temp_dict['fin_time'] = row[6]
            temp_dict['target'] = row[7]
            temp_dict['data'] = IO_data
            dataList.append(logdata(temp_dict))
        return  dataList

    def get_IO_data(self, hash):
        temp_data = ()
        data = []
        try:
            csr = self._db.cursor()
            csr.execute(self._sql_flow%hash)
            temp_data = csr.fetchall()
            csr.close()
        except:
            traceback.print_exc()
            self._db.rollback()

        for row in temp_data:
            data.append((row[2],row[3],b64decode(row[4])))

        data.sort()

        return data



class logdata(object):
    def __init__(self, data):
        self._data = data

    def show(self):
        log.info('Get a connnection to %s at %s'%(ctime(self._data['con_time']),self._data['target']))
        log.info('The connection from %s:%d'%(self._data['host'],self._data['port']))
        if self._data['token'] != '':
            log.info('Token is: %s'%self._data['token'])

        datas = self._data['data']

        for data in datas:
            if data[1] == sqllog.recv:
                log.recv('Received %#x bytes At %s: ' % (len(data[2]),ctime(data[0])))
            elif data[1] == sqllog.send:
                log.send('Sent %#x bytes At %s:' % (len(data[2]),ctime(data[0])))

            if len(set(data[2])) == 1:
                log.indented('%r * %#x' % (data[2][0], len(data[2])), level = logging.INFO)
            elif all(c in string.printable for c in data[2]):
                for line in data[2].splitlines(True):
                    log.indented(repr(line), level = logging.INFO)
            else:
                log.indented(fiddling.hexdump(data[2]), level = logging.INFO)


    def get_josn(self):
        return json.dumps(self._data)

    def get_dict(self):
        return self._data
