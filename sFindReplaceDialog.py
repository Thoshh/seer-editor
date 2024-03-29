#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Initial code framework based from DrPython, Copyright 2003-2007 Daniel Pozmanter

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

#FindReplace Dialog

import wx
import wx.stc
import sScrolledMessageDialog
import re

class sFinder:
    def __init__(self, parent, stc, oldfinder=None):
        self.parent = parent
        self.stc = stc
        self.reset()
        self.Copy(oldfinder)

    def Copy(self, finder):
        if finder:
            self.findtext = finder.findtext
            self.findflags = finder.findflags
            self.backwards = finder.backwards
            self.RE = finder.RE
            self.docEnd = self.stc.GetTextLength()
            self.SetTargetRange(0, self.docEnd)

    def DoFind(self, findtext, findflags, backwards=False):
        self.parent.SetStatusText(findtext, 2)
        self.RE = 0
        self.rectanglefind = 0
        doclength = self.stc.GetLength()

        self.findtext = findtext
        self.findflags = findflags

        prev = self.findpos

        if self.backwards != backwards:
            self.backwards = backwards

        if backwards:
            endpos = self.targetStart
        else:
            endpos = self.targetEnd

        self.findpos = self.stc.FindText(self.findpos, endpos, findtext, findflags)

        if self.findpos == -1:
            if self.stc.FindText(self.targetStart, self.targetEnd, findtext, findflags) == -1:
                if self.parent.prefs.enablefeedback:
                    sScrolledMessageDialog.ShowMessage(self.parent, ('Search string "' + findtext + '" not found.'), "Seer Find")
                else:
                    self.parent.SetStatusText('NOT FOUND: ' + findtext, 2)
                return
            if ((self.findpos >= doclength) or (self.findpos < 0)) and (doclength > 0):
                self.lastposition = -1
                if self.backwards:
                    msg = 'Start of document reached: "' + findtext + '".\nStart again from the end?'
                    self.findpos = self.targetEnd
                else:
                    msg = 'End of document reached: "' + findtext + '".\nStart again from the beginning?'
                    self.findpos = self.targetStart
                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.OK
                else:
                    answer = wx.MessageBox(msg, "Seer Find", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                if answer == wx.OK:
                    self.stc.GotoPos(self.findpos)
                    if self.backwards:
                        self.DoFindPrevious()
                    else:
                        self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return
            
        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        endpos = self.findpos + len(findtext)

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = self.findpos + len(findtext)

        if backwards:
            self.findpos = self.findpos - 1
        else:
            self.findpos = self.findpos + 1

    def DoREFind(self, findtext, matchcase):
        self.RE = 1
        self.rectanglefind = 0

        self.findtext = findtext
        self.findflags = matchcase

        prev = self.findpos

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, 'Regular Expression Error', "Seer Find")
            return

        endpos = self.targetEnd

        matchedtext = regularexpression.search(self.stc.GetText()[self.findpos:endpos])

        if matchedtext is None:
            testforexist = regularexpression.search(self.stc.GetText())
            if testforexist is None:
                sScrolledMessageDialog.ShowMessage(self.parent, ('Regular expression "' + findtext + '" not found.'), "Seer Find")
                return
            self.lastposition = -1
            if prev > self.targetStart:
                self.findpos = self.targetStart
                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.OK
                else:
                    answer = wx.MessageBox('End of document reached: "' + findtext + '".\nStart again from the beginning?', "Seer Find", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                if answer == wx.OK:
                    self.stc.GotoPos(self.findpos)
                    self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
            return

        oldpos = self.findpos
        self.findpos = oldpos + matchedtext.start()
        endpos = oldpos + matchedtext.end()

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = endpos

        self.findpos = endpos

    def DoFindNext(self):
        if not self.findtext:
            return
        if not self.inselection:
            textlength = self.stc.GetTextLength()
            if textlength != self.docEnd:
                self.docEnd = textlength
                self.SetTargetRange(0, self.docEnd)
        self.findpos = self.stc.GetCurrentPos()
        if not self.RE:
            if self.rectanglefind:
                self.DoRectangleFind(self.findtext, self.findflags)
            else:
                self.DoFind(self.findtext, self.findflags)
            return
        if self.rectanglefind:
            self.DoRERectangleFind(self.findtext, self.findflags)
            return
        self.DoREFind(self.findtext, self.findflags)

    def DoFindPrevious(self):
        if not self.findtext:
            return
        if not self.inselection:
            textlength = self.stc.GetTextLength()
            if textlength != self.docEnd:
                self.docEnd = textlength
                self.SetTargetRange(self.docEnd, 0)
        self.findpos = self.stc.GetCurrentPos()
        if not self.RE:
            if (self.findpos == self.lastposition) and not self.rectanglefind:
                self.findpos = self.findpos - len(self.findtext) - 1
                self.stc.GotoPos(self.findpos)
            elif self.rectanglefind and (self.lastposition == -1) and (not self.backwards):
                self.stc.GotoPos(self.findpos)

            if self.rectanglefind:
                self.DoRectangleFind(self.findtext, self.findflags, True)
            else:
                self.DoFind(self.findtext, self.findflags, True)
        else:
            sScrolledMessageDialog.ShowMessage(self.parent, 'Find Previous Not Possible:\nRegular Expressions Are On.', 'Seer Find')

    def DoRectangleFind(self, findtext, matchcase, backwards=False):
        self.RE = 0
        self.rectanglefind = 1
        doclength = self.stc.GetLength()
        lenlines = len(self.Lines)

        if matchcase:
            self.findtext = findtext
        else:
            self.findtext = findtext.lower()

        prev = self.findpos

        if self.backwards != backwards:
            self.backwards = backwards
            self.findpos = self.stc.GetCurrentPos()

        endpos = self.targetEnd

        lineArrayPosition = self.getArrayPosition(self.findpos)
        if lineArrayPosition == -1:
            self.findpos = self.findpos - 1
            lineArrayPosition = self.getArrayPosition(self.findpos - 1)
            if lineArrayPosition == -1:
                self.findpos = -1
            else:
                relative_findpos = self.positions[lineArrayPosition].index(self.findpos) + 1
        else:
            relative_findpos = self.positions[lineArrayPosition].index(self.findpos)

        if self.findpos > -1:
            self.findpos = self.findInArray(lineArrayPosition, relative_findpos)

        if self.findpos == -1:
            if self.backwards:
                notFound = self.findInArray(0, self.positions[lenlines-1][len(self.positions[lenlines-1])-1]) == -1
            else:
                notFound = self.findInArray(0, 0) == -1
            if notFound:
                sScrolledMessageDialog.ShowMessage(self.parent, ('Search string "' + findtext + '" not found.'), "Seer Find")
                return
            if ((self.findpos >= doclength) or (self.findpos < 0)) and (doclength > 0):
                self.lastposition = -1
                if self.backwards:
                    msg = 'Start of document reached: "' + findtext + '".\nStart again from the end?'
                    self.findpos = self.targetEnd
                else:
                    msg = 'End of document reached: "' + findtext + '".\nStart again from the beginning?'
                    self.findpos = self.targetStart
                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.OK
                else:
                    answer = wx.MessageBox(msg, "Seer Find", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                if answer == wx.OK:
                    self.stc.GotoPos(self.findpos)
                    if self.backwards:
                        self.DoFindPrevious()
                    else:
                        self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        endpos = self.findpos + len(findtext)

        self.stc.EnsurePositionIsVisible(endpos)
        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = self.findpos + len(findtext)

    def DoRERectangleFind(self, findtext, matchcase):
        self.RE = 1
        self.rectanglefind = 1
        doclength = self.stc.GetLength()

        self.findtext = findtext
        self.findflags = matchcase

        prev = self.findpos

        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, 'Regular Expression Error', "Seer Find")
            return

        endpos = self.targetEnd
        if (self.findpos >= doclength) or (self.findpos < 0):
            self.findpos = 0

        lineArrayPosition = self.getArrayPosition(self.findpos)
        if lineArrayPosition == -1:
            self.findpos = self.findpos - 1
            lineArrayPosition = self.getArrayPosition(self.findpos - 1)
            if lineArrayPosition == -1:
                self.findpos = -1
            else:
                relative_findpos = self.positions[lineArrayPosition].index(self.findpos) + 1
        else:
            relative_findpos = self.positions[lineArrayPosition].index(self.findpos)

        if self.findpos > -1:
            matchedtext, newArrayPosition = self.searchInArray(regularexpression, lineArrayPosition, relative_findpos)
        else:
            matchedtext = None

        if matchedtext is None:
            testforexist, nap = self.searchInArray(regularexpression, 0, 0)
            if testforexist is None:
                sScrolledMessageDialog.ShowMessage(self.parent, ('Regular expression "' + findtext + '" not found.'), "Seer Find")
                return
            self.lastposition = -1
            if prev > self.targetStart:
                self.findpos = self.targetStart
                if self.parent.prefs.findreplaceautowrap:
                    answer = wx.OK
                else:
                    answer = wx.MessageBox('End of document reached: "' + findtext + '".\nStart again from the beginning?', "Seer Find", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                if answer == wx.OK:
                    self.stc.GotoPos(self.findpos)
                    self.DoFindNext()
                else:
                    self.stc.GotoPos(prev)
                return

        relative_findpos = matchedtext.start()

        self.findpos = self.positions[newArrayPosition][relative_findpos]

        endpos = self.findpos + (matchedtext.end() - matchedtext.start())

        if self.parent.prefs.docfolding:
            self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))

        self.stc.EnsurePositionIsVisible(endpos)

        self.stc.GotoPos(self.findpos)
        self.stc.SetSelectionStart(self.findpos)
        self.stc.SetSelectionEnd(endpos)
        self.lastposition = endpos

        self.findpos = endpos

    def findInArray(self, arrayposition, position):
        if self.backwards:
            r = self.Lines[arrayposition][:position].rfind(self.findtext)
            if r == -1:
                arrayposition -= 1
                while arrayposition > -1:
                    r = self.Lines[arrayposition].rfind(self.findtext)
                    if r == -1:
                        arrayposition -= 1
                    else:
                        return self.positions[arrayposition][r]
            else:
                return self.positions[arrayposition][r]
        else:
            l = len(self.Lines)
            r = self.Lines[arrayposition][position:].find(self.findtext)
            if r == -1:
                arrayposition += 1
                while arrayposition < l:
                    r = self.Lines[arrayposition].find(self.findtext)
                    if r == -1:
                        arrayposition += 1
                    else:
                        return self.positions[arrayposition][r]
            else:
                return self.positions[arrayposition][r]
        return -1

    def getArrayPosition(self, position):
        x = 0
        for posArray in self.positions:
            if position in posArray:
                return x
            x += 1
        return -1

    def GetFindPos(self):
        return self.findpos

    def GetFindText(self):
        return self.findtext

    def RectangleReplaceAll(self, findtext, replacetext, matchcase):
        targetText = self.stc.GetSelectedText()

        if not matchcase:
            targetText = targetText.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        lines = targetText.strip().split(eolchar)

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(lines[0])

        x = 0

        for line in lines:
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            p = line.find(findtext)
            if p > -1:
                line = line.replace(findtext, replacetext)
                self.stc.SetTargetStart(position_of_first_character)
                self.stc.SetTargetEnd(position_of_first_character+lenline)
                self.stc.ReplaceTarget(line)
                x = x + 1
            linenumber = linenumber + 1

        return x

    def RectangleREReplaceAll(self, findtext, replacetext, matchcase):
        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, 'Regular Expression Error', "Seer Replace")
            return

        targetText = self.stc.GetSelectedText()

        if not matchcase:
            targetText = targetText.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        lines = targetText.strip().split(eolchar)

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(lines[0])

        y = 0

        for line in lines:
            #You need to update the position(do the replace) during the loop.
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            line, x = regularexpression.subn(replacetext, line)
            y = y + x
            self.stc.SetTargetStart(position_of_first_character)
            self.stc.SetTargetEnd(position_of_first_character+lenline)
            self.stc.ReplaceTarget(line)
            linenumber = linenumber + 1

        return y

    def ReplaceAll(self, findtext, replacetext, flags, prompt = 0):
        p = self.stc.FindText(self.targetStart, self.targetEnd, findtext, flags)
        diff = len(replacetext) - len(findtext)
        x = 0
        notfirst = 0
        favpos = wx.Point(5, 5)
        while p != -1:
            if self.parent.prefs.docfolding:
                self.stc.EnsureVisible(self.stc.LineFromPosition(p))
            self.stc.GotoPos(p)
            self.stc.EnsureCaretVisible()
            self.stc.SetTargetStart(p)
            self.stc.SetTargetEnd(p + len(findtext))
            if prompt:
                self.stc.SetSelection(p, (p + len(findtext)))
                d = wx.SingleChoiceDialog(self.parent, ("Found \"" + findtext + "\" at Line: " \
                + str(self.stc.LineFromPosition(p)+1) + \
                " Col: " + str(self.stc.GetColumn(p))
                + "\n(Hit Cancel to Stop)"), "Replace", ["Replace", "Skip"], wx.CHOICEDLG_STYLE)
                if notfirst:
                    d.Move(favpos)
                else:
                    notfirst = 1
                answer = d.ShowModal()
                favpos = d.GetPosition()
                d.Destroy()
                if answer == wx.ID_OK:
                    if d.GetStringSelection() == "Replace":
                        self.stc.ReplaceTarget(replacetext)
                        self.targetEnd = self.targetEnd + diff
                    else:
                        x = x - 1
                        p = p + 1
                    p = self.stc.FindText((p + len(replacetext)), self.targetEnd, findtext, flags)
                else:
                    p = -1
                    x = x - 1
            else:
                self.stc.ReplaceTarget(replacetext)
                self.targetEnd = self.targetEnd + diff
                p = self.stc.FindText((p + len(replacetext)), self.targetEnd, findtext, flags)
            x = x + 1
        return x

    def REReplaceAll(self, findtext, replacetext, matchcase, prompt = 0):
        case = 0
        if not matchcase:
            case = re.IGNORECASE

        try:
            regularexpression = re.compile(findtext, case | re.MULTILINE)
        except:
            sScrolledMessageDialog.ShowMessage(self.parent, 'Regular Expression Error', "Seer Replace")
            return

        oldtext = self.stc.GetText()
        if not prompt:
            newtext, x = regularexpression.subn(replacetext, oldtext[self.targetStart:self.targetEnd])

            self.stc.SetText(oldtext[0:self.targetStart] + newtext + oldtext[self.targetEnd:])
        else:
            matchedtext = regularexpression.search(self.stc.GetText()[self.findpos:self.targetEnd])

            diff = len(replacetext) - len(findtext)

            x = 0
            notfirst = 0

            favpos = wx.Point(5, 5)
            while matchedtext is not None:

                oldpos = self.findpos
                self.findpos = oldpos + matchedtext.start()
                endpos = oldpos + matchedtext.end()

                if self.parent.prefs.docfolding:
                    self.stc.EnsureVisible(self.stc.LineFromPosition(self.findpos))
                self.stc.GotoPos(self.findpos)
                self.stc.EnsureCaretVisible()
                self.stc.SetSelectionStart(self.findpos)
                self.stc.SetSelectionEnd(endpos)
                self.stc.SetTargetStart(self.findpos)
                self.stc.SetTargetEnd(endpos)

                d = wx.SingleChoiceDialog(self.parent, ("Found \"" + findtext + "\" at Line: " \
                + str(self.stc.LineFromPosition(self.findpos)+1) + \
                " Col: " + str(self.stc.GetColumn(self.findpos)) + \
                "\n(Hit Cancel to Stop)"), "Replace", ["Replace", "Skip"], wx.CHOICEDLG_STYLE)

                if notfirst:
                    d.Move(favpos)
                else:
                    notfirst = 1
                answer = d.ShowModal()
                favpos = d.GetPosition()
                d.Destroy()
                if answer == wx.ID_OK:
                    if d.GetStringSelection() == "Replace":
                        self.stc.ReplaceTarget(replacetext)
                        self.findpos = self.findpos + len(replacetext)
                        self.targetEnd = self.targetEnd + diff
                    else:
                        self.findpos = endpos
                        x = x - 1
                    x = x + 1

                    matchedtext = regularexpression.search(self.stc.GetText()[self.findpos:self.targetEnd])
                else:
                    matchedtext = None

        return x

    def reset(self):
        self.inselection = 0
        self.findflags = 0
        self.findpos = 0
        self.lastposition = 0
        self.backwards = 0
        self.findtext = ""
        self.targetStart = 0
        self.targetEnd = 0
        self.docEnd = 0
        self.RE = 0
        self.rectanglefind = 0

    def searchInArray(self, regularexpression, arrayposition, position):
        l = len(self.Lines)
        match = regularexpression.search(self.Lines[arrayposition][position:])
        if match is None:
            arrayposition += 1
            while arrayposition < l:
                match = regularexpression.search(self.Lines[arrayposition])
                if match is None:
                    arrayposition += 1
                else:
                    return match, arrayposition
        return match, arrayposition

    def SetFindPos(self, findpos):
        self.findpos = findpos

    def SetFindText(self, findtext):
        self.findtext = findtext

    def SetTargetPositions(self, matchcase):
        self.targetText = self.stc.GetSelectedText()

        self.findflags = matchcase

        if not matchcase:
            self.targetText = self.targetText.lower()

        eolchar = self.stc.GetEndOfLineCharacter()

        self.Lines = self.targetText.strip().split(eolchar)

        self.targetText = self.targetText.replace(eolchar, '')

        c = self.stc.GetColumn(self.targetStart)

        linenumber = self.stc.LineFromPosition(self.targetStart)

        lenline = len(self.Lines[0])

        self.positions = []

        for line in self.Lines:
            position_of_first_character = c + self.stc.PositionFromLine(linenumber)
            self.positions.append(range(position_of_first_character, position_of_first_character+lenline))
            linenumber = linenumber + 1

    def SetTargetRange(self, start, end, backwards = 0):
        self.docEnd = self.stc.GetTextLength()
        self.inselection = (start > 0) | (end < self.docEnd)

        self.findpos = start
        if backwards:
            self.findpos = end
        self.targetStart = start
        self.targetEnd = end

