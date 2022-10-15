#!/usr/bin/python3
'Reports log of package updates.'
# Author: Mark Blakeney, 2016->2021.

import os
import sys
import re
import argparse
import fileinput
import shlex
import fnmatch
from importlib import util, machinery
from datetime import datetime, date, time, timedelta
from pathlib import Path

TIMEGAP = 2  # mins
PATHSEP = ':'

DAYS = 30

ACTIONS = {
    'installed': (1, 'green'),
    'removed': (2, 'red'),
    'upgraded': (3, 'yellow'),
    'downgraded': (3, 'magenta'),
    'reinstalled': (4, 'cyan'),
}

MODDIR = Path(__file__).parent.resolve()
CNFFILE = Path(os.getenv('XDG_CONFIG_HOME', '~/.config'),
        f'{MODDIR.name}-flags.conf')

class Queue:
    queue = []
    installed = {}
    console = None
    boottime = None
    bootstr = None
    delim = None

    @classmethod
    def print(cls, color, *msg):
        'Output given message'
        for m in msg:
            if m:
                if cls.console:
                    cls.console.print(m, style=(color or 'white'),
                                      highlight=False)
                else:
                    print(m)

    @classmethod
    def output(cls, args):
        'Output queued set of package transactions to screen'
        if not cls.queue:
            return

        out = []
        maxlen = 1

        # First loop to extract data and determine longest package name in
        # this transaction set
        for dt, action, pkg, vers in cls.queue:
            actcode, color = ACTIONS[action]
            if args.updated_only:
                if actcode != 3:
                    continue
            if args.installed or args.installed_only:
                if actcode > 2:
                    continue
                if args.installed_only and actcode > 1:
                    continue
            if args.package:
                if args.regex:
                    if not args.regex.match(pkg):
                        continue
                elif pkg != args.package:
                    continue
            if args.installed_net:
                pkgdt = cls.installed.get(pkg)
                if not pkgdt or dt < pkgdt:
                    continue
            if actcode != 3 or args.verbose:
                vers += ' ' + action
            out.append((dt, pkg, vers, color))
            if not args.nojustify:
                maxlen = max(maxlen, len(pkg))

        # Now output justified lines to screen
        for num, (dt, pkg, vers, color) in enumerate(out):
            if cls.bootstr and dt > cls.boottime:
                cls.print(None, cls.delim, cls.bootstr, cls.delim)
                cls.bootstr = None
            elif num == 0:
                cls.print(None, cls.delim)

            cls.print(color, f'{dt} {pkg:{maxlen}} {vers}')

        cls.queue.clear()

    @classmethod
    def append(cls, dt, action, pkg, vers):
        'Append this package + action to the internal queue'
        actcode, _ = ACTIONS[action]
        if actcode == 1:
            cls.installed[pkg] = dt
        elif actcode == 2:
            cls.installed.pop(pkg, None)

        cls.queue.append((dt, action, pkg, vers))

def import_path(path):
    'Import given module path'
    modname = path.stem.replace('-', '_')
    spec = util.spec_from_loader(modname,
            machinery.SourceFileLoader(modname, str(path)))
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def compute_start_time(args):
    'Compute start time from when to output log'
    start_time = None
    days = -1
    if not args.alldays:
        timestr = args.days
        if timestr:
            try:
                days = int(timestr)
            except Exception:
                # If no day is included then prepend today
                if '-' not in timestr:
                    timestr = date.today().isoformat() + ' ' + timestr
                try:
                    start_time = datetime.fromisoformat(timestr)
                except Exception:
                    sys.exit(f'ERROR: Can not parse days value "{args.days}".')

        elif not args.package:
            days = DAYS

    if days >= 0:
        day = date.today() - timedelta(days=days)
        start_time = datetime.combine(day, time.min)

    return start_time

