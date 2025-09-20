#!/usr/bin/python3
"Reports concise log of package changes."

# Author: Mark Blakeney, 2016->2021.
from __future__ import annotations

import fileinput
import fnmatch
import os
import re
import shlex
import sys
from argparse import ArgumentParser, Namespace
from datetime import date, datetime, time, timedelta
from importlib import util
from pathlib import Path

TIMEGAP = 2  # mins
PATHSEP = ':'

DAYS = 30
NETDAYS = 2

# Define ANSI escape sequences for colors ..
# Refer https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
COLOR_red = '\033[31m'
COLOR_green = '\033[32m'
COLOR_yellow = '\033[33m'
COLOR_blue = '\033[34m'
COLOR_magenta = '\033[35m'
COLOR_cyan = '\033[36m'
COLOR_white = '\033[37m'
COLOR_reset = '\033[39m'

ACTIONS = {
    'installed': (1, COLOR_green),
    'removed': (2, COLOR_red),
    'upgraded': (3, COLOR_yellow),
    'downgraded': (3, COLOR_magenta),
    'reinstalled': (4, COLOR_cyan),
}

MODDIR = Path(__file__).parent.resolve()
CNFFILE = Path(os.getenv('XDG_CONFIG_HOME', '~/.config'), f'{MODDIR.name}-flags.conf')


class Queue:
    queue = []  # type: ignore
    installed = {}  # type: ignore
    installed_previously = {}  # type: ignore
    installed_net_days: timedelta
    no_color: bool
    boottime: datetime
    bootstr: str = ''
    delim: str = ''

    @classmethod
    def print(cls, color: str | None, *msg: str) -> None:
        "Output given message"
        for m in msg:
            if m:
                if cls.no_color:
                    print(m)
                else:
                    if color:
                        m = color + m

                    print(m + COLOR_reset)

    @classmethod
    def output(cls, args: Namespace) -> None:
        "Output queued set of package transactions to screen"
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
                for arg_pkg in args.package:
                    if args.regex:
                        if arg_pkg.search(pkg):
                            break
                    elif pkg == arg_pkg:
                        break
                else:
                    continue

            if args.installed_net:
                pkgdt = cls.installed.get(pkg)
                if not pkgdt or dt < pkgdt:
                    continue
                pkgdt_rm = cls.installed_previously.get(pkg)
                if pkgdt_rm and (pkgdt - pkgdt_rm) < cls.installed_net_days:
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
                cls.bootstr = ''
            elif num == 0:
                cls.print(None, cls.delim)

            cls.print(color, f'{dt} {pkg:{maxlen}} {vers}')

        cls.queue.clear()

    @classmethod
    def append(cls, dt: datetime, action: str, pkg: str, vers: str) -> None:
        "Append this package + action to the internal queue"
        actcode, _ = ACTIONS[action]
        if actcode == 1:
            cls.installed[pkg] = dt
        elif actcode == 2:
            cls.installed.pop(pkg, None)
            cls.installed_previously[pkg] = dt

        cls.queue.append((dt, action, pkg, vers))


def import_path(path: Path):
    "Import given module path"
    modname = path.stem.replace('-', '_')
    spec = util.spec_from_file_location(modname, path)
    module = util.module_from_spec(spec)  # type: ignore
    sys.modules[modname] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


class Module:
    "Class to wrap parser module files"

    def __init__(self, path: Path) -> None:
        self.module = import_path(path)
        if not hasattr(self.module, 'logfile'):
            sys.exit(f'Must define logfile attribute for {path}')

        self.logfile = Path(self.module.logfile)


def compute_start_time(args: Namespace) -> datetime | None:
    "Compute start time from when to output log"
    start_time = None
    days = -1
    if not args.alldays:
        if timestr := args.days:
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


