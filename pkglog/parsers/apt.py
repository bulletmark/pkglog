#!/usr/bin/python3
"Parse Debian/Ubuntu APT log messages"

from __future__ import annotations

import re
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from datetime import datetime

logfile = '/var/log/apt/history.log'

_ACTIONS = {
    'Upgrade': 'upgraded',
    'Downgrade': 'downgraded',
    'Install': 'installed',
    'Remove': 'removed',
    'Reinstall': 'reinstalled',
}


@dataclass
class Parser:
    action: str = ''
    line: str = ''

    def get_time(self, line: str) -> datetime | None:
        vals = line.split(':', maxsplit=1)
        if len(vals) != 2:
            return None

        func, rest = vals

        if func == 'Start-Date':
            self.action = ''
            return None

        if func == 'End-Date':
            try:
                return datetime.fromisoformat(rest[1:].strip().replace('  ', ' '))
            except Exception:
                return None

        action = _ACTIONS.get(func)
        if action:
            self.action = action
            self.line = rest[1:]
        return None

    def get_packages(self) -> Generator[Sequence[str]]:
        if self.action:
            for pline in self.line.strip().split('),'):
                pkg, vers = pline.split(maxsplit=1)
                pkg = re.sub(':.*', '', pkg)
                vers = vers.strip().strip('()')
                vers = vers.replace(', automatic', '')
                vers = vers.replace(', ', ' -> ')
                yield self.action, pkg, vers
