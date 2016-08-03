#! /usr/bin/python
import pwn
a = pwn.logListen(12345)
a.set_sql('explorer','123456')
a()
