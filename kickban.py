# -*- coding: utf-8 -*-
"""
Description:
 With one command kickban an user based at IP or account,
 and request a /CS OP before if user is not op.

Use:
 /kb NICK
 /B NICK
 The script will query a /whois NICK, if the user have
 account, the ban will be $a:account, else the ban will
 be *!*@*IP, if there is no IP in user host an error is
 returned. After determined the ban, it is requested a
 /CS OP is user is not op, after ban and kick NICK. /B
 only ban.

@author  : danilo (nick in freenode)
@licence : GNU General Public License 3.0 (GPL V3)
"""
__module_name__ = 'kickban'
__module_version__ = '1.0'
__module_description__ = 'ban/kickban users'

import hexchat, re
from threading import Thread, Event
from time import sleep

hooks = []
opflag = {}
accounts = {}

def whoisAuth(word, word_eol, userdata):
    if word[1] == 'is logged in as':
        accounts[word[0]] = word[2]
    return hexchat.EAT_ALL

def whoisEnd(word, word_eol, userdata):
    if word[0] not in accounts:
        accounts[word[0]] = None
    return hexchat.EAT_ALL

def whoisPass(w, e, u):
    return hexchat.EAT_ALL

def chanop(word, word_eol, userdata):
    if word[1] == hexchat.get_info('nick'):
        opflag[hexchat.get_info('channel')] = True

def csnotice(word, word_eol, userdata):
    if word[0] == 'ChanServ' and word[1].startswith('You are not authorized to'):
        opflag[hexchat.get_info('channel')] = False

def kickban(cmd, nick):
    channel = hexchat.get_info('channel')
    ctx = hexchat.get_context()
    for user in hexchat.get_list('users'):
        if user.nick == nick:
            host = user.host
            break
    else:
        host = None
    ip = re.search(r'@.*?(\d{1,3}([.-])\d{1,3}\2\d{1,3}\2\d{1,3})', host) if host else None
    if ip:
        ip = '*!*@*' + ip.group(1).replace('-', '.')

    accban = None
    if nick not in accounts:
        if cmdWait('WHOIS ' + nick, lambda: nick in accounts,
                {'WhoIs Authenticated': whoisAuth, 'WhoIs End': whoisEnd, 'WhoIs Name Line': whoisPass,
                'WhoIs Channel/Oper Line': whoisPass, 'WhoIs Server Line': whoisPass}):
            if accounts[nick]:
                accban = '$a:' + accounts[nick]
        else:
            ctx.prnt('KICKBAN: Whois timeout')
            return
    elif accounts.get(nick):
        accban = '$a:' + accounts[nick]
    if not ip and not accban:
        ctx.prnt('KICKBAN: I did\'n found user IP nor user account')
        return

    commands = []
    if cmd in ('kb', 'ban'):
        commands.append('MODE +b ' + (accban or ip))
    if cmd == 'kb':
        commands.append('KICK ' + nick)
    if '@' not in [u.prefix for u in hexchat.get_list('users') if u.nick == hexchat.get_info('nick')]:
        opflag[channel] = None
        if cmdWait('CS OP ' + channel, lambda: opflag[channel] in (True, False),
                {'Channel Operator': chanop, 'Notice': csnotice}):
            if not opflag[channel]:
                ctx.prnt('KICKBAN: ChanServ did\'t grant op')
                return
        else:
            ctx.prnt('KICKBAN: ChanServ OP timeout')
            return
    for command in commands:
        hexchat.command(command)

def thread(word, word_eol, cmd):
    t = Thread(target=kickban, args=(cmd, word[1]))
    t.start()
    return hexchat.EAT_ALL

def cmdWait(cmd, check, sethooks):
    for hook in sethooks:
        hooks.append(hexchat.hook_print(hook, sethooks[hook]))
    hexchat.command(cmd)
    for t in range(10):
        if check():
            resp = True
            break
        sleep(.2)
    else:
        resp = False
    [hexchat.unhook(hook) for hook in hooks]
    return resp

hexchat.hook_command('KB', thread, 'kb')
hexchat.hook_command('B', thread, 'ban')
