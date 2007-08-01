#!/usr/bin/env python

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