#!/usr/bin/env python
#-*- coding:utf-8 -*-
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import *
import requests,sqlite3,logging,re,json,xmltodict,os

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#logger = logging.getLogger(__name__)
ADDTYPE, ADDURL, ADDNAME= range(3)
var = {}
con = sqlite3.connect("Bot.db",check_same_thread=False)
cur = con.cursor()
if(not os.path.exists("Bot.db")):
    cur.execute('CREATE TABLE api (id INTEGER PRIMARY KEY, name VARCHAR(20) UNIQUE, url VARCHAR(512) UNIQUE, type VARCHAR(16))')
    con.commit()

def hello(bot, update):
    update.message.reply_text('Hello, {} {}! '.format(update.message.from_user.first_name,update.message.from_user.last_name))

def echo(bot, update,args):
    update.message.reply_text(args[0])

def add(bot, update):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    reply_keyboard = [['solusvm', 'virtualizor']]
    update.message.reply_text(
        'Please select a type of Server API?\n'
        'Send /cancel to stop talking to me.\n\n'
        'optionable solusvm, virtualizor'
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ADDTYPE

def input_add_type(bot, update):
    global var
    user = update.message.from_user
    var["type"] = update.message.text
    #logger.info("TYPE of %s: %s", user.id, update.message.text)
    update.message.reply_text('Please input API URL. \n'
    	                      'solusvm URL example: CC\n'
    	                      'virtualizor URL example: https://hostname:4083/index.php?svs=id_of_the_vps&api=json&apikey=your_api_key&apipass=your_api_pass\n'
                              'so I know what you look like, or send /cancel if you don\'t want to.',
    reply_markup=ReplyKeyboardRemove())
    return ADDURL

def input_add_url(bot, update):
    global var,con,cur
    user = update.message.from_user
    var["url"] = update.message.text
    #logger.info("URL of %s: %s", user.id, update.message.text)
    if(re.match('(https?)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]',update.message.text)):
        cur.execute('select * from api where url="{}"'.format(update.message.text))
        if(len(cur.fetchall()) >= 1):
            update.message.reply_text('value of url is used \n'
                                  'Please try again type \n'
                                  'so I know what you look like, or send /cancel if you don\'t want to.',
            reply_markup=ReplyKeyboardRemove())
            return ADDURL
        else:
            update.message.reply_text('check API URL is succeed \n'
                                      'Next step, Please input a name of server. \n'
                                      'so I know what you look like, or send /cancel if you don\'t want to.',
            reply_markup=ReplyKeyboardRemove())
            return ADDNAME
    else:
        update.message.reply_text('check API url is failure \n'
                                  'Please try again type \n'
                                  'so I know what you look like, or send /cancel if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove())
        return ADDURL

def input_add_name(bot, update):
    global var,con,cur
    user = update.message.from_user
    var["name"] = update.message.text.lower()
    #logger.info("CHECK of %s: %s", user.id, update.message.text.lower())
    if(update.message.text!=None):
        cur.execute('select * from api where name="{}"'.format(update.message.text.lower()))
        if(len(cur.fetchall()) >= 1):
            update.message.reply_text('value of name is used \n'
                                      'Please try again type \n'
                                      'so I know what you look like, or send /cancel if you don\'t want to.',
            reply_markup=ReplyKeyboardRemove())
            return ADDNAME
        else:
            cur.execute('INSERT INTO api (name, url, type) VALUES("{}", "{}", "{}")'.format(var["name"],var["url"],var["type"]))
            con.commit()
            update.message.reply_text('add to db is succeed. \n',
                                      reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    else:
        update.message.reply_text('value of name is invalid. \n'
                                  'so I know what you look like, or send /cancel if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove())
        return ADDNAME

def cancel(bot, update):
    user = update.message.from_user
    #logger.info("User %s canceled the conversation.", user.id)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def bw(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("bw of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=info&bw=true",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    bw=data["bw"].split(",")
                    bwtotal=bytes(int(bw[0]))
                    bwused=bytes(int(bw[1]))
                    bwfree=bytes(int(bw[2]))
                    bwpercentused=bw[3]
                    msg=data["hostname"]+" ( "+data["ipaddress"]+" )\n"+"Total: "+bwtotal+"\nUsed: "+bwused+"\nFree: "+bwfree+"\nUsed Percent: "+bwpercentused+"%"
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url,timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    msg=data["info"]["hostname"]+" ( "+data["info"]["ip"][0]+" )\n"+"Total: "+str(data["info"]["bandwidth"]["limit_gb"])+"GB\nUsed: "+str(data["info"]["bandwidth"]["used_gb"])+"GB\nFree: "+str(data["info"]["bandwidth"]["free_gb"])+"GB\nUsed Percent: "+str(data["info"]["bandwidth"]["percent"])+"%"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def hdd(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("hdd of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=info&hdd=true",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    hdd=data["hdd"].split(",")
                    hddtotal=bytes(int(hdd[0]))
                    hddused=bytes(int(hdd[1]))
                    hddfree=bytes(int(hdd[2]))
                    hddpercentused=hdd[3]
                    msg=data["hostname"]+" ( "+data["ipaddress"]+" )\n"+"Total: "+hddtotal+"\nUsed: "+hddused+"\nFree: "+hddfree+"\nUsed Percent: "+hddpercentused+"%"
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url,timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    msg=data["info"]["hostname"]+" ( "+data["info"]["ip"][0]+" )\n"+"Total: "+str(data["info"]["disk"]["limit_gb"])+"GB\nUsed: "+str(data["info"]["disk"]["used_gb"])+"GB\nFree: "+str(data["info"]["disk"]["free_gb"])+"GB\nUsed Percent: "+str(data["info"]["disk"]["percent"])+"%"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def mem(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("mem of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=info&mem=true",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    mem=data["mem"].split(",")
                    memtotal=bytes(int(mem[0]))
                    memused=bytes(int(mem[1]))
                    memfree=bytes(int(mem[2]))
                    mempercentused=mem[3]
                    msg=data["hostname"]+" ( "+data["ipaddress"]+" )\n"+"Total: "+memtotal+"\nUsed: "+memused+"\nFree: "+memfree+"\nUsed Percent: "+mempercentused+"%"
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url,timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    msg=data["info"]["hostname"]+" ( "+data["info"]["ip"][0]+" )\n"+"Total: "+str(data["info"]["ram"]["limit"])+"MB\nUsed: "+str(data["info"]["ram"]["used"])+"MB\nFree: "+str(data["info"]["ram"]["free"])+"MB\nUsed Percent: "+str(data["info"]["ram"]["percent"])+"%"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def ipaddr(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("ipaddr of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=info&ipaddr=true",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    ipaddr=data["ipaddr"].split(",")
                    msg=data["hostname"]+" ( "+data["ipaddress"]+" )\n"
                    for i in range(len(ipaddr)):
                        msg+=ipaddr[i]+"\n"
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url,timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    msg=""
                    for i in range(data["info"]["ip_count"]):
                        msg+=data["info"]["ip"][i]+"\n"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def reboot(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("reboot of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=reboot",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    msg=data["statusmsg"]
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url+"&act=restart",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    #print(json.dumps(data))
                    msg="rebooted" if data["status"]==1 else "failure"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def boot(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("boot of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=boot",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    msg=data["statusmsg"]
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url+"&act=start",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    #print(json.dumps(data))
                    msg="booted" if data["status"]==1 else "failure"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def shutdown(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("shutdown of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
        	#logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=shutdown",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    msg=data["statusmsg"]
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url+"&act=stop",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    #print(json.dumps(data))
                    msg="shutdowned" if data["status"]==1 else "failure"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def status(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("status of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            api_info_url=api_info[0][2]
            api_info_type=api_info[0][3]
            if(api_info_type=="solusvm"):
                r = requests.get(api_info_url+"&action=status",timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=xmltodict.parse("<data>"+r.text+"</data>")["data"]
                    #print(json.dumps(data))
                    msg=data["statusmsg"]
            elif(api_info_type=="virtualizor"):
                r = requests.get(api_info_url,timeout=6)
                msg="API error!"
                if(r.status_code==200):
                    data=json.loads(r.text)
                    #print(json.dumps(data))
                    msg="online" if data["info"]["status"]==1 else "offline"
            update.message.reply_text(msg)
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def delete(bot, update,args):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    if(args):
        user = update.message.from_user
        #logger.info("delete of %s: %s", user.id, args[0].lower())
        cur.execute('select * from api where name="{}"'.format(args[0].lower()))
        api_info=cur.fetchall()
        if(len(api_info) >= 1):
            #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
            if(cur.execute('delete from api where name="{}"'.format(args[0].lower()))):
                update.message.reply_text("succeed")
            else:
                update.message.reply_text("failed")
        else:
            update.message.reply_text('This name was no found. ')
    else:
        update.message.reply_text('This command is invalid. ')

def list(bot, update):
    if(not power_check(update)):
        return update.message.reply_text("No Power !")
    user = update.message.from_user
    #logger.info("list of %s", user.id)
    cur.execute('select * from api')
    api_info=cur.fetchall()
    if(len(api_info) >= 1):
        #logger.info("api_info of %s: %s", user.id, str(api_info[0]))
        msg=""
        for i in range(len(api_info)):
            msg+=str(api_info[i][0])+". [ "+api_info[i][3]+" ] "+api_info[i][1]+"\n"
        update.message.reply_text(msg)
    else:
        update.message.reply_text('This datebase is empty. ')

def myinfo(bot, update):
    user = update.message.from_user
    #logger.info("myinfo of %s", user.id)
    msg="ID: "+ str( user.id ) + "\n"
    msg+="Bot: "+ str( user.is_bot )+ "\n"
    msg+="First Name: "+ str( user.first_name ) + "\n"
    msg+="Last Name: "+ str( user.last_name ) + "\n"
    msg+="username: "+ str( user.username ) + "\n"
    msg+="Language Code: "+ str( user.language_code ) + "\n"
    update.message.reply_text(msg)

def menu(bot, update):
    update.message.reply_text("/hello ,simply greet.\n/echo ,return your input content.\n/astatus ,return api sum status.\n/servers ,return NQ node info.\n/list ,return all node name.\n/add ,add one node.\n/delete ,delete one node.\n/bw ,return one node for bandwidth.\n/hdd ,return one node for hdd disk.\n/ipaddr ,return one node for ip address.\n/mem ,return one node for memery.\n/boot ,boot a node.\n/reboot ,reboot a node.\n/shutdown ,shutdown a node.\n/status ,return one node for status.\n/myinfo ,return your info.")

def power_check(update):
    power_id=260685916  #Your telegram id
    if(update.message.from_user.id!=power_id):
        return False
    else:
        return True

def bytes(bytes):
    if bytes < 1024:  #bit
        bytes = str(round(bytes, 2)) + ' B' #Byte
    elif bytes >= 1024 and bytes < 1024 * 1024:
        bytes = str(round(bytes / 1024, 2)) + ' KB' #kByte
    elif bytes >= 1024 * 1024 and bytes < 1024 * 1024 * 1024:
        bytes = str(round(bytes / 1024 / 1024, 2)) + ' MB' #MByte
    elif bytes >= 1024 * 1024 * 1024 and bytes < 1024 * 1024 * 1024 * 1024:
        bytes = str(round(bytes / 1024 / 1024 / 1024, 2)) + ' GB' #KMByte
    elif bytes >= 1024 * 1024 * 1024 * 1024 and bytes < 1024 * 1024 * 1024 * 1024 * 1024:
        bytes = str(round(bytes / 1024 / 1024 / 1024 / 1024, 2)) + ' TB' #TByte
    elif bytes >= 1024 * 1024 * 1024 * 1024 * 1024 and bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        bytes = str(round(bytes / 1024 / 1024 / 1024 / 1024 / 1024, 2)) + ' PB' #PByte
    elif bytes >= 1024 * 1024 * 1024 * 1024 * 1024 * 1024 and bytes < 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        bytes = str(round(bytes / 1024 / 1024 / 1024 / 1024 / 1024 /1024, 2)) + ' EB' #EByte
    return bytes

def main():
    updater = Updater('Your telegram bot apikey')
    updater.dispatcher.add_handler(CommandHandler('hello', hello))
    updater.dispatcher.add_handler(CommandHandler('list', list))
    updater.dispatcher.add_handler(CommandHandler('myinfo', myinfo))
    updater.dispatcher.add_handler(CommandHandler('menu', menu))
    updater.dispatcher.add_handler(CommandHandler('echo', echo, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('bw', bw, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('ipaddr', ipaddr, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('hdd', hdd, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('mem', mem, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('reboot', reboot, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('boot', boot, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('shutdown', shutdown, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('status', status, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('delete', delete, pass_args=True))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            ADDTYPE: [MessageHandler(Filters.text, input_add_type)],
            ADDURL: [MessageHandler(Filters.text, input_add_url)],
            ADDNAME: [MessageHandler(Filters.text, input_add_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()