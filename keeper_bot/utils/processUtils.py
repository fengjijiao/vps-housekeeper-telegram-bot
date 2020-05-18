#!/usr/bin/env python
# -*- coding:utf-8 -*-
# PIDFILE = '/var/run/myscript.pid'
import os
PIDFILEPATH = '%s.pid'


def is_running(label='default'):
    PIDFILE = PIDFILEPATH % label
    try:
        with open(PIDFILE) as f:
            pid = int(next(f))
        return os.kill(pid, 0) is None
    except Exception:
        return False


def set_running(label='default'):
    PIDFILE = PIDFILEPATH % label
    with open(PIDFILE, 'w') as f:
        f.write(f'{os.getpid()}\n')


def del_running(label='default'):
    PIDFILE = PIDFILEPATH % label
    if os.path.exists(PIDFILE):
        # 删除文件，可使用以下两种方法。
        os.remove(PIDFILE)
        # os.unlink(my_file)
    else:
        print('no such file:%s' % PIDFILE)
