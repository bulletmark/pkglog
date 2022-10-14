#!/usr/bin/python3
'Parse RedHat/Fedora DNF log messages'
import re
from datetime import datetime

logfile = '/var/log/dnf.rpm.log'
priority = 3

# Action mapped to log entry and is_change? flag = yes(1)/no(0)
ACTIONS = {
    'Upgraded': ('upgraded', 1),
    'Downgraded': ('downgraded', 1),
    'Installed': ('installed', 0),
    'Erase': ('removed', 0),
    'Reinstalled': ('reinstalled', 0),
}

class g:
    vers = {}
    pkgs = None

def get_time(line):
    fields = line.split(maxsplit=3)

    if len(fields) != 4:
        return None

    dtstr, key, action, rest = fields

    if key != 'SUBDEBUG':
        return None

    action = action[:-1]
    pkg = re.sub(r'\.[^.]+$', '', rest)
    m = re.match(r'^(.+?)-(\d.*)$', pkg)
    pkg, vers = m.group(1), m.group(2)

    action, change = ACTIONS.get(action, (None, 0))
    if not action:
        g.vers[pkg] = vers
        return None

    if change:
        vers = vers + ' -> ' + g.vers.get(pkg, '?')

    g.pkgs = (action, pkg, vers)

    index = dtstr.find('+')
    if index < 0:
        dtstr = dtstr.replace('Z', '+00:00')
    else:
        dtstr = dtstr[:index + 3] + ':' + dtstr[index + 3:]

    return datetime.fromisoformat(dtstr).astimezone().replace(tzinfo=None)

def get_packages():
    yield g.pkgs
