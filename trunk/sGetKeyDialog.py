#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#GetKey Dialog

import sShortcuts
import wx

class sGetTextCtrl(wx.TextCtrl):
    def __init__(self, parent, ignorestring, grandparent):
        #Bug-Report With Fix, Christian Daven.
        wx.TextCtrl.__init__(self, parent, -1, "Hit A Key", wx.DefaultPosition, wx.DefaultSize, style=wx.TE_PROCESS_TAB|wx.TE_PROCESS_ENTER)

        self.ancestor = grandparent

        self.valuestring = ''

        self.allowControl = not (ignorestring.find("Control") > -1)
        self.allowShift = not (ignorestring.find("Shift") > -1)
        self.allowMeta = not (ignorestring.find("Meta") > -1)
        self.allowAlt = not (ignorestring.find("Alt") > -1)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def GetValue(self):
        return self.valuestring

    def OnKeyDown(self, event):
        keystr = ""
        keycode = event.GetKeyCode()
        if (keycode == wx.WXK_CONTROL) or (keycode == 309) or (keycode == wx.WXK_SHIFT):
            return
        if event.ControlDown() and self.allowControl:
            keystr = "Control"
        if event.ShiftDown() and self.allowShift:
            keystr = keystr + "Shift"
        if event.AltDown() and self.allowAlt:
            keystr = keystr + "Alt"
        if event.MetaDown() and self.allowMeta:
            keystr = keystr + "Meta"
        keystr = keystr + str(keycode)
        self.SetValue(keystr)

    def SetValue(self, value):
        self.valuestring = value

        vstring = ''
        if sShortcuts.MatchControl(value):
            vstring += "Control + "
        if sShortcuts.MatchShift(value):
            vstring += "Shift + "
        if sShortcuts.MatchAlt(value):
            vstring += "Alt + "
        if sShortcuts.MatchMeta(value):
            vstring += "Meta + "

        vstring = vstring + sShortcuts.GetKeycodeStringFromShortcut(value)

        wx.TextCtrl.SetValue(self, vstring)

class sGetKeyDialog(wx.Dialog):

    def __init__(self, parent, ignorestring, grandparent):
        wx.Dialog.__init__(self, parent, -1, ("Hit A Key"), wx.DefaultPosition, wx.Size(200, 200), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.txtKey = sGetTextCtrl(self, ignorestring, grandparent)
        self.theSizer.Add(self.txtKey, 1, wx.EXPAND)
        self.btnClear = wx.Button(self, 102, "Clear")
        self.btnClose = wx.Button(self, 101, "&Close")

        self.theSizer.Add(self.btnClear, 1, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.btnClose, 1, wx.SHAPED | wx.ALIGN_CENTER)

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.txtKey.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnbtnClose, id=101)
        self.Bind(wx.EVT_BUTTON, self.OnbtnClear, id=102)

    def SetKeyString(self, keystring):
        if sShortcuts.GetKeycodeFromShortcut(keystring):
            self.txtKey.SetValue(keystring)
        else:
            self.txtKey.SetValue("Hit A Key")

    def GetKeyString(self):
        y = self.txtKey.GetValue()
        if y == "Hit A Key":
            return ""
        return y

    def OnbtnClear(self, event):
        self.txtKey.SetValue("Hit A Key")

    def OnbtnClose(self, event):
        self.EndModal(0)