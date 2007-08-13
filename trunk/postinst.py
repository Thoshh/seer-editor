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

# Seer post installation script

"""Seer postinstallation  script"""

import sys, os

if sys.platform.startswith('win'):
    platform = 'win'
else:
    platform = 'other'

from distutils.sysconfig import get_python_lib
python_lib = get_python_lib()

seer_base = os.path.join(python_lib, 'seer')
seer_prg = os.path.join(seer_base, 'seer.pyw')
seer_docs = os.path.join(seer_base, 'documentation')
seer_help = os.path.join(seer_docs, 'help.html')

def install():
    """Routine to be run with the -install switch."""

    try:
        import wx
        wx = True
    except ImportError:
        print 'Seer needs wxPython (http://www.wxpython.org)'
        wx = False

    if platform == 'win': # Windows specific part of installation

        if wx:
            # here, you could add a wx dialog asking the user:
            # - shall desktop shortcuts be created?
            # - shall start menu shortcuts be created?
            # - user or system wide installation?
            #   (i.e use personal desktop or common desktop, etc.)
            # - take over old user profile? (in case of update, default yes)
            # - associate .py/.pyw extension with Seer automatically?
            # - start Seer automatically after installation?
            # - show release information after installation?
            # - some fundamental preferences to be preconfigured?
            #   (default language, like tabs or no tabs etc.)
            pass # not yet implemented

        # for the time being, we only add desktop shortcuts (if they do not already exist)

        def create_shortcut_safe(target, description, filename, *args, **kw):
            """Create and register a shortcut only if it doesn't already exist."""
            if not os.path.isfile(filename):
                create_shortcut(target, description, filename, *args, **kw)
                file_created(filename)

        desktop = get_special_folder_path('CSIDL_DESKTOPDIRECTORY')

        create_shortcut_safe(seer_prg,
            'Seer Editor/Environment', desktop + '\\Seer.lnk')
        create_shortcut_safe(seer_help,
            'Seer Help', desktop + '\\Seer Help.lnk')

def remove():
    """Routine to be run with the -remove switch."""
    pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-install':
            install()
        elif sys.argv[1] == '-remove':
            remove()
