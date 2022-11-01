#!/usr/bin/python3
'Parse OpenSUSE zypper log format'
from datetime import datetime
from packaging.version import parse

# User may want to chmod 755 the "/var/log/zypp" directory so they can
# run this tool as normal user.
logfile = '/var/log/zypp/history'

_pkgs = {}

class g:
    pkg = None
    vers = None
    oldvers = None
    removed = None

def get_time(line):
    vals = line.split('|', maxsplit=4)
    if len(vals) < 4:
        return None

    datestr, func, pkg, vers, _ = vals

    if func == 'install':
        g.oldvers = _pkgs.get(pkg)
        _pkgs[pkg] = vers
        g.removed = False
    elif func == 'remove':
        g.oldvers = None
        _pkgs.pop(pkg, None)
        g.removed = True
    else:
        return None

    g.pkg = pkg
    g.vers = vers
    return datetime.fromisoformat(datestr)

def get_packages():
    if g.removed:
        action = 'removed'
    elif g.oldvers:
        vers = parse(g.vers)
        oldvers = parse(g.oldvers)
        if vers == oldvers:
            action = 'reinstalled'
        else:
            action = 'upgraded' if vers > oldvers else 'downgraded'
            g.vers = f'{g.oldvers} -> {g.vers}'
    else:
        action = 'installed'

    yield action, g.pkg, g.vers
