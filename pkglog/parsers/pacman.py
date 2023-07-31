#!/usr/bin/python3
'Parse Arch Linux pacman log messages'
from datetime import datetime

logfile = '/var/log/pacman.log'

LINETYPES = {'[ALPM]', '[PACMAN]'}

class g:
    line = None

def get_time(line):
    vals = line.split(maxsplit=2)
    if len(vals) != 3:
        return None

    dts, linetype, rest = vals

    if linetype not in LINETYPES:
        return None

    # Pacman log sometimes has stray leading nulls
    dts = dts.lstrip().lstrip('\0').strip()

    # Add missing ":" in timezone which fromisoformat() requires
    try:
        dt = datetime.fromisoformat(f'{dts[1:23]}:{dts[23:-1]}')
    except Exception:
        return None

    g.line = rest

    # We also convert the logged time to localtime
    return dt.astimezone().replace(tzinfo=None)

def get_packages():
    try:
        res = g.line.strip().split(maxsplit=2)
    except Exception:
        return

    if res and len(res) == 3:
        res[2] = res[2][1:-1]
        yield res
