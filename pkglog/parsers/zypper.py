#!/usr/bin/python3
"Parse OpenSUSE zypper log format"

import sys
from datetime import datetime

# User may want to chmod 755 the "/var/log/zypp" directory so they can
# run this tool as normal user.
logfile = '/var/log/zypp/history'

_pkgs = {}  # type: ignore


class g:
    pkg = None
    vers = None
    oldvers = None
    removed = None


def get_time(line):
    vals = line.split('|', maxsplit=4)
    if len(vals) < 4:
        return None

    dts, func, pkg, vers, _ = vals

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

    try:
        dt = datetime.fromisoformat(dts.strip())
    except Exception:
        return None

    return dt


def get_packages():
    try:
        from looseversion import LooseVersion as Version  # type: ignore
    except Exception:
        sys.exit(
            'Error: Need to install Python looseversion package to use zypper parsing.'
        )

    if g.removed:
        action = 'removed'
    elif g.oldvers:
        vers = Version(g.vers)
        oldvers = Version(g.oldvers)
        if vers == oldvers:
            action = 'reinstalled'
        else:
            action = 'upgraded' if vers > oldvers else 'downgraded'
            g.vers = f'{g.oldvers} -> {g.vers}'
    else:
        action = 'installed'

    yield action, g.pkg, g.vers
