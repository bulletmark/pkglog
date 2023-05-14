## PKGLOG - Linux utility to output concise log of package changes
[![PyPi](https://img.shields.io/pypi/v/pkglog)](https://pypi.org/project/pkglog/)
[![AUR](https://img.shields.io/aur/version/pkglog)](https://aur.archlinux.org/packages/pkglog/)

This is a Linux command line utility to output a concise list of
packages installed, removed, upgraded, downgraded, or reinstalled. It
should be able to parse package log formats used by the common Linux
distributions. Example output is shown below.

![screenshot](https://user-images.githubusercontent.com/217011/195960110-02a43a1c-366a-4e61-9372-10c4f1f4c55f.png)

1. Most terminals show this output in color, as seen above. Five
   different colors are used to identify the package actions as shown
   in the table below. You can choose to disable colored output.

2. Changes are grouped together by time so you can distinguish the group
   of packages changed each time you did package
   updates/installs/removal. By default, all changes with less than a
   succeeding 2 minute gap between any of them are grouped together, but
   you can change that time value.

3. By default, only package changes over the last 30 days are shown. You
   can choose to specify the number of days back, or from a specific
   date (optionally plus a time, or specify just a time and today is
   assumed), since last boot, or for all time.

4. The `LAST SYSTEM BOOT` line shows you which packages have been
   changed since the last boot, e.g. if the linux kernel package has
   updated you may decide to reboot asap.

5. You can specify a package name and only changes to that package are
   shown. See the USAGE section below.

6. You can use the `-n/--installed-net` option to see a list of all
   packages currently installed and their date of installation. E.g. use
   this option after you have installed and removed a heap of trial
   packages and you want to easily see if you have actually removed all
   of them and their dependencies. E.g. `pkglog -n -d0` shows a net
   summary of packages you ended up installing today.

See the latest documentation and code at https://github.com/bulletmark/pkglog.

## COLORED OUTPUT LINES

|Package Action|Line Text Color
|--------------|-----
|Installed     |green
|Removed       |red
|Upgraded      |yellow
|Downgraded    |magenta
|Reinstalled   |cyan

You can use a command line option to disable colors explicitly, or set
that option disabled as a [default option](#default-options).

## LOG FILE FORMATS

Parsers for the following log formats currently exist. The appropriate
parser for you system is normally automatically determined.
Alternatively, you can choose the log file path[s], and/or parser
explicitly. You can also set these as [default
options](#default-options).

A very simple parser plugin architecture is used, so creating a new
parser is easy. Use the `-f/--parser-file` option to explicitly specify
the path to your custom parser for development. By default, parsers are
loaded from the `parsers/` sub-directory so, if cloning, forking, or
submitting a PR for the software, then simply place your custom parser
file in that directory and the program will automatically recognise it.
See the [current parsers](pkglog/parsers) for example code.

|Log Parser|Default Path           |Distribution       |
|----------|-----------------------|-------------------|
|apt       |`/var/log/apt/history*`|Debian, Ubuntu, etc|
|dnf       |`/var/log/dnf.rpm.log` |RedHat, Fedora, etc|
|pacman    |`/var/log/pacman.log`  |Arch, Manjaro, etc |
|zypper    |`/var/log/zypp/history`|OpenSUSE           |

## USAGE

Type `pkglog -h` to view the usage summary:

```
usage: pkglog [-h] [-u | -i | -I | -n] [-d DAYS | -a | -b] [-j] [-v] [-c]
                   [-p {pacman,zypper,apt,dnf} | -f PARSER_PLUGIN]
                   [-t TIMEGAP] [-P PATH] [-g | -r]
                   [package]

Reports concise log of package changes.

positional arguments:
  package               specific package name to report

options:
  -h, --help            show this help message and exit
  -u, --updated-only    show updated only
  -i, --installed       show installed/removed only
  -I, --installed-only  show installed only
  -n, --installed-net   show net installed only
  -d DAYS, --days DAYS  show all packages only from given number of days ago,
                        or from given YYYY-MM-DD[?HH:MM[:SS]],
                        default=30(days), 0=today, -1=all. If only time is
                        specified, then today is assumed.
  -a, --alldays         show all packages for all days (same as "--days=-1")
  -b, --boot            show only packages updated since last boot
  -j, --nojustify       don't right justify version numbers
  -v, --verbose         be verbose, describe upgrades/downgrades
  -c, --no-color        do not color output lines
  -p {pacman,zypper,apt,dnf}, --parser {pacman,zypper,apt,dnf}
                        log parser type, default=pacman
  -f PARSER_PLUGIN, --parser-plugin PARSER_PLUGIN
                        path to alternate custom parser plugin file
  -t TIMEGAP, --timegap TIMEGAP
                        max minutes gap between grouped changes, default=2
  -P PATH, --path PATH  alternate log path[s] (separate multiple using ":",
                        must be time sequenced)
  -g, --glob            given package name is glob pattern to match
  -r, --regex           given package name is regular expression to match

Note you can set default starting options in ~/.config/pkglog-flags.conf.
```

## DEFAULT OPTIONS

You can add default options to a personal configuration file
`~/.config/pkglog-flags.conf`. If that file exists then each line of
options in the file will be concatenated and automatically prepended
to your `pkglog` command line options.

This allow you to set default preferred starting options to `pkglog`.
Type `pkglog -h` to see the options supported.
E.g. `echo "--days 7" >~/.config/pkglog-flags.conf` to make `pkglog`
only display the last 7 days of changes by default. This is also useful
to set your parser explicitly using `-p/--parser` (e.g. if the default
parser is not automatically determined correctly on your system).

## INSTALLATION

Arch Linux users can install [pkglog from the
AUR](https://aur.archlinux.org/packages/pkglog).

Python 3.7 or later is required. Python package
[`looseversion`](https://pypi.org/project/looseversion/) is also
required if you want to parse zypper logs.

Note [pkglog is on PyPI](https://pypi.org/project/pkglog/) so just
ensure that `python3-pip` and `python3-wheel` are installed then type
the following to install (or upgrade):

```
$ sudo pip3 install -U --use-pep517 --root-user-action=ignore pkglog
```

Alternatively, do the following to install from the source repository.

```sh
$ git clone http://github.com/bulletmark/pkglog
$ cd pkglog
$ sudo pip3 install -U --use-pep517 --root-user-action=ignore .
```

## UPGRADE

```sh
$ cd pkglog  # Source dir, as above
$ git pull
$ sudo pip3 install -U --use-pep517 --root-user-action=ignore .
```

## REMOVAL

```sh
$ sudo pip3 uninstall --root-user-action=ignore pkglog
```

## LICENSE

Copyright (C) 2020 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.
