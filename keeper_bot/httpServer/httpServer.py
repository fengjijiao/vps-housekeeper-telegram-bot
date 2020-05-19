#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import flask
import sys
import signal
import importlib
import keeper_bot.utils.dbUtils as dbUtils
from keeper_bot.utils import processUtils
import keeper_bot.config as staticGlobal  # 全局配置
from gevent.pywsgi import WSGIServer

app = flask.Flask(__name__)
app.debug = staticGlobal.HTTP_SERVER_DEBUG
app.secret_key = staticGlobal.APP_SESSION_SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
processName = 'httpServer'


def loginAuth(func):  # 验证用户身份的装饰器
    @functools.wraps(func)  # 作用是保持被装饰函数的函数名,因为url_for是根据函数名来的,如果不保持会报错,或者使用endpoint取别名
    def inner(*args, **kwargs):
        user = flask.session.get('authKey', '')
        if user != staticGlobal.ADMIN_LOGIN_AUTHKEY:
            return flask.redirect("/login")
        return func(*args, **kwargs)

    return inner


@app.route('/login', methods=['GET', 'POST'])
def actionLogin():
    if flask.request.method == 'GET':
        authKey = flask.session.get('authKey', '')
        if authKey == staticGlobal.ADMIN_LOGIN_AUTHKEY:
            tip = 'already login!'
        else:
            tip = ''
        return flask.render_template('login.html', tip=tip)
    else:
        authKey = flask.request.form.get('authKey', '')
        if authKey == staticGlobal.ADMIN_LOGIN_AUTHKEY:
            flask.session['authKey'] = authKey
            return flask.redirect('/')
        else:
            return flask.render_template('login.html', tip='account no found or password error!')


@app.route('/')
@loginAuth
def hello_world():
    return 'Hello, World!'


@app.route('/v1/getAllApiType')
@loginAuth
def getAllApiType():
    return dbUtils.getAllApiType()


@app.route('/v1/getAllApi')
@loginAuth
def getAllApi():
    return dbUtils.getAllApi()


@app.route('/v1/getOneApi/<int:api_id>')
@loginAuth
def getOneApi(api_id):
    return dbUtils.getOneApi(api_id)


@app.route('/v1/addOneApi')
@loginAuth
def addOneApi():
    api_name = flask.request.form.get('apiName', '')
    api_type = flask.request.form.get('apiType', '')
    api_url = flask.request.form.get('apiUrl', '')
    return dbUtils.addOneApi(api_name, api_type, api_url)


@app.route('/v1/refreshOneApi/<int:api_id>')
@loginAuth
def refreshOneApi(api_id):
    api_info = dbUtils.getOneApi(api_id, returnData=True)
    api_type = dbUtils.getApiType(api_info['type'], returnData=True)
    apiModule = importlib.import_module('keeper_bot.api.' + api_type['name'])  # 动态调用类
    if hasattr(apiModule, 'isCanToUse'):
        isCanToUse = getattr(apiModule, 'isCanToUse')
        if not isCanToUse():
            print('can not use {} library!'.format(api_type['name']))
            return 'can not use {} library!'.format(api_type['name'])
        else:
            print('can use {} library!'.format(api_type['name']))
            # return dbUtils.addOneApi(api_name, api_type, api_url)
            return 'can use {} library!'.format(api_type['name'])
    else:
        print('no support api type {}!'.format(api_type['name']))
        return 'no support api type {}!'.format(api_type['name'])


@app.route('/v1/getAllServer')
@loginAuth
def getAllServer():
    return dbUtils.getAllServer()


@app.route('/v1/getOneServer/<int:server_id>')
@loginAuth
def getOneServer(server_id):
    return dbUtils.getOneServer(server_id)


class MiddleWare:
    def __init__(self, wsgi_app):
        print("__init__")  # only start http server
        self.wsgi_app = wsgi_app

    def __call__(self, *args, **kwargs):
        print("__call__")  # per request
        return self.wsgi_app(*args, **kwargs)


def InterruptF():
    processUtils.del_running(processName)


def run():
    if not processUtils.is_running(processName):
        processUtils.set_running(processName)
        print(processName, '启动成功')
        signal.signal(signal.SIGTERM | signal.SIGINT, InterruptF)  # 暂时无效果
        app.wsgi_app = MiddleWare(app.wsgi_app)
        # debug
        # app.run()
        # production
        http_server = WSGIServer((staticGlobal.HTTP_SERVER_LISTEN_ADDRESS, staticGlobal.HTTP_SERVER_LISTEN_PORT), app)
        http_server.serve_forever()
    else:
        print(processName, '已经启动了')
        sys.exit(1)
