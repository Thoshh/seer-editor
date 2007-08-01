#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Menus

import os.path
import wx

class sMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent
        self.bitmapdirectory = self.parent.programdirectory + "/bitmaps/16/"

    def Append(self, id, label, LaunchesDialog = False, AmpersandAt = -1, AbsoluteLabel=''):
        ''' Appends the item, any applicable bitmap, and also any keyboard shortcut. '''

        item = wx.MenuItem(self, id, self.parent.getmenulabel(label, LaunchesDialog, AmpersandAt, AbsoluteLabel))

        bitmap = self.bitmapdirectory + label + '.png'
        if os.path.exists(bitmap):
            item.SetBitmap(wx.BitmapFromImage(wx.Image(bitmap, wx.BITMAP_TYPE_PNG)))

        return self.AppendItem(item)