def main():
    parsers = {}
    order = {}
    priority = 100

    # Load all parsers
    for index, m in enumerate((MODDIR / 'parsers').glob('[!_]*.py')):
        name = m.name[:-3]
        mod = import_path(m)
        parsers[name] = mod
        prio = mod.priority if hasattr(mod, 'priority') else (priority + index)
        order[prio] = name

    # Determine default parser for this system
    for c in sorted(order):
        parser = order[c]
        if Path(parsers[parser].logfile).exists():
            break
    else:
        parser = '?'

    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip(),
            epilog=f'Note you can set default starting options in {CNFFILE}.')
    opt.add_argument('-u', '--updated-only', action='store_true',
            help='show updated only')
    opt.add_argument('-i', '--installed', action='store_true',
            help='show installed/removed only')
    opt.add_argument('-I', '--installed-only', action='store_true',
            help='show installed only')
    opt.add_argument('-n', '--installed-net', action='store_true',
            help='show net installed only')
    opt.add_argument('-d', '--days',
            help='show all packages only from given number of days ago, '
            f'or from given YYYY-MM-DD[?HH:MM[:SS]], default={DAYS}(days), '
            '0=today, -1=all. If only time is specified, then today is '
            'assumed.')
    opt.add_argument('-a', '--alldays', action='store_true',
            help='show all packages for all days (same as "--days=-1")')
    opt.add_argument('-j', '--nojustify', action='store_true',
            help='don\'t right justify version numbers')
    opt.add_argument('-v', '--verbose', action='store_true',
            help='be verbose, describe upgrades/downgrades')
    opt.add_argument('-c', '--no-color', action='store_true',
            help='do not color output lines')
    opt.add_argument('-p', '--parser', choices=parsers,
            help=f'log parser type, default={parser}')
    opt.add_argument('-t', '--timegap', type=float, default=TIMEGAP,
            help=f'max minutes gap between grouped updates, default={TIMEGAP}')
    opt.add_argument('-P', '--path',
            help='alternate log path[s] '
            f'(separate multiple using "{PATHSEP}", must be time sequenced)')
    grp = opt.add_mutually_exclusive_group()
    grp.add_argument('-g', '--glob', action='store_true',
            help='given package name is glob pattern to match')
    grp.add_argument('-r', '--regex', action='store_true',
            help='given package name is regular expression to match')
    opt.add_argument('package', nargs='?',
            help='specific package name to report')

    # Merge in default options from user config file. Then parse the
    # command line.
    cnflines = ''
    cnffile = CNFFILE.expanduser()
    if cnffile.exists():
        with cnffile.open() as fp:
            cnflines = [re.sub(r'#.*$', '', line).strip() for line in fp]
        cnflines = ' '.join(cnflines).strip()

    args = opt.parse_args(shlex.split(cnflines) + sys.argv[1:])

    if not args.no_color:
        try:
            from rich.console import Console
        except Exception:
            args.no_color = True
        else:
            Queue.console = Console()

    if args.parser:
        parser = args.parser

    if args.package:
        if args.glob:
            args.package = fnmatch.translate(args.package)
            args.regex = True

        if args.regex:
            args.regex = re.compile(args.package)
    else:
        args.regex = None

    if args.installed_net:
        args.installed = True

    logmod = parsers.get(parser)
    if not logmod:
        sys.exit('ERROR: Can not determine log parser for this system.')

    defpath = Path(logmod.logfile)

    if not args.package and not (args.installed or args.installed_only):
        Queue.delim = 80 * '-'

    timegap = timedelta(minutes=args.timegap)
    dt_out = datetime.max
    start_time = compute_start_time(args) or datetime.min

    if not args.package:
        # Get last boot time
        upsecs = float(Path('/proc/uptime').read_text().split()[0])
        Queue.boottime = datetime.now() - timedelta(seconds=upsecs)
        timestr = Queue.boottime.isoformat(' ', 'seconds')
        Queue.bootstr = f'{timestr} ### LAST SYSTEM BOOT ###'

    if args.path:
        pathlist = [Path(p) for p in args.path.split(PATHSEP)]
    else:
        pathlist = [defpath.parent]

    # Loop over all lines in input files
    for path in pathlist:
        if path.is_dir():
            filelist = list(path.glob(f'{defpath.name}.*'))
            filelist.sort(key=lambda x: int(re.sub(r'\D+', '', str(x)) or 0),
                    reverse=True)
            filelist.append(path / defpath.name)
        else:
            filelist = [path]

        if not filelist[-1].exists():
            sys.exit(f'ERROR: {filelist[-1]} does not exist.')

        for lineb in fileinput.input(filelist,
                openhook=fileinput.hook_compressed):
            line = lineb if isinstance(lineb, str) else lineb.decode()
            line = line.strip()
            if not line:
                continue

            dt = logmod.get_time(line)
            if not dt:
                continue

            if dt < start_time:
                continue

            if dt - dt_out > timegap and not args.installed_net:
                Queue.output(args)

            dt_out = dt

            for fields in logmod.get_packages():
                if fields and len(fields) == 3 and fields[0] in ACTIONS:
                    Queue.append(dt, *fields)

    # Flush any remaining queued output
    Queue.output(args)
    if Queue.bootstr:
        Queue.print(None, Queue.delim, Queue.bootstr)

if __name__ == '__main__':
    main()
