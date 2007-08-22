#!/usr/bin/env python

# Initial code framework based from DrPython, Copyright 2003-2007 Daniel Pozmanter

#    Distributed under the terms of the GPL (GNU Public License)
#
#    Seer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# Seer installation script
# Copyright (c) 2004 Radoslaw Stachowiak <radek@gentoo.org>
# Last modification: 2004-10-12
#

"""\
Seer - a highly customizable cross-platform Text Editor

Seer is a highly customizable, cross-platform, extensible editor and
environment for developing programs written in multiple programming
languages. It is implemented in wxPython (a set of Python bindings and
extra widgets for wxWidgets) and uses its Scintilla based editor component.

You can get the latest Python version from http://www.python.org.

You can get the latest wxPython version from http://www.wxpython.org."""

# version (should be imported from drpython.py or __init__.py)
MY_VER='0.1'

# package name, do not change
MY_NAME = 'seer'

AUTHOR = 'David Torres'
AUTHOR_EMAIL = 'verbena1@gmail.com'
URL = 'http://code.google.com/p/seer-editor/'

# Trove classification (get list with python setup.py register --list-classifiers)
classifiers = """
Development Status :: 5 - Production/Stable
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications :: GTK
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Information Technology
Intended Audience :: Other Audience
Intended Audience :: Science/Research
Intended Audience :: System Administrators
OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Documentation
Topic :: Software Development
Topic :: Text Editors
Topic :: Text Editors :: Integrated Development Environments (IDE)
"""

# take name and description from setup.py docstring
description = __doc__.split('\n\n', 1)
name=description[0].split(' ', 1)[0]

# please add every package data file to be installed to the list
DATA = [
    'documentation/*',
    'bitmaps/*.ico', 'bitmaps/*.png',
    'bitmaps/16/*.png', 'bitmaps/24/*.png',
    # adding runner scripts, TODO: seer startup should be probably redone
    'seer.pyw', 'seer.lin'
]

from distutils.core import setup

# and now standard distutils installation routine
setup(name=name,
    version=MY_VER,
    description=description[0],
    long_description=description[1],
    classifiers = filter(None, classifiers.split('\n')),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    platforms = "any",
    license = 'GPL',
    packages=[ MY_NAME ],
    package_dir={ MY_NAME : '.' },
    package_data={ MY_NAME : DATA },
    scripts=['postinst.py'],
)
