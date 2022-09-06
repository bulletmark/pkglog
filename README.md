## PKGLOG - Linux utility to output list of changed packages
[![PyPi](https://img.shields.io/pypi/v/pkglog)](https://pypi.org/project/pkglog/)
[![AUR](https://img.shields.io/aur/version/pkglog)](https://aur.archlinux.org/packages/pkglog/)

This is a Linux command line utility to output a list of packages
installed, removed, upgraded, or downgraded. It should be able to parse
the package log formats used by the common Linux distributions. Example
output is shown below (although it is displayed with colored lines
in most terminals, just not here in the text README).

```
$ pkglog
---------------------------------------------------------------------------------
2021-01-15 10:52:18 alsa-card-profiles   14.1-1 -> 14.1-2
2021-01-15 10:52:18 libpulse             14.1-1 -> 14.1-2
2021-01-15 10:52:18 pulseaudio           14.1-1 -> 14.1-2
2021-01-15 10:52:18 mutter               3.38.2+7+gfbb9a34f2-1 -> 3.38.3-1
2021-01-15 10:52:18 pulseaudio-bluetooth 14.1-1 -> 14.1-2
2021-01-15 10:52:18 gnome-shell          1:3.38.2+22+g3a343a8aa-1 -> 1:3.38.3-1
--------------------------------------------------------------------------------
2021-01-15 16:16:26 gridsome-cli 0.3.3-1 removed
--------------------------------------------------------------------------------
2021-01-16 07:11:33 httpie                2.3.0-3 -> 2.3.0-4
2021-01-16 07:11:33 nodejs                15.5.1-1 -> 15.6.0-1
2021-01-16 07:11:33 glib2                 2.66.4-1 -> 2.66.4-2
2021-01-16 07:11:33 glib2-docs            2.66.4-1 -> 2.66.4-2
2021-01-16 07:11:33 gtk-update-icon-cache 1:4.0.1-1 -> 1:4.0.1-2
2021-01-16 07:11:33 qt5-base              5.15.2-2 -> 5.15.2-3
2021-01-16 07:11:33 kdiagram              2.7.0-1 -> 2.8.0-1
---------------------------------------------------------------------------------
2021-01-17 07:13:15 nano         5.4-1 -> 5.5-1
2021-01-17 07:13:15 mesa         20.3.2-2 -> 20.3.3-1
2021-01-17 07:13:15 rav1e        0.3.5-1 -> 0.4.0-1
2021-01-17 07:13:15 tk           8.6.11-1 -> 8.6.11.1-1
2021-01-17 07:13:15 vulkan-intel 20.3.2-2 -> 20.3.3-1
---------------------------------------------------------------------------------
2021-01-18 06:51:45 perl-datetime-timezone      2.35-2 -> 2.44-1
2021-01-18 06:51:46 python-h11                  0.11.0-1 -> 0.12.0-1
2021-01-18 06:51:46 python-pkginfo              1.6.1-3 -> 1.7.0-1
2021-01-18 06:51:46 alsa-card-profiles          14.1-2 -> 14.2-1
2021-01-18 06:51:46 imagemagick                 7.0.10.57-1 -> 7.0.10.58-1
2021-01-18 06:51:46 libbytesize                 2.4-3 -> 2.4-4
2021-01-18 06:51:46 libblockdev                 2.24-3 -> 2.25-1
2021-01-18 06:51:46 libibus                     1.5.23+3+gaa558de8-2 -> 1.5.23+3+gaa558de8-3
2021-01-18 06:51:46 libmm-glib                  1.14.8-1 -> 1.14.10-1
2021-01-18 06:51:46 libpulse                    14.1-2 -> 14.2-1
2021-01-18 06:51:46 modemmanager                1.14.8-1 -> 1.14.10-1
2021-01-18 06:51:46 pulseaudio                  14.1-2 -> 14.2-1
2021-01-18 06:51:46 pulseaudio-bluetooth        14.1-2 -> 14.2-1
2021-01-18 06:51:46 python-urllib3              1.26.1-1 -> 1.26.2-1
---------------------------------------------------------------------------------
2021-01-18 07:21:10 ### LAST SYSTEM BOOT ###
---------------------------------------------------------------------------------
2021-01-18 07:57:48 tree 1.8.0-2 installed
```

1. By default, only package updates over the last 30 days are shown. You
   can choose to specify a specific date, or number of days back, or for
   all time.

2. Updates are grouped together by time (all updates with less than a 2
   minute gap between any of them) so you can distinguish the group of
   packages updated each time you did a system update.

3. The `LAST SYSTEM BOOT` line shows you which packages have been
   updated since the last boot, e.g. if the linux kernel package was
   since updated you may decide to reboot asap. In the above example,
   only the `tree` package has been installed since the last boot.

4. You can specify a package name and only updates to that package are
   shown. See the USAGE section below.

5. Most terminals show this output in color. Five different colors are
   used to identify the package actions as shown below.
   You can choose to disable colored output.

6. You can use the `-n/--installed-net` option to see a list of all
   packages currently installed and their date of installation. E.g. use
   this option after you have installed and removed a heap of trial
   packages and you want to easily see if you have actually removed all
   of them.

See the latest documentation and code at https://github.com/bulletmark/pkglog.

## COLORED OUTPUT LINES

|Package Action|Color
|--------------|-----
|Installed     |green
|Removed       |red
|Upgraded      |yellow
|Downgraded    |magenta
|Reinstalled   |cyan

You can use a command line option to disable colored output, or set it
as a default option.

## LOG FILE FORMATS

Parsers for the following log formats currently exist. The appropriate
parser for you system is normally automatically determined.
Alternatively, you can choose the log directory[s], file[s], and/or
parser explicitly using the `-p/--parser` option. A very simple parser
plugin architecture is used, so creating a new parser is easy. Simply
drop the parser file in the `parsers/` directory and the program will
automatically use it. See the [current parsers](pkglog/parsers) for
example code.

|Log Parser|Default Path           |Systems            |
|----------|-----------------------|-------------------|
|apt       |`/var/log/apt/history*`|Debian, Ubuntu, etc|
|dnf       |`/var/log/dnf.rpm.log` |RedHat, Fedora, etc|
|pacman    |`/var/log/pacman.log`  |Arch, Manjaro, etc |

## USAGE

Type `pkglog -h` to view the following usage summary:

```
usage: pkglog [-h] [-u] [-i] [-I] [-n] [-d DAYS] [-a] [-j] [-v] [-c]
                 [-p {pacman,apt,dnf}] [-t TIMEGAP] [-P PATH] [-g | -r]
                 [package]

Reports log of package updates.

positional arguments:
  package               specific package name to report

options:
  -h, --help            show this help message and exit
  -u, --updated-only    show updated only
  -i, --installed       show installed/removed only
  -I, --installed-only  show installed only
  -n, --installed-net   show net installed only
  -d DAYS, --days DAYS  show all packages only from given days ago (or YYYY-
                        MM-DD), default=30, -1=all
  -a, --alldays         show all packages for all days (same as "-days=-1")
  -j, --nojustify       don't right justify version numbers
  -v, --verbose         be verbose, describe upgrades/downgrades
  -c, --no-color        do not color output lines
  -p {pacman,apt,dnf}, --parser {pacman,apt,dnf}
                        log parser type, default=pacman
  -t TIMEGAP, --timegap TIMEGAP
                        max minutes gap between grouped updates, default=2
  -P PATH, --path PATH  alternate log path[s] (separate multiple using ":",
                        must be time sequenced)
  -g, --glob            given package name is glob pattern to match
  -r, --regex           given package name is regular expression to match

Note you can set default starting arguments in ~/.config/pkglog-flags.conf.
```

## DEFAULT ARGUMENTS

You can add default arguments to a personal configuration file
`~/.config/pkglog-flags.conf`. If that file exists then each line of
arguments in the file will be concatenated and automatically prepended
to your `pkglog` command line arguments.

This allow you to set default preferred starting arguments to `pkglog`.
Type `pkglog -h` to see the arguments supported.
E.g. `echo "--days 7" >~/.config/pkglog-flags.conf` to make `pkglog`
only display the last 7 days of updates by default. This is also useful
to set your parser explicitly using `-p/--parser` (e.g. if the default
parser is not automatically determined correctly on your system).

## INSTALLATION

Arch Linux users can install [pkglog from the
AUR](https://aur.archlinux.org/packages/pkglog). Python 3.7 or later is
required. The [`python-rich`](https://pypi.org/project/rich/) package is
required if you want colored output (which is the default unless you
specify the `-c/--no-color` option).

Note [pkglog is on PyPI](https://pypi.org/project/pkglog/) so just
ensure that `python3-pip` and `python3-wheel` are installed then type
the following to install (or upgrade):

```
$ sudo pip3 install -U pkglog
```

Alternatively, do the following to install from the source repository.

```sh
$ git clone http://github.com/bulletmark/pkglog
$ cd pkglog
$ sudo pip3 install -U .
```

## UPGRADE

```sh
$ cd pkglog  # Source dir, as above
$ git pull
$ sudo pip3 install -U .
```

## REMOVAL

```sh
$ sudo pip3 uninstall pkglog
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
