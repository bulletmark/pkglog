#!/usr/bin/python3
"Parse RedHat/Fedora DNF log messages"

import re
from datetime import datetime

logfile = '/var/log/dnf.rpm.log'

# Action mapped to log entry and is_change? flag = yes(1)/no(0)
ACTIONS = {
    'Upgraded': ('upgraded', 1),
    'Downgraded': ('downgraded', 1),
    'Installed': ('installed', 0),
    'Erase': ('removed', 0),
    'Reinstalled': ('reinstalled', 0),
}


class g:
    vers = {}  # type: ignore
    pkgs = None  # type: ignore


def get_time(line):
    fields = line.split(maxsplit=3)

    if len(fields) != 4:
        return None

    dts, key, action, rest = fields

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

    dts = dts.strip()
    index = dts.find('+')
    if index < 0:
        dts = dts.replace('Z', '+00:00')
    else:
        dts = dts[: index + 3] + ':' + dts[index + 3 :]

    # Return the logged time in localtime
    try:
        dt = datetime.fromisoformat(dts).astimezone().replace(tzinfo=None)
    except Exception:
        return None

    return dt


def get_packages():
    yield g.pkgs
