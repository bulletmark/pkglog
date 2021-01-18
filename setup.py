#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

from pathlib import Path
from setuptools import setup

name = 'pkglog'
here = Path(__file__).resolve().parent

setup(
    name=name,
    version='1.1',
    description='Reports log of package updates',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/bulletmark/{}'.format(name),
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='pacman apt',
    license='GPLv3',
    packages=[name] + [str(d) for d in Path(name).iterdir() if d.is_dir()
        and not d.name.startswith('_') and not d.name.startswith('.')],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        ('share/{}'.format(name), ['README.md']),
    ],
    # Don't use console scripts until woeful startup issue is addressed.
    # See https://github.com/pypa/setuptools/issues/510.
    # entry_points = {
    #     'console_scripts': ['{}={}:main'.format(name, name)],
    # }
    scripts=['scripts/{}'.format(name)]
)
