#!/usr/bin/env python
# -*- coding:utf-8 -*-
from multiprocessing import Process
import keeper_bot.botServer.botServer as botServer
import keeper_bot.httpServer.httpServer as httpServer


if __name__ == "__main__":
    botServerThread = Process(target=botServer.run)
    botServerThread.start()
    httpServerThread = Process(target=httpServer.run)
    httpServerThread.start()
