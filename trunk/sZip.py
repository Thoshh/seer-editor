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

#This is a module to make adding
#to / from zip files really easy.

#Targets are prefs directory,
#creating a directory structure from the plugins.

import os, zipfile, string, tempfile
from sPrefsFile import ExtractPreferenceFromText

def AddDirectoryToZipFile(directory, dirname, zip):
    dlist = os.listdir(directory)

    for item in dlist:
        absitem = os.path.join(directory, item)
        zipitem = os.path.join(dirname, item)
        if os.path.isdir(absitem):
            AddDirectoryToZipFile(absitem, zipitem, zip)
        else:
            zip.write(absitem, zipitem)

def CreateDirectories(targetdir, zippedfilename):
    zippedfilename = zippedfilename.replace('\\', '/')
    d = zippedfilename.find('/')
    while d > -1:
        dir = zippedfilename[:d]
        targetdir = targetdir + '/' + dir
        if not os.path.exists(targetdir):
            os.mkdir(targetdir)
        zippedfilename = zippedfilename[d+1:]
        d = zippedfilename.find('/')

def ExportDirectoryTo(targetdirectory, filename, ziproot = ''):
    zf = zipfile.ZipFile(filename, 'w')

    AddDirectoryToZipFile(targetdirectory, ziproot, zf)

    zf.close()

def ExportPreferencesTo(pluginsdirectory, prefdir, shortcutsdir, datdirectory, filename,
                        shortcuts = True, popupmenu = True, toolbar = True, plugins = True):
    zf = zipfile.ZipFile(filename, 'w')

    #Add Plugins
    if plugins:
        AddDirectoryToZipFile(pluginsdirectory, '', zf)

    #Add Preferences
    zf.write(prefdir + "/preferences.dat", 'preferences.dat')

    #Add Shortcuts
    if shortcuts:
        zf.write(shortcutsdir + "/shortcuts.dat", 'shortcuts.dat')
        zf.write(shortcutsdir + "/stcshortcuts.dat", 'stcshortcuts.dat')

    #Add Pop Up Menu
    if popupmenu:
        zf.write(datdirectory +  "/popupmenu.dat", 'popupmenu.dat')

    #Add ToolBar
    if toolbar:
        zf.write(datdirectory + "/toolbar.dat", 'toolbar.dat')

    zf.close()

def ImportPluginsFrom(prefdir, filename):
    UnPackIf(prefdir, filename, 'plugins')

def UnPack(targetdirectory, filename, label=''):
    zf = zipfile.ZipFile(filename, 'r')

    dir = targetdirectory + label

    if not os.path.exists(dir):
        os.mkdir(dir)

    zippedfiles = zf.namelist()

    for zippedfile in zippedfiles:
        l = len(zippedfile)
        if (zippedfile[l-1] == '/') or (zippedfile[l-1] == '\\'):
            CreateDirectories(dir, zippedfile)
        else:
            CreateDirectories(dir, zippedfile)
            data = zf.read(zippedfile)
            f = file(dir + '/' + zippedfile, 'wb')
            f.write(data)
            f.close()

    zf.close()

def UnPackIf(targetdirectory, filename, prefix, label=''):
    zf = zipfile.ZipFile(filename, 'r')

    dir = targetdirectory + label

    if not os.path.exists(dir):
        os.mkdir(dir)

    zippedfiles = zf.namelist()

    for zippedfile in zippedfiles:
        if zippedfile.find(prefix) == 0:
            l = len(zippedfile)
            if (zippedfile[l-1] == '/') or (zippedfile[l-1] == '\\'):
                CreateDirectories(dir, zippedfile)
            else:
                CreateDirectories(dir, zippedfile)
                data = zf.read(zippedfile)
                f = file(dir + '/' + zippedfile, 'wb')
                f.write(data)
                f.close()

    zf.close()

def UnPackJustPreferences(targetdirectory, filename, label=''):
    zf = zipfile.ZipFile(filename, 'r')

    dir = targetdirectory + label

    if not os.path.exists(dir):
        os.mkdir(dir)

    rawzippedfiles = zf.namelist()

    zippedfiles = []

    targets = ['preferences.dat', 'popupmenu.dat', 'shortcuts.dat', 'stcshortcuts.dat', 'toolbar.dat']

    for rz in rawzippedfiles:
        if rz in targets:
            zippedfiles.append(rz)

    for zippedfile in zippedfiles:
        l = len(zippedfile)
        if (zippedfile[l-1] == '/') or (zippedfile[l-1] == '\\'):
            CreateDirectories(dir, zippedfile)
        else:
            CreateDirectories(dir, zippedfile)
            data = zf.read(zippedfile)
            f = file(dir + '/' + zippedfile, 'wb')
            f.write(data)
            f.close()

    zf.close()