class sFindTextCtrl(wx.ComboBox):
    def __init__(self, parent, id, value, pos, size, returnfunction = None, InFiles = False):
        wx.ComboBox.__init__(self, parent, id, value, pos, size)

        self.parent = parent
        if InFiles:
            self.ancestor = parent.parent.parent
        else:
            self.ancestor = parent.parent
        if self.ancestor.PLATFORM_IS_WIN:
            self.doReplace = True
            self.cr = chr(5)
        else:
            self.doReplace = False
            self.cr = '\r'

        self.ID_CHAR_BASE = 20

        self.ID_MENU_BASE = 50

        self.ID_HISTORY_BASE = 420

        self.returnfunc = returnfunction
        if self.returnfunc is None:
            self.returnfunc = self.parent.OnbtnFind

        self.Bind(wx.EVT_CHAR, self.OnChar)

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnPopUp)

        if self.ancestor.PLATFORM_IS_WIN:
            self.insertionpoint = -1
            self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def AppendToHistory(self, targetList):
        text = self.GetText()
        try:
            i = targetList.index(text)
            targetList.pop(i)
        except:
            pass

        targetList.append(text)

    def GetText(self):
        text = self.GetValue()
        if self.doReplace:
            return text.replace(chr(5), '\r')
        else:
            return text

    def OnChar(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.parent.OnbtnCancel(event)
        elif event.GetKeyCode() == wx.WXK_RETURN:
            self.returnfunc(event)
        else:
            event.Skip()

    def OnFocus(self, event):
        self.insertionpoint = -1
        event.Skip()

    def OnKillFocus(self, event):
        self.insertionpoint = self.GetInsertionPoint()
        event.Skip()

    def OnPopUp(self, event):
        self.PopUp(event.GetPosition())

    def OnPopUpMenu(self, event):
        eid = event.GetId()

        pos = self.GetInsertionPoint()
        if self.ancestor.PLATFORM_IS_WIN:
            if self.insertionpoint > -1:
                pos = self.insertionpoint
        text = self.GetValue()

        if eid == self.ID_CHAR_BASE:
            self.SetValue(text[:pos] + '\t' + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_CHAR_BASE+1:
            self.SetValue(text[:pos] + '\n' + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_CHAR_BASE+2:
            self.SetValue(text[:pos] + self.cr + text[pos:])
            self.SetInsertionPoint(pos+1)
        elif eid == self.ID_MENU_BASE+1:
            self.Cut()
        elif eid == self.ID_MENU_BASE+2:
            self.Copy()
        elif eid == self.ID_MENU_BASE+3:
            self.Paste()
        elif eid == self.ID_MENU_BASE+4:
            f, to = self.GetSelection()
            self.Remove(f, to)
        elif eid == self.ID_MENU_BASE+5:
            self.SetValue("")

        self.SetFocus()

    def PopUp(self, pos):
        self.PopUpMenu = wx.Menu()

        self.CharMenu = wx.Menu()

        self.CharMenu.Append(self.ID_CHAR_BASE, "Tab (\\t)")
        self.CharMenu.Append(self.ID_CHAR_BASE+1, "Newline (\\n)")
        self.CharMenu.Append(self.ID_CHAR_BASE+2, "Carraige Return (\\r)")

        self.PopUpMenu.Append(self.ID_MENU_BASE+5, "Clear Text")

        self.PopUpMenu.AppendSeparator()

        self.PopUpMenu.AppendMenu(self.ID_MENU_BASE, "Insert Special Character", self.CharMenu)

        self.PopUpMenu.AppendSeparator()

        self.PopUpMenu.Append(self.ID_MENU_BASE+1, "Cut")
        self.PopUpMenu.Append(self.ID_MENU_BASE+2, "Copy")
        self.PopUpMenu.Append(self.ID_MENU_BASE+3, "Paste")
        self.PopUpMenu.Append(self.ID_MENU_BASE+4, "Delete")

        x = 0
        y = 0
        while x < 6:
            if y < 3:
                self.Bind(wx.EVT_MENU, self.OnPopUpMenu, id=self.ID_CHAR_BASE+y)
                y = y + 1
            self.Bind(wx.EVT_MENU, self.OnPopUpMenu, id=self.ID_MENU_BASE+x)
            x = x + 1

        self.PopupMenu(self.PopUpMenu, pos)

        self.PopUpMenu.Destroy()

    def SetHistory(self, history):
        if self.GetCount() > 0:
            self.Clear()
        l = len(history)
        self.Append('')
        x = l - 1
        while x > -1:
            self.Append(history[x])
            x = x - 1
        if l > 0:
            self.SetMark(0, len(history[l-1]))

class sFindReplaceDialog(wx.Dialog):
    def __init__(self, parent, id, title, stc, IsReplace = 0):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(-1, -1), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)

        self.ID_FIND = 1001
        self.ID_CANCEL = 1002

        self.ID_CHK_REGEX = 1010
        self.ID_CREATERE = 1011

        self.ID_SEARCH_TXT = 1012

        self.ID_BTNSF = 98
        self.ID_BTNRW = 99

        self.parent = parent

        self.stc = stc

        self.theSizer = wx.FlexGridSizer(8, 3, 5, 10)

        self.IsReplace = IsReplace

        #Size Buffer
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "Search For: "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.txtSearchFor = sFindTextCtrl(self, self.ID_SEARCH_TXT, "", wx.DefaultPosition, wx.Size(250, -1))
        self.btnPopUpSearchFor = wx.Button(self, self.ID_BTNSF, " Menu ")
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.txtSearchFor, 1, wx.SHAPED)
        self.theSizer.Add(self.btnPopUpSearchFor, 1, wx.SHAPED)

        self.txtSearchFor.SetHistory(parent.FindHistory)

        if IsReplace:
            self.txtReplaceWith = sFindTextCtrl(self, -1, "", wx.DefaultPosition, wx.Size(250, -1))
            self.btnPopUpReplaceWith = wx.Button(self, self.ID_BTNRW, " Menu ")
            self.txtReplaceWith.SetHistory(parent.ReplaceHistory)

        self.chkRegularExpression = wx.CheckBox(self, self.ID_CHK_REGEX, "RegularExpression")
        self.btnCreateRE = wx.Button(self, self.ID_CREATERE, " &Create ")
        self.chkMatchCase = wx.CheckBox(self, -1, "Match Case")
        self.chkFindBackwards = wx.CheckBox(self, -1, "Find Backwards")
        self.chkWholeWord = wx.CheckBox(self, -1, "Whole Word")
        self.chkInSelection = wx.CheckBox(self, -1, "In Selection")
        self.chkFromCursor = wx.CheckBox(self, -1, "From Cursor")

        #Prefs
        self.chkRegularExpression.SetValue(parent.prefs.findreplaceregularexpression)
        self.btnCreateRE.Enable(parent.prefs.findreplaceregularexpression)
        self.chkMatchCase.SetValue(parent.prefs.findreplacematchcase)
        self.chkFindBackwards.SetValue(parent.prefs.findreplacefindbackwards)
        self.chkWholeWord.SetValue(parent.prefs.findreplacewholeword)
        self.chkInSelection.SetValue(parent.prefs.findreplaceinselection)
        self.chkFromCursor.SetValue(parent.prefs.findreplacefromcursor)

        self.chkInSelection.Enable(len(parent.txtDocument.GetSelectedText()) > 0)

        if IsReplace:
            self.chkPromptOnReplace  = wx.CheckBox(self, -1, "Prompt on Replace")
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, "Replace With: "), 1, wx.SHAPED)
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
            self.theSizer.Add(self.txtReplaceWith, 1 ,wx.SHAPED)
            self.theSizer.Add(self.btnPopUpReplaceWith, 1, wx.SHAPED)

            self.chkFromCursor.Disable()
            self.chkFindBackwards.Disable()

            #Prefs
            self.chkPromptOnReplace.SetValue(parent.prefs.findreplacepromptonreplace)

            self.Bind(wx.EVT_BUTTON,  self.OnbtnPopUp, id=self.ID_BTNRW)

        #Size Buffer
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkRegularExpression, 1, wx.SHAPED)
        self.theSizer.Add(self.btnCreateRE, 1, wx.SHAPED)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkMatchCase, 1, wx.SHAPED)
        self.theSizer.Add(self.chkFindBackwards, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkWholeWord, 1, wx.SHAPED)
        self.theSizer.Add(self.chkInSelection, 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.chkFromCursor, 1, wx.SHAPED)
        if IsReplace:
            self.theSizer.Add(self.chkPromptOnReplace, 1, wx.SHAPED)
        else:
            self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)

        self.btnCancel = wx.Button(self, self.ID_CANCEL, "&Cancel")
        self.btnFind = wx.Button(self, self.ID_FIND, "&Ok")
        self.btnFind.Enable(False)

        self.theSizer.Add(wx.StaticText(self, -1, "    "), 1, wx.SHAPED)
        self.theSizer.Add(self.btnCancel, 1, wx.SHAPED)
        self.theSizer.Add(self.btnFind, 1, wx.SHAPED)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        self.btnFind.SetDefault()
        self.txtSearchFor.SetFocus()

        self.Bind(wx.EVT_BUTTON,  self.OnbtnCancel, id=self.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnFind, id=self.ID_FIND)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnCreateRE, id=self.ID_CREATERE)
        self.Bind(wx.EVT_BUTTON,  self.OnbtnPopUp, id=self.ID_BTNSF)

        self.Bind(wx.EVT_CHECKBOX,  self.OnCheckRegularExpression, id=self.ID_CHK_REGEX)

        self.Bind(wx.EVT_TEXT, self.OnTextChanged, id=self.ID_SEARCH_TXT)

        self.parent.LoadDialogSizeAndPosition(self, 'findreplacedialog.sizeandposition.dat')

    def OnCloseW(self, event):
        self.parent.SaveDialogSizeAndPosition(self, 'findreplacedialog.sizeandposition.dat')
        if event is not None:
            event.Skip()

    def GetOptions(self):
        rarray = [self.chkRegularExpression.GetValue(), self.chkMatchCase.GetValue(), \
        self.chkFindBackwards.GetValue(), self.chkWholeWord.GetValue(), \
        self.chkInSelection.GetValue(), self.chkFromCursor.GetValue()]

        if self.IsReplace:
            rarray.append(self.chkPromptOnReplace.GetValue())

        return rarray

    def OnbtnCancel(self, event):
        self.Close(1)

    def OnbtnCreateRE(self, event):
        from sRegularExpressionDialog import sRegularExpressionDialog
        d = sRegularExpressionDialog(self, -1, "Create Regular Expression")
        d.Show()

    def OnbtnFind(self, event):
        if not self.btnFind.IsEnabled():
            return
        self.Show(0)
        findflags = 0
        findbackwards = self.chkFindBackwards.GetValue()

        isRegularExpression = self.chkRegularExpression.GetValue()
        isMatchCase = self.chkMatchCase.GetValue()

        self.txtSearchFor.AppendToHistory(self.parent.FindHistory)
        if self.IsReplace:
            self.txtReplaceWith.AppendToHistory(self.parent.ReplaceHistory)

        #Set Target Range
        if self.chkInSelection.GetValue():
            selstart = self.stc.GetSelectionStart()
            selend = self.stc.GetSelectionEnd()
            if (selend - selstart) < 1:
                selstart = 0
                selend = self.stc.GetTextLength()
            self.stc.Finder.SetTargetRange(selstart, selend, findbackwards)
            #Do the Search if it's a rectangle:
            if self.stc.SelectionIsRectangle():
                if self.IsReplace:
                    if isRegularExpression:
                        x = self.stc.Finder.RectangleREReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase)
                        if self.parent.prefs.enablefeedback:
                            sScrolledMessageDialog.ShowMessage(self, (str(x) + " occurances of \"" + self.txtSearchFor.GetText() + "\" replaced with \"" + self.txtReplaceWith.GetText() + "\""), "Replace")
                    else:
                        x = self.stc.Finder.RectangleReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase)
                        if self.parent.prefs.enablefeedback:
                            sScrolledMessageDialog.ShowMessage(self, (str(x) + " occurances of \"" + self.txtSearchFor.GetText() + "\" replaced with \"" + self.txtReplaceWith.GetText() + "\""), "Replace")
                else:
                    self.stc.Finder.SetTargetPositions(isMatchCase)
                    if isRegularExpression:
                        self.stc.Finder.DoRERectangleFind(self.txtSearchFor.GetText(), isMatchCase)
                    else:
                        self.stc.Finder.DoRectangleFind(self.txtSearchFor.GetText(), isMatchCase, findbackwards)
                self.Close(1)
                return
        else:
            self.stc.Finder.SetTargetRange(0, self.stc.GetTextLength(), findbackwards)


        if (self.chkFromCursor.GetValue()) and (not self.IsReplace):
            self.stc.Finder.SetFindPos(self.stc.GetCurrentPos())

        #Do Search
        if isRegularExpression:
            if self.IsReplace:
                x = self.stc.Finder.REReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), isMatchCase, self.chkPromptOnReplace.GetValue())
                if x == 0:
                    if self.parent.prefs.enablefeedback:
                        sScrolledMessageDialog.ShowMessage(self, 'Search string: "' + self.txtSearchFor.GetText() + '" not found.', 'Seer Replace')
                    else:
                        self.parent.SetStatusText( '"'+self.txtSearchFor.GetText() + '" NOT FOUND', 2)
                else:
                    if self.parent.prefs.enablefeedback:
                        sScrolledMessageDialog.ShowMessage(self, (str(x) + " occurances of \"" + self.txtSearchFor.GetText() + "\" replaced with \"" + self.txtReplaceWith.GetText() + "\""), "Replace")
                    else:
                        self.parent.SetStatusText(str(x) + ' occurances of "' + self.txtSearchFor.GetText() + '" replaced with "' + self.txtReplaceWith.GetText() + '"', 2)
            else:
                self.stc.Finder.DoREFind(self.txtSearchFor.GetText(), isMatchCase)
        else:
            #Set Flags
            if self.chkWholeWord.GetValue():
                findflags = findflags | wx.stc.STC_FIND_WHOLEWORD
            if isMatchCase:
                findflags = findflags | wx.stc.STC_FIND_MATCHCASE

            if self.IsReplace:
                x = self.stc.Finder.ReplaceAll(self.txtSearchFor.GetText(), self.txtReplaceWith.GetText(), findflags, self.chkPromptOnReplace.GetValue())
                if x == 0:
                    if self.parent.prefs.enablefeedback:
                        sScrolledMessageDialog.ShowMessage(self, 'Search string: "' + self.txtSearchFor.GetText() + '" not found.', 'Seer Replace')
                    else:
                        self.parent.SetStatusText( '"'+self.txtSearchFor.GetText() + '" NOT FOUND', 2)
                else:
                    if self.parent.prefs.enablefeedback:
                        sScrolledMessageDialog.ShowMessage(self, (str(x) + " occurances of \"" + self.txtSearchFor.GetText() + "\" replaced with \"" + self.txtReplaceWith.GetText() + "\""), "Replace")
                    else:
                        self.parent.SetStatusText(str(x) + ' occurances of "' + self.txtSearchFor.GetText() + '" replaced with "' + self.txtReplaceWith.GetText() + '"', 2)
            else:
                self.stc.Finder.DoFind(self.txtSearchFor.GetText(), findflags, findbackwards)

        self.Close(1)

        if self.IsReplace:
            self.parent.ReplaceOptions = self.GetOptions()
        else:
            self.parent.FindOptions = self.GetOptions()

    def OnbtnPopUp(self, event):
        eid = event.GetId()
        if eid == self.ID_BTNSF:
            s = self.txtSearchFor.GetPosition()[0]
            x = self.btnPopUpSearchFor.GetPosition()[0]
            self.txtSearchFor.PopUp((x-s, 0))
        elif eid == self.ID_BTNRW:
            s = self.txtReplaceWith.GetPosition()[0]
            x = self.btnPopUpReplaceWith.GetPosition()[0]
            self.txtReplaceWith.PopUp((x-s, 0))

    def OnCheckRegularExpression(self, event):
        usingRegularExpressions = self.chkRegularExpression.GetValue()
        self.btnCreateRE.Enable(usingRegularExpressions)
        self.chkWholeWord.Enable(not usingRegularExpressions)
        if not self.IsReplace:
            self.chkFindBackwards.Enable(not usingRegularExpressions)

    def OnTextChanged(self, event):
        self.btnFind.Enable(len(self.txtSearchFor.GetText()) > 0)

    def SetFindString(self, findstring):
        self.txtSearchFor.SetValue(findstring)
        self.txtSearchFor.SetMark(0, len(findstring))
        self.OnTextChanged(None)

    def SetOptions(self, OptionsArray):
        if OptionsArray:
            self.chkRegularExpression.SetValue(OptionsArray[0])
            self.btnCreateRE.Enable(OptionsArray[0])
            self.chkMatchCase.SetValue(OptionsArray[1])
            self.chkFindBackwards.SetValue(OptionsArray[2])
            self.chkWholeWord.SetValue(OptionsArray[3])
            self.chkInSelection.SetValue(OptionsArray[4])
            self.chkFromCursor.SetValue(OptionsArray[5])

            if self.IsReplace:
                self.chkPromptOnReplace.SetValue(OptionsArray[6])
