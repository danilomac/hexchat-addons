# -*- coding: utf-8 -*-
"""
Description:
 Allow the use of more than 4 modes in one /mode command,
 and make op, deop, voice and devoice commands work as
 '/cs op/deop/voice/devoice #channel-that-you-are' when
 you use these commands without parameter.

Use:
 /mode +bbbbbb ban1 ban2 ban3 ban4 ban5 ban6
 /mode +b* ban1 ban2 ban3 ban4 ban5 ban6
 The two commands above is equivalents, the command will be
 automatic splited into one +bbbb and other +bb before send
 to server.

 /op
 /deop
 /voice
 /devoice
 If one of these channels is used without parameter, it
 will send a command to ChanServ op/de/voice/devoice you
 in the channel you are.

@author  : danilo (nick in freenode)
@licence : GNU General Public License 3.0 (GPL V3)
"""
__module_name__ = 'modeextend'
__module_version__ = '1.0'
__module_description__ = 'extend MODE command to allow more than 4 mode changes at once'

import hexchat

def mode(word, word_eol, cmd):
    sign = None
    modes = []
    args = word[2:]
    for m in word[1]:
        if m in '+-':
            sign = m
        elif not sign:
            return
        elif m == '*':
            modes.extend([modes[-1]] * (len(args) - len(modes)))
        else:
            modes.append(sign + m)
    if len(modes) < 5 and not '*' in word[1]:
        return
    lines = []
    channel = hexchat.get_info('channel')
    while modes:
        sign = None
        line = ['MODE', channel, '']
        for m in modes[:4]:
            if m[0] != sign:
                line[2] += m
                sign = m[0]
            else:
                line[2] += m[1]
            if m[1] in 'ovbqeIjfkl':
                line.append(args.pop(0))
        del modes[:4]
        lines.append(line)
    for line in lines:
        hexchat.command(' '.join(line))
    return hexchat.EAT_ALL

def cs(word, word_eol, command):
    if len(word) > 1:
        return
    channel = hexchat.get_info('channel')
    hexchat.command('CS %s %s' % (command, channel))
    return hexchat.EAT_ALL

hexchat.hook_command('MODE', mode)
hexchat.hook_command('OP', cs, 'OP')
hexchat.hook_command('DEOP', cs, 'DEOP')
hexchat.hook_command('VOICE', cs, 'VOICE')
hexchat.hook_command('DEVOICE', cs, 'DEVOICE')
