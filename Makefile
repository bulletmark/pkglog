# Copyright (C) 2016 Mark Blakeney. This program is distributed under
# the terms of the GNU General Public License.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License at <http://www.gnu.org/licenses/> for more
# details.

NAME = $(shell basename $(CURDIR))

DOC = README.md

all:
	@echo "Type sudo make install|uninstall"
	@echo "or make sdist|upload|doc|check|clean"

install:
	pip3 install -U --root-user-action=ignore .

uninstall:
	pip3 uninstall --root-user-action=ignore $(NAME)

sdist:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload: sdist
	twine3 upload --skip-existing dist/*

check:
	flake8 $(NAME)/*.py $(NAME)/*/*.py setup.py
	vermin -i --no-tips $(NAME)/*.py $(NAME)/*/*.py setup.py
	python3 setup.py check

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
