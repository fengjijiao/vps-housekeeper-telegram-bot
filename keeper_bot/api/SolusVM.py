#!/usr/bin/env python
# -*- coding:utf-8 -*-
API_TYPE = "SolusVM"


def isCanToUse():
    return True


def isCanGetAllServer():
    print(API_TYPE, "no api to get all server info!")
    return False
