#!/usr/bin/python3
"Parse OpenSUSE zypper log format"

from __future__ import annotations

import sys
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from datetime import datetime

# User may want to chmod 755 the "/var/log/zypp" directory so they can
# run this tool as normal user.
logfile = '/var/log/zypp/history'

_pkgs = {}  # type: ignore


@dataclass
class Parser:
    pkg: str = ''
    vers: str = ''
    oldvers: str = ''
    removed: bool = False

    #
    def __init__(self):
        self.pkg = ''
        self.vers = ''
        self.oldvers = ''
        self.removed = False

    def get_time(self, line: str) -> datetime | None:
        vals = line.split('|', maxsplit=4)
        if len(vals) < 4:
            return None

        dts, func, pkg, vers, _ = vals

        if func == 'install':
            self.oldvers = _pkgs.get(pkg, '')
            _pkgs[pkg] = vers
            self.removed = False
        elif func == 'remove':
            self.oldvers = ''
            _pkgs.pop(pkg, None)
            self.removed = True
        else:
            return None

        self.pkg = pkg
        self.vers = vers

        try:
            dt = datetime.fromisoformat(dts.strip())
        except Exception:
            return None

        return dt

    def get_packages(self) -> Generator[Sequence[str]]:
        try:
            from looseversion import LooseVersion as Version  # type: ignore
        except Exception:
            sys.exit(
                'Error: Need to install Python looseversion package to use zypper parsing.'
            )

        if self.removed:
            action = 'removed'
        elif self.oldvers:
            vers = Version(self.vers)
            oldvers = Version(self.oldvers)
            if vers == oldvers:
                action = 'reinstalled'
            else:
                action = 'upgraded' if vers > oldvers else 'downgraded'
                self.vers = f'{self.oldvers} -> {self.vers}'
        else:
            action = 'installed'

        yield action, self.pkg, self.vers
