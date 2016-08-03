import pwn

log = pwn.logrotate('explorer','123456')
a = log.find(host='192.168.199.254')[0]
a.show(True)
