#!/usr/bin/python3
'Parse Arch Linux pacman log messages'
from datetime import datetime

logfile = '/var/log/pacman.log'
priority = 1

class g:
    line = None

def get_time(line):
    if line[0] != '[' or ']' not in line:
        return None

    ind = line.index(']')
    dts = line[1:ind]
    if len(dts) != 24:
        return None

    g.line = line[ind + 2:]

    # Add missing ":" in timezone which fromisoformat() requires
    dt = datetime.fromisoformat(f'{dts[:22]}:{dts[22:]}')
    return dt.astimezone().replace(tzinfo=None)

def get_packages():
    try:
        res = g.line.strip().split(maxsplit=3)[1:]
    except Exception:
        res = None

    if res and len(res) == 3:
        res[2] = res[2][1:-1]
        yield res
