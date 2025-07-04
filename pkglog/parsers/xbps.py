#!/usr/bin/python3
"Parse Void Linux xbps log messages"

from __future__ import annotations

from collections.abc import Generator, Sequence
from dataclasses import dataclass, field
from datetime import datetime

logfile = '/var/log/socklog/xbps/current'


@dataclass
class Parser:
    pkg: tuple = tuple()
    prev: dict[str, str] = field(default_factory=dict)
    vers: dict[str, str] = field(default_factory=dict)

    def get_time(self, line: str) -> datetime | None:
        fields = line.split(maxsplit=9)
        if len(fields) < 10:
            return None

        action = pkg = ver = ''
        if fields[7] == 'updating':
            if fields[8] == 'to' and fields[6][-1] == ':':
                pkg, ver = fields[6][:-1].rsplit('-', 1)
                self.prev[pkg] = ver
        elif fields[8] == 'successfully':
            if (func := fields[6]) == 'Installed':
                pkg, ver = fields[7][1:-1].rsplit('-', 1)
                oldver = self.vers.get(pkg, '')
                self.vers[pkg] = ver
                if ver == oldver:
                    action = 'reinstalled'
                elif oldver:
                    # The only way using xbps to get "Installed" with a version
                    # change is when a downgrade happens.
                    action = 'downgraded'
                    ver = f'{oldver} -> {ver}'
                else:
                    action = 'installed'

            elif func == 'Updated':
                pkg, ver = fields[7][1:-1].rsplit('-', 1)
                oldver = self.prev.get(pkg, '?')
                self.vers[pkg] = ver
                ver = f'{oldver} -> {ver}'
                action = 'upgraded'
            elif func == 'Removed':
                pkg, ver = fields[7][1:-1].rsplit('-', 1)
                self.vers.pop(pkg, None)
                action = 'removed'

        if not action:
            return None

        self.pkg = action, pkg, ver
        dts = line[:19].strip() + '+00:00'
        return datetime.fromisoformat(dts).astimezone().replace(tzinfo=None)

    def get_packages(self) -> Generator[Sequence[str]]:
        yield self.pkg
