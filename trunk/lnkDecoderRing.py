#!/usr/bin/env python

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

import string, re

refile = re.compile('(\\\\|[A-Z]\:)(.+)', re.M)
reinvalid = re.compile('(\")|(\t)|(\n)|(\r)', re.M)

def IsFolder(text):
    return ord(text[0x18]) & 0x10

def IsNetwork(text):
    return (ord(text[0x18]) == 0x00) and (ord(text[0x14]) == 1)

def GetPrintableStrings(text):
    strings = []

    cs = ''

    for character in text:
        if character in string.printable:
            cs += character
        else:
            if cs:
                if (refile.search(cs) is not None) and (reinvalid.search(cs) is None):
                    if cs[0] != '/':
                        strings.append(cs)
            cs = ''

    return strings

def ReadLink(filename):
    f = file(filename, 'rb')
    text = f.read()
    f.close()

    return GetPrintableStrings(text)[0].replace('\\', '/')