#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Printing.  Very simple.  No colors.
#Takes the font and size from the style given, and uses it to print with.

import wx.html

class sPrinter(wx.html.HtmlEasyPrinting):

    def __init__(self, parent):
        wx.html.HtmlEasyPrinting.__init__(self)
        self.parent = parent

    def HTMLify(self, text, linenumbers):
        #Prep Special Characters
        text = text.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")

        #Line numbers:
        if linenumbers:
            text = "1<a href=\"#\">00000</a>" + text.replace(' ', " &nbsp;")
            x = 0
            l = len(text)
            line = 2
            n = ""
            while x < l:
                if text[x] == '\n':
                    n = n + "\n" + str(line)
                    if line < 10:
                        n = n + "<a href=\"#\">00000</a>"
                    elif line < 100:
                        n = n + "<a href=\"#\">0000</a>"
                    elif line < 1000:
                        n = n + "<a href=\"#\">000</a>"
                    else:
                        n = n + "<a href=\"#\">00</a>"
                    line = line + 1
                else:
                    n = n + text[x]
                x = x + 1

            text = n

        #htmlify the text:
        thehtml = "<html><body link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">" \
        + text.replace('\n', "\n<br>") \
        + "</span></body></html>"

        #TabWidth
        twstring = "".zfill(self.parent.prefs.printtabwidth)
        twstring = "<a href=\"#\">" + twstring + "</a>"
        thehtml = thehtml.replace('\t', twstring)

        return thehtml

    def Print(self, text, filename, linenumbers = 1):
        self.SetHeader(filename)

        self.PrintText(self.HTMLify(text, linenumbers), filename)

    def PrinterSetup(self, parent):
        data = wx.PrintDialogData()

        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)
        data.SetMinPage(1)
        data.SetMaxPage(5)
        data.SetAllPages(True)

        dlg = wx.PrintDialog(parent, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPrintDialogData()
            self.log.WriteText('GetAllPages: %d\n' % data.GetAllPages())

        dlg.Destroy()

