#!/usr/bin/env python
#This is a module to make adding
#to / from zip files really easy.

#Targets are prefs directory,
#creating a directory structure from the sscript menu
#an all plugins.

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

def AddsScriptsToZipFile(prefdir, zip):
    scriptfile = prefdir + "/sscript.dat"

    if os.path.exists(scriptfile):
        newlines = []

        dirstrings = ['sscripts']
        lastCount = 0
        #Read from the file
        f = open(scriptfile, 'rb')
        #Initialize
        line = f.readline()
        while line:
            c = line.count('\t')
            indentationstring = line[:c]
            line = line[c:].rstrip()
            while lastCount > c:
                dirstrings.pop()
                lastCount = lastCount - 1

            if line[0] == '>':
                dirstrings.append(line[1:])
                newlines.append(indentationstring + line)
                c = c + 1
            else:
                line_path = ExtractPreferenceFromText(line, "path")
                line_title = ExtractPreferenceFromText(line, "title")

                line_filename = os.path.basename(line_path)

                if os.path.exists(line_path):
                    zippath = string.join(dirstrings, '/')
                    zipname = os.path.join(zippath, line_filename)
                    zip.write(line_path, zipname)
                    newlines.append(indentationstring + '<path>' + zipname + '</path><title>' + line_title + '</title>')

            lastCount = c
            line = f.readline()
        f.close()


        #Add the edited Script File:
        newtext = string.join(newlines, '\n')

        tsscript = tempfile.mktemp()

        f = file(tsscript, 'wb')
        f.write(newtext)
        f.close()

        zip.write(tsscript, 'sscript.dat')

        #Remove the temporary file:
        os.remove(tsscript)

        #Add Shortcuts
        zip.write(prefdir + "/sscript.shortcuts.dat", 'sscript.shortcuts.dat')


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

def ExportsScriptsTo(prefdir, filename):
    zf = zipfile.ZipFile(filename, 'w')

    AddsScriptsToZipFile(prefdir, zf)

    zf.close()

def ExportPreferencesTo(pluginsdirectory, prefdir, shortcutsdir, datdirectory, filename,
                        shortcuts = True, popupmenu = True, toolbar = True, plugins = True, sscripts = True):
    zf = zipfile.ZipFile(filename, 'w')

    #Add Plugins
    if plugins:
        AddDirectoryToZipFile(pluginsdirectory, '', zf)

    if sscripts:
        AddsScriptsToZipFile(prefdir, zf)

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



def ImportsScriptsFrom(prefdir, filename):
    UnPackIf(prefdir, filename, 'sscript')
    SetupImportedsScripts(prefdir)

def ImportPluginsFrom(prefdir, filename):
    UnPackIf(prefdir, filename, 'plugins')

def ImportPreferencesFrom(prefdir, filename):
    UnPack(prefdir, filename)
    SetupImportedsScripts(prefdir)

def ImportJustPreferencesFrom(prefdir, filename):
    UnPackJustPreferences(prefdir, filename)
    SetupImportedsScripts(prefdir)

def SetupImportedsScripts(prefdir):
    scriptfile = prefdir + "/sscript.dat"

    if os.path.exists(scriptfile):

        #Read from the file
        f = open(scriptfile, 'rb')
        lines = f.readlines()
        f.close()

        newlines = []

        for line in lines:
            c = line.count('\t')
            identationstring =  line[:c]

            if line[0] != '>':

                line_path = ExtractPreferenceFromText(line, "path")
                line_title = ExtractPreferenceFromText(line, "title")

                new_path = os.path.join(prefdir, line_path)

                if os.path.exists(new_path):
                    newlines.append(identationstring + '<path>' + new_path + '</path><title>' + line_title + '</title>\n')
            else:
                newlines.append(identationstring + line)

        f = open(scriptfile, 'wb')
        f.writelines(newlines)
        f.close()

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
