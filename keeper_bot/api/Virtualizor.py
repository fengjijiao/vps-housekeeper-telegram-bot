#!/usr/bin/env python
# -*- coding:utf-8 -*-
from urllib.parse import urlparse
API_TYPE = "Virtualizor"


def isCanToUse():
    return True


def isCanGetAllServer():
    return True


def getAllServerInfo():
    aaa = 1  # https://hostname:4083/index.php?act=listvs


def generateApiUrl(url, action):
    return 'https://{}/index.php?act={}&api=json&apikey=your_api_key&apipass=your_api_pass'.format(getNetLocViaUrl(url), action)


def getNetLocViaUrl(url):
    serverInfo = urlparse(url)
    return serverInfo.netloc
