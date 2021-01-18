#!/usr/bin/python3
'Parse RedHat/Fedora DNF log messages'
import re
from datetime import datetime

logfile = '/var/log/dnf.rpm.log'
priority = 3

ACTIONS = {
    'Upgraded': 'upgraded',
    'Installed': 'installed',
    'Erase': 'removed',
    'Downgraded': 'downgraded',
}

CHANGES = {'u', 'd'}

class g:
    vers = {}
    pkgs = None

def get_date(line):
    if ' SUBDEBUG ' not in line:
        return None
    dtstr, _, action, rest = line.split(maxsplit=3)
    index = dtstr.find('+')
    if index >= 0:
        dtstr = dtstr[:index + 3] + ':' + dtstr[index + 3:]
    dtstr = dtstr.replace('Z', '+00:00')
    dt = datetime.fromisoformat(dtstr).astimezone().replace(tzinfo=None)
    action = action[:-1]
    pkg = re.sub(r'\.[^.]+$', '', rest)
    m = re.match(r'^(.+?)-(\d.*)$', pkg)
    pkg, vers = m.group(1), m.group(2)

    action = ACTIONS.get(action)
    if not action:
        g.vers[pkg] = vers
        return None

    if action[0] in CHANGES:
        vers = vers + ' -> ' + g.vers.get(pkg, '?')

    g.pkgs = (action, pkg, vers)
    return dt

def get_packages():
    yield g.pkgs
