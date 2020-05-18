#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json


# status:0:error,1:success,2:danger,3:warning
def simplePacket(status, msg, data, total=None):
    result = dict()
    result['status'] = status
    result['msg'] = msg
    result['data'] = data
    if total is None:
        result['total'] = len(data)
    else:
        result['total'] = total
    return json.dumps(result)
