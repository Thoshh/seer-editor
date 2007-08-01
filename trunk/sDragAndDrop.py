#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Drag and Drop

import wx, wx.stc

class sDropTarget(wx.DropTarget):
    def __init__(self, window):
        wx.DropTarget.__init__(self)
        self.window = window.grandparent

        window.Bind(wx.stc.EVT_STC_START_DRAG, self.OnStartDrag, id=window.GetId())

        self.data = wx.DataObjectComposite()
        self.dtext = wx.TextDataObject()
        self.dfilename = wx.FileDataObject()
        self.data.Add(self.dtext, True)
        self.data.Add(self.dfilename)

        self.draginitiatedfromstc = False

        self.moddown = False

        self.SetDataObject(self.data)

    def DropFiles(self, filenames):
        filenames = map(lambda x: x.replace("\\", "/"), filenames)
        alreadyopen = self.window.GetAlreadyOpen()
        if self.window.txtDocument.filename:
            for filename in filenames:
                if filename in alreadyopen:
                    self.window.setDocumentTo(alreadyopen.index(filename))
                else:
                    self.window.OpenFile(filename, True)
        else:
            if filenames[0] in alreadyopen:
                self.window.setDocumentTo(0)
            else:
                self.window.OpenFile(filenames[0], self.window.txtDocumentArray[0].GetModify())
            x = 1
            l = len(filenames)
            while x < l:
                if filenames[x] in alreadyopen:
                    self.window.setDocumentTo(alreadyopen.index(filenames[x]))
                else:
                    self.window.OpenFile(filenames[x], True)
                x = x + 1

    def DropText(self, text, point):
        if self.window.prefs.draganddropmode != 2:
            if self.draginitiatedfromstc:
                if ((self.window.prefs.draganddroptextmode == 0) and self.moddown) or \
                ((self.window.prefs.draganddroptextmode == 1) and (not self.moddown)):
                    self.window.txtDocument.SetSelectedText('')
            position = self.window.txtDocument.PositionFromPoint(point)
            self.window.txtDocument.InsertText(position, text)
            self.window.txtDocument.GotoPos(position+len(text))


    def OnDrop(self, x, y):
        if self.draginitiatedfromstc==1 and self.window.prefs.draganddropmode==2:
            return False
        else:
            return True
        
    def OnData(self, x, y, theData):
        self.GetData()
        if self.dtext.GetTextLength() > 1:
            self.DropText(self.dtext.GetText(), wx.Point(x, y))
            self.dtext.SetText('')
        else:
            self.DropFiles(self.dfilename.GetFilenames())

        self.draginitiatedfromstc = False

        return theData

    def OnStartDrag(self, event):
        self.draginitiatedfromstc = True

    def SetModifierDown(self, moddown):
        self.moddown = moddown