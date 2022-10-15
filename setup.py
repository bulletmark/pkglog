#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

from pathlib import Path
from setuptools import setup

name = 'pkglog'
module = name.replace('-', '_')
here = Path(__file__).resolve().parent

setup(
    name=name,
    version='1.12',
    description='Reports log of package updates',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/bulletmark/{name}',
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='pacman apt-get apt dnf',
    license='GPLv3',
    packages=[module] + [str(d) for d in Path(module).iterdir() if d.is_dir()
        and not d.name.startswith('_') and not d.name.startswith('.')],
    python_requires='>=3.7',
    install_requires=['rich'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        (f'share/{name}', ['README.md']),
    ],
    entry_points={
        'console_scripts': [f'{name}={module}:{module}.main'],
    },
)
