#!/usr/bin/env python
# -*- coding:utf-8 -*-
import keeper_bot.config as staticGlobal  # 全局配置
from keeper_bot.utils import packetUtils
import sqlite3, os

con = sqlite3.connect(staticGlobal.DB_FILE_PATH, check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()
if not os.path.exists(staticGlobal.DB_FILE_PATH):
    cur.execute('create table api ( id integer not null constraint api_pk primary key autoincrement,name varchar(32) '
                'not null,url varchar(512) not null,type integer default 0 not null);')
    cur.execute('create table server ( sid integer not null constraint server_pk primary key autoincrement, '
                'vpsname varchar(32) not null, vpsid integer not null, virt integer default 0 not null, '
                'osname varchar(64) not null );')
    cur.execute('create table type ( tid integer not null constraint type_pk primary key autoincrement, name varchar('
                '32) not null );')
    con.commit()


def getAllApiType():
    result = cur.execute('select * from type;')
    result = [dict(row) for row in result.fetchall()]  # cover Cursor to dict
    return packetUtils.simplePacket(0x01, 'success', result)


def getOneApi(aid):
    result = cur.execute('select * from api where aid="{}" limit 1;'.format(aid)).fetchone()
    total = len(result)
    if total == 0:
        return packetUtils.simplePacket(0x00, 'no more data!', {}, total)
    else:
        result = dict(result[0])  # cover Cursor to dict, only one
        return packetUtils.simplePacket(0x01, 'success', result, total)


def getAllApi():
    result = cur.execute('select * from api;')
    result = [dict(row) for row in result.fetchall()]  # cover Cursor to dict
    return packetUtils.simplePacket(0x01, 'success', result)


def addOneApi(api_name, api_url, api_type):
    cur.execute('INSERT INTO api (name,url,type) VALUES ("{}", "{}", "{}");'.format(api_name, api_url, api_type))


def getOneServer(sid):
    result = cur.execute('select * from server where sid="{}" limit 1;'.format(sid)).fetchone()
    total = len(result)
    if total == 0:
        return packetUtils.simplePacket(0x00, 'no more data!', {}, total)
    else:
        result = dict(result[0])  # cover Cursor to dict, only one
        return packetUtils.simplePacket(0x01, 'success', result, total)


def getAllServer():
    result = cur.execute('select * from server;')
    result = [dict(row) for row in result.fetchall()]  # cover Cursor to dict
    return packetUtils.simplePacket(0x01, 'success', result)


def addOneServer(vps_id, vps_name, virt, os_name):
    cur.execute('INSERT INTO server (vpsid,vpsname,virt,osname) VALUES ("{}", "{}", "{}", "{}");'.format(vps_id, vps_name, virt, os_name))


def getApiType(api_type):
    result = cur.execute('SELECT * FROM type WHERE tid="{}" LIMIT 1;'.format(api_type)).fetchone()
    total = len(result)
    if total <= 0:
        return packetUtils.simplePacket(0x00, 'no more data!', {}, total)
    else:
        result = dict(result[0])  # cover Cursor to dict, only one
        return packetUtils.simplePacket(0x01, 'success', result, total)
