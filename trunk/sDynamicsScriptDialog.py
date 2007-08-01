#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Dynamic sScript Dialog

import os.path
import wx
import sScrolledMessageDialog
from sText import sText

class sDynamicsScriptDialog(wx.Dialog):

    def __init__(self, parent, text):
        wx.Dialog.__init__(self, parent, -1, ("Dynamic sScript"), wx.DefaultPosition, wx.Size(600, 400), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.parent = parent

        self.txtScript = sText(self, -1, self.parent, 1)
        self.txtScript.SetText(text)
        self.txtScript.SetupPrefsDocument()
        self.theSizer.Add(self.txtScript, 9, wx.EXPAND)

        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnClose = wx.Button(self, 101, "&Close")
        self.btnOk = wx.Button(self, 102, "&Ok")
        self.theSizer.Add(wx.StaticText(self, -1, ""), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnClose, 0,  wx.SHAPED | wx.ALIGN_CENTER)
        self.commandSizer.Add(wx.StaticText(self, -1, "   "), 0, wx.ALIGN_CENTER | wx.SHAPED)
        self.commandSizer.Add(self.btnOk, 0,  wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.commandSizer, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.btnOk.SetDefault()

        self.SetAutoLayout(True)
        self.SetSizer(self.theSizer)

        self.Bind(wx.EVT_CLOSE, self.OnCloseW)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnClose, id=101)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnOk, id=102)

        self.parent.LoadDialogSizeAndPosition(self, 'dynamicsscriptdialog.sizeandposition.dat')

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, 'dynamicsscriptdialog.sizeandposition.dat')
        if event is not None:
            event.Skip()

    def OnbtnClose(self, event):
        self.Close(1)

    def OnbtnOk(self, event):
        value = self.txtScript.GetText()
        if value.find("sFilename") > -1:
            value = value.replace("sFilename", "self.parent.txtDocument.filename")
        if value.find("sScript") > -1:
            value = value.replace("sScript", "self.parent.sScript")
        if value.find("sDocument") > -1:
            value = value.replace("sDocument", "self.parent.txtDocument")
        if value.find("sPrompt") > -1:
            value = value.replace("sPrompt", "self.parent.txtPrompt")
        if value.find("sFrame") > -1:
            value = value.replace("sFrame", "self.parent")

        try:
            #Bug-Report/Fix (Submitted, Edited) Franz Steinhausier
            value = value.replace('\r', '\n')
            code = compile((value + '\n'), "Dynamic sScript", 'exec')
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, ("Error compiling dynamic script."), "Error", wx.DefaultPosition, wx.Size(550,300))
            return

        try:
            exec(code)
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, ("Error running dynamic script."), "Error", wx.DefaultPosition, wx.Size(550,300))
            return

    def GetText(self):
        return self.txtScript.GetText()