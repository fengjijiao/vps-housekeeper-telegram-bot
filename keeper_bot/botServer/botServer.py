#!/usr/bin/env python
# -*- coding:utf-8 -*-
import signal
import telebot
import logging
from telebot import apihelper
import sys
import keeper_bot.config as staticGlobal  # 全局配置
from keeper_bot.utils import processUtils

apihelper.proxy = {'https': 'socks5://127.0.0.1:1082'}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(staticGlobal.TELEGRAM_BOT_APIKEY)
processName = 'botServer'


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Howdy, how are you doing?')


def InterruptF():
    processUtils.del_running(processName)


def run():
    if not processUtils.is_running(processName):
        processUtils.set_running(processName)
        print(processName, '启动成功')
        signal.signal(signal.SIGTERM | signal.SIGINT, InterruptF)# 暂时无效果
        bot.polling()
    else:
        print(processName, '已经启动了')
        sys.exit(1)
