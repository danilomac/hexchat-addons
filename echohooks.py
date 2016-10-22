# -*- coding: utf-8 -*-
"""
Description:
 Echo event parameters in the frrenode tab. This is intended to be use
 for development propose, to know when the text event is used and its
 parameters

Use:
 /hook NAME : hook NAME event, the parameters will be print in the
              freenode tab when the event occurs
 /unhook    : unhook all hooks hooked by this plugin

Example:
 /hook Whois Name Line
 This line will hook this event. When you receives a whois data,
 the parameters of the Whois Name Line are showed in the freenode
 tab
 Note: the events names are case insensitive

@author  : danilo (nick in freenode)
@licence : GNU General Public License 3.0 (GPL V3)
"""
__module_name__ = "echohooks"
__module_version__ = "1.0"
__module_description__ = "echo hooks in freenode tab (server tab, not channel)"

import hexchat

hooks = []
freenode = hexchat.find_context(channel='freenode')

def prnt(txt):
    global freenode
    if not freenode:
        freenode = hexchat.find_context(channel='freenode')
    freenode.prnt(txt)

def echo(word, word_eol, cmd):
    prnt('\x0303%s\x03: %r' % (cmd, word))

def makehook(word, word_eol, userdata):
    hooks.append((word_eol[1], hexchat.hook_print(word_eol[1], echo, word_eol[1])))
    prnt('%s hooked' % word_eol[1])
    return hexchat.EAT_ALL

def unhook(word, word_eol, userdata):
    unhooked = []
    while hooks:
        name, hook = hooks.pop()
        hexchat.unhook(hook)
        unhooked.append(name)
    prnt('unhooked: ' + (', '.join(unhooked) or 'None'))
    return hexchat.EAT_ALL

hexchat.hook_command('HOOK', makehook)
hexchat.hook_command('UNHOOK', unhook)
