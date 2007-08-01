#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Bookmarks Menu

import os.path
import wx
from sProperty import *
import sScrolledMessageDialog

class sBookmarksMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.ID_BOOKMARK_BASE = 5500

        self.ID_BOOKMARK_MENU = 5199

        self.bookmarks = []

        self.parent = parent
        self.datdirectory = parent.datdirectory

        self.loadBookmarks()

    def loadBookmarks(self):
        bookfile = self.datdirectory + "/bookmarks.dat"
        if os.path.exists(bookfile):
            try:
                #Read from the file
                f = open(bookfile, 'r')
                folders = [self]
                folderindex = 0
                menuTitles = []
                menuTitleindex = -1
                lastCount = 1
                bookmarkcount = 0
                #Skip the First Line
                line = f.readline()
                #Initialize
                line = f.readline()
                while line:
                    c = line.count('\t')
                    line = line[c:].rstrip()
                    while lastCount > c:
                        folders[(folderindex - 1)].AppendMenu(self.ID_BOOKMARK_MENU, menuTitles.pop(), folders.pop())
                        folderindex = folderindex - 1
                        menuTitleindex = menuTitleindex - 1
                        lastCount = lastCount - 1
                    if line[0] == '>':
                        folders.append(wx.Menu())
                        menuTitles.append(line[1:])
                        folderindex = folderindex + 1
                        menuTitleindex = menuTitleindex + 1
                        c = c + 1
                    else:
                        self.bookmarks.append(line)
                        self.parent.Bind(wx.EVT_MENU, self.OnBookmark, id=(self.ID_BOOKMARK_BASE + bookmarkcount))
                        folders[folderindex].Append((self.ID_BOOKMARK_BASE + bookmarkcount), line, line)
                        bookmarkcount = bookmarkcount + 1
                    lastCount = c
                    line = f.readline()
                f.close()
                #Add any menus not yet added:
                c = 1
                while lastCount > c:
                    folders[(folderindex - 1)].AppendMenu(self.ID_BOOKMARK_MENU, menuTitles.pop(), folders.pop())
                    folderindex = folderindex - 1
                    menuTitleindex = menuTitleindex - 1
                    lastCount = lastCount - 1
            except:
                sScrolledMessageDialog.ShowMessage(self.parent, ("Your bookmarks file is a tad messed up.\n"), "Error")

    def OnBookmark(self, event):
        bookmarkindex = event.GetId() - self.ID_BOOKMARK_BASE
        if not (os.path.exists(self.bookmarks[bookmarkindex])):
            sScrolledMessageDialog.ShowMessage(self.parent, ("Error with: " + self.bookmarks[bookmarkindex] + "\nBookmark does not actually exist.\n"), "Error")
            return
        if os.path.isdir(self.bookmarks[bookmarkindex]):
            self.parent.ddirectory = self.bookmarks[bookmarkindex].replace("\\", "/")
            self.parent.OnOpen(event)
            return
        old = self.parent.txtDocument.filename
        filename = self.bookmarks[bookmarkindex].replace("\\", "/")

        alreadyopen = self.parent.GetAlreadyOpen()
        if filename in alreadyopen:
            self.parent.setDocumentTo(alreadyopen.index(filename))
            return

        if (len(old) > 0) or self.parent.txtDocument.GetModify():
            self.parent.OpenFile(filename, True)
        else:
            self.parent.OpenFile(filename, False)

    def reloadBookmarks(self):
        mnuitems = self.GetMenuItems()
        num = len(mnuitems)
        x = 0
        while x < num:
            self.Remove(mnuitems[x].GetId())
            #mnuitems[x].Destroy()
            x = x + 1
        self.bookmarks = []
        self.loadBookmarks()
