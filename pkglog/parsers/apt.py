#!/usr/bin/python3
'Parse Debian/Ubuntu APT log messages'
import re
from datetime import datetime

logfile = '/var/log/apt/history.log'
priority = 2

ACTIONS = {
    'Upgrade': 'upgraded',
    'Downgrade': 'downgraded',
    'Install': 'installed',
    'Remove': 'removed',
    'Reinstall': 'reinstalled',
}

class g:
    action = None
    line = None

def get_time(line):
    vals = line.split(':', maxsplit=1)
    if len(vals) != 2:
        return None

    func, rest = vals

    if func == 'Start-Date':
        g.action = None
        return None

    if func == 'End-Date':
        return datetime.fromisoformat(rest[1:].replace('  ', ' '))

    action = ACTIONS.get(func)
    if action:
        g.action = action
        g.line = rest[1:]
    return None

def get_packages():
    if g.action:
        for pline in g.line.strip().split('),'):
            pkg, vers = pline.split(maxsplit=1)
            pkg = re.sub(':.*', '', pkg)
            vers = vers.strip().strip('()')
            vers = vers.replace(', automatic', '')
            vers = vers.replace(', ', ' -> ')
            yield g.action, pkg, vers
