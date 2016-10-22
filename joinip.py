# -*- coding: utf-8 -*-
"""
Description:
 Shows the city, region and country for each user that join
 a channelthat have yhe ip in the host. The IP data is
 requested only one time per IP and it keep stored untill
 hexchat is closed.

@author  : danilo (nick in freenode)
@licence : GNU General Public License 3.0 (GPL V3)
"""
__module_name__ = 'joinip'
__module_version__ = '1.0'
__module_description__ = 'Show IP localization when user join'

import hexchat
import re, json
from threading import Thread, Lock
from urllib2 import urlopen

iplist = {}
lock = Lock()

def encd(txt):
    if type(txt) == unicode:
        return txt.encode('utf-8')
    else:
        return txt

def ipAPI(name, ip, chan):
    lock.acquire()
    if ip not in iplist:
        try:
            api = urlopen('http://ip-api.com/json/' + ip, timeout=1)
        except:
            lock.release()
            return
        r = json.loads(api.read().decode('utf-8'))
    else:
        r = iplist[ip]
    lock.release()
    if r['status'] == 'success':
        iplist[ip] = r
        ctx = hexchat.find_context(channel=chan)
        ctx.prnt('\x0303\%s: %s, %s, %s' % (name, encd(r.get('city', '')),
            encd(r.get('regionName', '')), encd(r.get('country', ''))))

def ipDetail(word, word_eol, userdata):
    ip = re.search(r'@.*?(\d{1,3}([.-])\d{1,3}\2\d{1,3}\2\d{1,3}|[0-9a-f-A-F]{1,4}(?:::?[0-9a-fA-F]{1,4}){1,7})', word[2])
    if ip:
        t = Thread(target=ipAPI, args=(word[0], ip.group(1).replace('-', '.'), word[1]))
        t.start()


hexchat.hook_print('Join', ipDetail)
