#Tab Nanny Check: returns a string on checking.

from tabnanny import *

#Copied from tabnanny by Tim Peters, then hacked to work the way I want.

import os
import tokenize

__all__ = ["check", "NannyNag", "process_tokens"]

verbose = 0
filename_only = 0

def errprint(*args):
    printstr(args)

def printstr(*args):
    result = ''
    sep = ''
    for arg in args:
        result += sep + str(arg)
        sep = ' '
    return result + '\n'

def Check(file):
    """check(file_or_dir)

    If file_or_dir is a directory and not a symbolic link, then recursively
    descend the directory tree named by file_or_dir, checking all .py files
    along the way. If file_or_dir is an ordinary Python source file, it is
    checked for whitespace related problems. The diagnostic messages are
    written to standard output using the print statement.
    """

    result = ''

    if os.path.isdir(file) and not os.path.islink(file):
        if verbose:
            result += printstr("%s: listing directory" % `file`)
        names = os.listdir(file)
        for name in names:
            fullname = os.path.join(file, name)
            if os.path.isdir(fullname) and not os.path.islink(fullname) or os.path.normcase(name[-3:]) == ".py":
                check(fullname)
        return result

    try:
        f = open(file)
    except IOError, msg:
        result += errprint("%s: I/O Error: %s" % (`file`, str(msg)))
        return result

    if verbose > 1:
        result += printstr("checking", `file`, "...")

    try:
        process_tokens(tokenize.generate_tokens(f.readline))

    except tokenize.TokenError, msg:
        result += errprint("%s: Token Error: %s" % (`file`, str(msg)))
        return result

    except NannyNag, nag:
        badline = nag.get_lineno()
        line = nag.get_line()
        if verbose:
            result += printstr("%s: *** Line %d: trouble in tab city! ***" % (`file`, badline))
            result += printstr("offending line:", `line`)
            result += printstr(nag.get_msg())
        else:
            if ' ' in file: file = '"' + file + '"'
            if filename_only: result += printstr(file)
            else: result += printstr(file, badline, `line`)
        return result

    if verbose:
        result += printstr("%s: Clean bill of health." % `file`)

    return result