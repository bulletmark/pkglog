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

5. You can specify one or more package names and only changes to those
   packages are shown. You can specify glob or regular expression
   patterns for the names. See the USAGE section below.

6. You can use the `-n/--installed-net` option to see a list of all
   packages currently installed and their date of installation. E.g. use
   this option after you have installed and removed a heap of trial
   packages and you want to easily see if you have actually removed all
   of them and their dependencies. E.g. `pkglog -n -d0` shows a net
   summary of packages you ended up installing today. Refer to the
   [Installed Net Output Options](#installed-net-output-options) section below.

See the latest documentation and code at https://github.com/bulletmark/pkglog.

## Colored Output Lines

|Package Action|Line Text Color
|--------------|-----
|Installed     |green
|Removed       |red
|Upgraded      |yellow
|Downgraded    |magenta
|Reinstalled   |cyan

You can use a command line option to disable colors explicitly, or set
that option disabled as a [default option](#default-options).

## Log File Formats

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
|xbps      |`/var/log/socklog/xbps/current`|Void Linux |
|zypper    |`/var/log/zypp/history`|OpenSUSE           |

## Usage

Type `pkglog -h` to view the usage summary:

```
usage: pkglog [-h] [-u | -i | -I | -n] [-N INSTALLED_NET_DAYS] [-d DAYS]
                   [-a] [-b] [-j] [-v] [-c] [-p {pacman,zypper,apt,xbps,dnf} |
                   -f PARSER_PLUGIN] [-t TIMEGAP] [-P PATH] [-g | -r] [-l]
                   [-V]
                   [package ...]

Reports concise log of package changes.

positional arguments:
  package               specific package name[s] to report

options:
  -h, --help            show this help message and exit
  -u, --updated-only    show updated only
  -i, --installed       show installed/removed only
  -I, --installed-only  show installed only
  -n, --installed-net   show net installed only
  -N, --installed-net-days INSTALLED_NET_DAYS
                        days previously removed before being re-considered as
                        new net installed, default=2. Set to 0 to disable.
  -d, --days DAYS       show all packages only from given number of days ago,
                        or from given YYYY-MM-DD[?HH:MM[:SS]],
                        default=30(days), 0=today, -1=all. If only time is
                        specified, then today is assumed.
  -a, --alldays         show all packages for all days (same as "--days=-1")
  -b, --boot            show only packages updated since last boot
  -j, --nojustify       don't right justify version numbers
  -v, --verbose         be verbose, describe upgrades/downgrades
  -c, --no-color        do not color output lines
  -p, --parser {pacman,zypper,apt,xbps,dnf}
                        log parser type, default=pacman
  -f, --parser-plugin PARSER_PLUGIN
                        path to alternate custom parser plugin file
  -t, --timegap TIMEGAP
                        max minutes gap between grouped changes, default=2
  -P, --path PATH       alternate log path[s] (separate multiple using ":",
                        must be time sequenced)
  -g, --glob            given package name[s] is glob pattern to match
  -r, --regex           given package name[s] is regular expression to match
  -l, --list-parsers    just list available parsers and their descriptions
  -V, --version         just show pkglog version

Note you can set default starting options in ~/.config/pkglog-flags.conf.
```

## Installed Net Output Options

The purpose of the `-n/--installed-net` option is perhaps not
intuitively clear so this section explains it by way of an example.

There are times when experimenting etc that I install and remove a heap
of various packages, e.g. over a few hours or days. At the end of that
experiment I remove all the packages I believe I installed for my
experiment. However, I am never too sure I have removed everything, e.g.
some dependencies that were automatically installed. So I type:

```bash
$ pkglog -d4 -n
```

The above shows the "net" packages have ended up installed over the last 4
days, i.e. those that were newly installed in the last 4 days and not
yet removed. I can then manually remove any packages I see listed that I
don't want.

There are some favorite packages which I normally have always installed
but I may remove very temporarily for some reason. Since these packages
then appear "newly" installed then they may be undesirably listed in the
`-n/--installed-net` output. To avoid this the `-N/--installed-net-days`
option, by default set to 2 days, removes packages from the
`-n/--installed-net` output which were previously uninstalled only for
that specified number of days or less. You can disable this filter
option by setting it to 0, e.g. as a [default option](#default-options).

## Default Options

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

## Installation

Arch Linux users can install [pkglog from the
AUR](https://aur.archlinux.org/packages/pkglog).

Python 3.9 or later is required.
Note [pkglog is on PyPI](https://pypi.org/project/pkglog/) so just
ensure that [`uv`](https://docs.astral.sh/uv/) is installed then
type the following:

```
$ uv tool install pkglog
```

To upgrade:

```
$ uv tool upgrade pkglog
```

Note that python package
[`looseversion`](https://pypi.org/project/looseversion/) is also
required if you want to parse zypper logs:

```
$ uv tool install --with looseversion pkglog
```

## License

Copyright (C) 2020 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <https://en.wikipedia.org/wiki/GNU_General_Public_License> for more details.

<!-- vim: se ai: -->
