#!/usr/bin/python3
'Parse Debian/Ubuntu APT log messages'
import re
from datetime import datetime

logfile = '/var/log/apt/history.log'
priority = 2

ACTIONS = {
    'Upgrade': 'upgraded',
    'Install': 'installed',
    'Remove': 'removed',
    'Downgrade': 'downgraded',
}

class g:
    action = None
    line = None

def get_time(line):
    if line.startswith('End-Date:'):
        return datetime.fromisoformat(line[10:].replace('  ', ' '))

    if line.startswith('Start-Date:'):
        g.action = None
    else:
        for act in ACTIONS:
            if line.startswith(f'{act}:'):
                g.line = line[line.index(':') + 2:]
                g.action = ACTIONS[act]
                break

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
