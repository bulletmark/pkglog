#!/usr/bin/python3
'Parse Arch Linux pacman log messages'
from datetime import datetime

logfile = '/var/log/pacman.log'
priority = 1

class g:
    line = None

def get_date(line):
    if line[0] != '[' or ']' not in line:
        return None

    ind = line.index(']')
    dt = datetime.fromisoformat(line[1:ind][:19])
    g.line = line[ind + 2:]
    return dt

def get_packages():
    try:
        res = g.line.strip().split(maxsplit=3)[1:]
    except Exception:
        res = None

    if res and len(res) == 3:
        res[2] = res[2][1:-1]
        yield res