def main() -> None:
    def_module = ''
    modules = {}

    # Load all parser modules
    for m in (MODDIR / 'parsers').glob('[!_]*.py'):
        modules[m.stem] = mod = Module(m)
        if not def_module and mod.logfile.exists():
            def_module = m.stem

    # Process command line options
    opt = ArgumentParser(
        description=__doc__,
        epilog=f'Note you can set default starting options in {CNFFILE}.',
    )
    grp = opt.add_mutually_exclusive_group()
    grp.add_argument(
        '-u', '--updated-only', action='store_true', help='show updated only'
    )
    grp.add_argument(
        '-i', '--installed', action='store_true', help='show installed/removed only'
    )
    grp.add_argument(
        '-I', '--installed-only', action='store_true', help='show installed only'
    )
    grp.add_argument(
        '-n', '--installed-net', action='store_true', help='show net installed only'
    )
    opt.add_argument(
        '-N',
        '--installed-net-days',
        type=float,
        default=NETDAYS,
        help='days previously removed before being re-considered as '
        f'new net installed, default={NETDAYS}. Set to 0 to disable.',
    )
    grp = opt.add_mutually_exclusive_group()
    grp.add_argument(
        '-d',
        '--days',
        help='show all packages only from given number of days ago, '
        f'or from given YYYY-MM-DD[?HH:MM[:SS]], default={DAYS}(days), '
        '0=today, -1=all. If only time is specified, then today is '
        'assumed.',
    )
    grp.add_argument(
        '-a',
        '--alldays',
        action='store_true',
        help='show all packages for all days (same as "--days=-1")',
    )
    grp.add_argument(
        '-b',
        '--boot',
        action='store_true',
        help='show only packages updated since last boot',
    )
    opt.add_argument(
        '-j',
        '--nojustify',
        action='store_true',
        help="don't right justify version numbers",
    )
    opt.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='be verbose, describe upgrades/downgrades',
    )
    opt.add_argument(
        '-c', '--no-color', action='store_true', help='do not color output lines'
    )
    grp1 = opt.add_mutually_exclusive_group()
    grp1.add_argument(
        '-p',
        '--parser',
        choices=modules,
        help=f'log parser type, default={def_module or "?"}',
    )
    grp1.add_argument(
        '-f', '--parser-plugin', help='path to alternate custom parser plugin file'
    )
    opt.add_argument(
        '-t',
        '--timegap',
        type=float,
        default=TIMEGAP,
        help=f'max minutes gap between grouped changes, default={TIMEGAP}',
    )
    opt.add_argument(
        '-P',
        '--path',
        help='alternate log path[s] '
        f'(separate multiple using "{PATHSEP}", must be time sequenced)',
    )
    grp2 = opt.add_mutually_exclusive_group()
    grp2.add_argument(
        '-g',
        '--glob',
        action='store_true',
        help='given package name[s] is glob pattern to match',
    )
    grp2.add_argument(
        '-r',
        '--regex',
        action='store_true',
        help='given package name[s] is regular expression to match',
    )
    grp.add_argument(
        '-l',
        '--list-parsers',
        action='store_true',
        help='just list available parsers and their descriptions',
    )
    opt.add_argument(
        '-V', '--version', action='store_true', help=f'just show {opt.prog} version'
    )
    opt.add_argument('package', nargs='*', help='specific package name[s] to report')

    # Merge in default options from user config file. Then parse the
    # command line.
    cnffile = CNFFILE.expanduser()
    if cnffile.exists():
        with cnffile.open() as fp:
            cnflinesl = [re.sub(r'#.*$', '', line).strip() for line in fp]
        cnflines = ' '.join(cnflinesl).strip()
    else:
        cnflines = ''

    args = opt.parse_args(shlex.split(cnflines) + sys.argv[1:])

    if args.version:
        from importlib.metadata import version

        try:
            ver = version(opt.prog)
        except Exception:
            ver = 'unknown'

        print(ver)
        return

    if args.list_parsers:
        for name in sorted(modules):
            mod = modules[name]
            desc = mod.module.__doc__ or 'No description available.'
            print(f'{name}\t: {desc}')
        return

    Queue.no_color = args.no_color or not sys.stdout.isatty()

    if args.parser_plugin:
        # Get alternate custom parser file
        path = Path(args.parser_plugin)
        if path.suffix.lower() != '.py':
            sys.exit(f'ERROR: "{path}" must end in .py')
        if not path.exists() or path.is_dir():
            sys.exit(f'ERROR: "{path}" must be an existing python file')

        module: Module | None = Module(path)
    else:
        # Get parser specified on command line or default parser
        module = modules.get(args.parser or def_module)

    if not module:
        sys.exit('ERROR: Can not determine log parser for this system.')

    if args.package:
        pkgs = []
        for pkg in args.package:
            # Convert glob pattern to regex
            if args.glob:
                pkg = fnmatch.translate(pkg)
                args.regex = True

            # Store compiled regex for package name
            if args.regex:
                pkg = re.compile(pkg)

            pkgs.append(pkg)

        args.package = pkgs

    if args.installed_net:
        args.installed = True
        Queue.installed_net_days = timedelta(days=args.installed_net_days)

    if not args.package and not (args.installed or args.installed_only):
        Queue.delim = 80 * '-'

    timegap = timedelta(minutes=args.timegap)
    dt_out = datetime.max
    start_time = compute_start_time(args) or datetime.min

    # Get last boot time
    upsecs = float(Path('/proc/uptime').read_text().split()[0])
    Queue.boottime = datetime.now() - timedelta(seconds=upsecs)

    if not args.package and not args.boot:
        timestr = Queue.boottime.isoformat(' ', 'seconds')
        Queue.bootstr = f'{timestr} ### LAST SYSTEM BOOT ###'

    # Instantiate the log parser
    log_parser = module.module.Parser()

    defpath = module.logfile

    if args.path:
        pathlist = [Path(p) for p in args.path.split(PATHSEP)]
    else:
        pathlist = [defpath.parent]

    # Loop over all lines in input files
    for path in pathlist:
        if path.is_dir():
            filelist = list(path.glob(f'{defpath.name}.*'))
            filelist.sort(
                key=lambda x: int(re.sub(r'\D+', '', str(x)) or 0), reverse=True
            )
            filelist.append(path / defpath.name)
        else:
            filelist = [path]

        if not filelist[-1].exists():
            sys.exit(f'ERROR: {filelist[-1]} does not exist.')

        for lineb in fileinput.input(
            filelist, openhook=fileinput.hook_compressed, encoding='unicode_escape'
        ):
            line = lineb if isinstance(lineb, str) else lineb.decode()
            if not (line := line.strip()):
                continue

            if not (dt := log_parser.get_time(line)):
                continue

            if dt < start_time or args.boot and dt < Queue.boottime:
                continue

            if dt - dt_out > timegap and not args.installed_net:
                Queue.output(args)

            dt_out = dt

            for fields in log_parser.get_packages():
                if fields and len(fields) == 3 and fields[0] in ACTIONS:
                    Queue.append(dt, *fields)

    # Flush any remaining queued output
    Queue.output(args)
    if Queue.bootstr:
        Queue.print(None, Queue.delim, Queue.bootstr)


if __name__ == '__main__':
    main()
