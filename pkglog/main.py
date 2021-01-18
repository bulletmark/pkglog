#!/usr/bin/python3
'Reports log of package updates.'
# Author: Mark Blakeney, 2016->2021.

import sys
import re
import argparse
import importlib
import fileinput
import shlex
from datetime import datetime, date, timedelta
from importlib.util import spec_from_loader
from pathlib import Path

TIMEGAP = 2  # mins
PATHSEP = ':'

DAYS = 30
ACTIONS_VER = {'upgraded', 'downgraded'}
ACTIONS_INSTALL = {'installed', 'removed'}
ACTIONS = {'reinstalled'} | ACTIONS_VER | ACTIONS_INSTALL

MODDIR = Path(__file__).parent.resolve()
CNFFILE = f'~/.config/{MODDIR.name}-flags.conf'

queue = []

def output(args, delim):
    'Output queued set of package transactions to screen'
    if not queue:
        return

    out = []
    maxlen = 1

    # First loop to extract data and determine longest package name in
    # this transaction set
    for dt, action, pkg, vers in queue:
        if args.installed or args.installed_only:
            if action not in ACTIONS_INSTALL:
                continue
            if args.installed_only and action == 'removed':
                continue
        if args.package and pkg != args.package:
            continue
        if action not in ACTIONS_VER or args.verbose:
            vers += ' ' + action
        out.append((dt, pkg, vers))
        if not args.nojustify:
            maxlen = max(maxlen, len(pkg))

    if out:
        if delim:
            print(delim)

        # Now output justified lines to screen
        for dt, pkg, vers in out:
            print(f'{dt} {pkg:{maxlen}} {vers}')

    queue.clear()

def import_path(path):
    'Import given module path'
    modname = path.stem.replace('-', '_')
    spec = spec_from_loader(modname,
            importlib.machinery.SourceFileLoader(modname, str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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
            epilog=f'Note you can set default starting arguments in {CNFFILE}.')
    opt.add_argument('-i', '--installed', action='store_true',
            help='show installed/removed only')
    opt.add_argument('-I', '--installed-only', action='store_true',
            help='show installed only')
    opt.add_argument('-d', '--days',
            help='show all packages only from given days ago '
            f'(or YYYY-MM-DD), default={DAYS}, -1=all')
    opt.add_argument('-a', '--alldays', action='store_true',
            help='show all packages for all days (same as "-days=-1")')
    opt.add_argument('-j', '--nojustify', action='store_true',
            help='don\'t right justify version numbers')
    opt.add_argument('-v', '--verbose', action='store_true',
            help='be verbose, describe upgrades/downgrades')
    opt.add_argument('-p', '--parser', choices=parsers,
            help=f'log parser type, default={parser}')
    opt.add_argument('-t', '--timegap', type=float, default=TIMEGAP,
            help=f'max minutes gap between grouped updates, default={TIMEGAP}')
    opt.add_argument('-P', '--path',
            help='alternate log path[s] (separate multiple using "{}", '
            'must be time sequenced)'.format(PATHSEP))
    opt.add_argument('package', nargs='?',
            help='specific package name to report')

    # Merge in default args from user config file. Then parse the
    # command line.
    cnffile = Path(CNFFILE).expanduser()
    cnfargs = shlex.split(cnffile.read_text().strip()) \
            if cnffile.exists() else []
    args = opt.parse_args(cnfargs + sys.argv[1:])

    if args.parser:
        parser = args.parser

    logmod = parsers.get(parser)
    if not logmod:
        sys.exit('ERROR: Can not determine log parser for this system.')

    defpath = Path(logmod.logfile)

    delim = 80 * '-' if not args.package \
            and not (args.installed or args.installed_only) else ''

    timegap = timedelta(minutes=args.timegap)

    if args.days:
        if args.days.isdigit():
            days = int(args.days)
        else:
            days = (date.today() - date.fromisoformat(args.days)).days
    else:
        days = -1 if args.package else DAYS

    if args.package:
        bootstr = None
    else:
        # Get last boot time
        upsecs = float(Path('/proc/uptime').read_text().split()[0])
        timeboot = datetime.now() - timedelta(seconds=upsecs)
        timestr = timeboot.isoformat(' ', 'seconds')
        dline = delim + '\n' if delim else ''
        bootstr = f'{dline}{timestr} ### LAST SYSTEM BOOT ###'

    start_date = date.today() - timedelta(days=days) if days >= 0 and \
            not args.alldays else None

    dt_out = datetime.max

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

            dt = logmod.get_date(line.strip())
            if not dt:
                continue

            if bootstr and dt > timeboot:
                output(args, delim)
                print(bootstr)
                bootstr = None

            if start_date and dt.date() < start_date:
                continue

            if dt - dt_out > timegap:
                output(args, delim)

            dt_out = dt

            for fields in logmod.get_packages():
                if fields and len(fields) == 3 and fields[0] in ACTIONS:
                    queue.append((dt, *fields))

    # Flush any remaining queued output
    output(args, delim)
    if bootstr:
        print(bootstr)

if __name__ == "__main__":
    main()
