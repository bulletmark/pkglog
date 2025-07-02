#!/usr/bin/python3
"Parse Arch Linux pacman log messages"

from __future__ import annotations

import sys
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from datetime import datetime

logfile = '/var/log/pacman.log'

_LINETYPES = {'[ALPM]', '[PACMAN]'}


@dataclass
class Parser:
    line: str = ''

    def get_time(self, line: str) -> datetime | None:
        # Handle old format pacman logs
        if len(line) > 11 and line[11] == ' ':
            line = line[:11] + 'T' + line[12:]

        vals = line.split(maxsplit=2)
        if len(vals) != 3:
            return None

        dts, linetype, rest = vals

        if linetype not in _LINETYPES:
            return None

        # Pacman log sometimes has stray leading nulls
        dts = dts.lstrip().lstrip('\0').strip()

        # Add missing ":" in timezone which fromisoformat() < 3.11 requires
        if sys.version_info < (3, 11) and ('+' in dts or '-' in dts):
            if len(dts) < 24:
                return None
            dts = f'{dts[:23]}:{dts[23:]}'

        try:
            dt = datetime.fromisoformat(dts[1:-1])
        except Exception:
            return None

        self.line = rest

        # We also convert the logged time to localtime
        return dt.astimezone().replace(tzinfo=None)

    def get_packages(self) -> Generator[Sequence[str]]:
        try:
            res = self.line.strip().split(maxsplit=2)
        except Exception:
            return

        if res and len(res) == 3:
            res[2] = res[2][1:-1]
            yield res
