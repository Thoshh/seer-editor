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

#ToolBar File

import os.path
import sPrefsFile
import wx
import sScrolledMessageDialog

def getToolBarList(datdirectory):
    toolbarfile = datdirectory + "/toolbar.dat"
    if not os.path.exists(toolbarfile):
        return ["New", "Open", "Reload File", "Close", "Save", \
        "<Separator>", "Print File", "Print Prompt", \
        "<Separator>", "Find", "Replace", \
        "<Separator>",  "Preferences", "Toggle Prompt", "Toggle View Whitespace", \
        "<Separator>",  "Check Syntax", "Run", "Set Arguments", "Python", \
        "End", "Import All"]
    ToolBarList = []
    f = file(toolbarfile, 'r')
    line = f.readline().rstrip()
    while line:
        ToolBarList.append(line)
        line = f.readline().rstrip()
    f.close()
    return ToolBarList

def getCustomBitmaps(datdirectory):
    filename = datdirectory + "/toolbar.custom.icons.dat"
    if not os.path.exists(filename):
        return [], [], []

    nameArray = []
    fileArray16 = []
    fileArray24 = []

    f = file(filename, 'r')
    line = f.readline()
    while line:
        nameArray.append(sPrefsFile.ExtractPreferenceFromText(line, "Name"))
        fileArray16.append(sPrefsFile.ExtractPreferenceFromText(line, '16'))
        fileArray24.append(sPrefsFile.ExtractPreferenceFromText(line, '24'))
        line = f.readline()
    f.close()

    return nameArray, fileArray16, fileArray24

def getBitmapFileArray(bitmapNames, defaultbitmapdirectory, iconsize, customNames, customFiles):
    iconsizestr = str(iconsize)
    fileArray = []

    l = len(bitmapNames)
    x = 0
    while x < l:
        if not bitmapNames[x] == "<Separator>":
            if bitmapNames[x] in customNames:
                i = customNames.index(bitmapNames[x])
                t = customFiles[i]
                if not os.path.exists(t):
                    t = defaultbitmapdirectory + "/" + iconsizestr + "/" + bitmapNames[x] + ".png"
            else:
                t = defaultbitmapdirectory + "/" + iconsizestr + "/" + bitmapNames[x] + ".png"
            if not os.path.exists(t):
                t = defaultbitmapdirectory + "/" + iconsizestr + "/Default.png"
            fileArray.append(t)
        else:
            fileArray.append("<Separator>")
        x = x + 1

    return fileArray

def AddandReturn(frame, bitmapFileArray, IDNUM, count, title = ""):
    if title:
        frame.toolbar.AddSimpleTool(IDNUM, wx.BitmapFromImage(wx.Image(bitmapFileArray[count], wx.BITMAP_TYPE_PNG)), title)
        return IDNUM
    frame.toolbar.AddSimpleTool(IDNUM, wx.BitmapFromImage(wx.Image(bitmapFileArray[count], wx.BITMAP_TYPE_PNG)), frame.ToolBarList[count])
    return IDNUM

def SetupToolBar(frame):
    try:
        names, f16, f24 = getCustomBitmaps(frame.datdirectory)

        if frame.prefs.iconsize == 16:
            bitmapFileArray = getBitmapFileArray(frame.ToolBarList, frame.bitmapdirectory, frame.prefs.iconsize, names, f16)
        else:
            bitmapFileArray = getBitmapFileArray(frame.ToolBarList, frame.bitmapdirectory, frame.prefs.iconsize, names, f24)


        frame.toolbar.SetToolBitmapSize(wx.Size(frame.prefs.iconsize, frame.prefs.iconsize))

        ToolBarIdList = []

        x = 0
        l = len(frame.ToolBarList)
        while x < l:
            if frame.ToolBarList[x] == "<Separator>":
                frame.toolbar.AddSeparator()
                ToolBarIdList.append(-300)

            elif frame.ToolBarList[x] == "New":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_NEW, x))
            elif frame.ToolBarList[x] == "Open":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_OPEN, x))
            elif frame.ToolBarList[x] == "Open Imported Module":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_OPEN_IMPORTED_MODULE, x))
            elif frame.ToolBarList[x] == "Reload File":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_RELOAD, x))
            elif frame.ToolBarList[x] == "Close":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CLOSE, x))
            elif frame.ToolBarList[x] == "Save":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SAVE, x))
            elif frame.ToolBarList[x] == "Save As":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SAVE_AS, x))
            elif frame.ToolBarList[x] == "Save All Documents":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SAVE_ALL, x))
            elif frame.ToolBarList[x] == "Save Prompt Output To File":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SAVE_PROMPT, x))
            elif frame.ToolBarList[x] == "Restore From Backup":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_RESTORE_FROM_BACKUP, x))
            elif frame.ToolBarList[x] == "Close All Documents":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CLOSE_ALL, x))
            elif frame.ToolBarList[x] == "Close All Other Documents":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CLOSE_ALL_OTHER_TABS, x))
            elif frame.ToolBarList[x] == "Print Setup":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PRINT_SETUP, x))
            elif frame.ToolBarList[x] == "Print File":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PRINT, x))
            elif frame.ToolBarList[x] == "Print Prompt":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PRINTPROMPT, x))
            elif frame.ToolBarList[x] == "Exit":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_EXIT, x))
            elif frame.ToolBarList[x] == "Next Document":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_NEXT_TAB, x))
            elif frame.ToolBarList[x] == "Previous Document":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PREVIOUS_TAB, x))
            elif frame.ToolBarList[x] == "First Document":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIRST_TAB, x))
            elif frame.ToolBarList[x] == "Last Document":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_LAST_TAB, x))
            elif frame.ToolBarList[x] == "Find":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIND, x))
            elif frame.ToolBarList[x] == "Replace":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_REPLACE, x))
            elif frame.ToolBarList[x] == "Find Next":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIND_NEXT, x))
            elif frame.ToolBarList[x] == "Find Previous":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIND_PREVIOUS, x))
            elif frame.ToolBarList[x] == "Insert Regular Expression":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_INSERT_REGEX, x))
            elif frame.ToolBarList[x] == "Insert Separator":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_INSERT_SEPARATOR, x))
            elif frame.ToolBarList[x] == "Go To":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO, x))
            elif frame.ToolBarList[x] == "Go To Block Start":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_BLOCK_START, x))
            elif frame.ToolBarList[x] == "Go To Block End":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_BLOCK_END, x))
            elif frame.ToolBarList[x] == "Go To Class Start":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_CLASS_START, x))
            elif frame.ToolBarList[x] == "Go To Class End":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_CLASS_END, x))
            elif frame.ToolBarList[x] == "Go To Def Start":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_DEF_START, x))
            elif frame.ToolBarList[x] == "Go To Def End":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_GOTO_DEF_END, x))
            elif frame.ToolBarList[x] == "Find And Complete":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIND_AND_COMPLETE, x))
            elif frame.ToolBarList[x] == "Comment":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_COMMENT_REGION, x))
            elif frame.ToolBarList[x] == "UnComment":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_UNCOMMENT_REGION, x))
            elif frame.ToolBarList[x] == "Indent":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_INDENT_REGION, x))
            elif frame.ToolBarList[x] == "Dedent":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_DEDENT_REGION, x))
            elif frame.ToolBarList[x] == "Undo":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_UNDO, x))
            elif frame.ToolBarList[x] == "Redo":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_REDO, x))
            elif frame.ToolBarList[x] == "Uppercase":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_UPPERCASE, x))
            elif frame.ToolBarList[x] == "Lowercase":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_LOWERCASE, x))
            elif frame.ToolBarList[x] == "Find And Complete":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FIND_AND_COMPLETE, x))
            elif frame.ToolBarList[x] == "Copy":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_COPY, x))
            elif frame.ToolBarList[x] == "Cut":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CUT, x))
            elif frame.ToolBarList[x] == "Paste":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PASTE, x))
            elif frame.ToolBarList[x] == "Delete":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_DELETE, x))
            elif frame.ToolBarList[x] == "Select All":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SELECT_ALL, x))
            elif frame.ToolBarList[x] == "Select None":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SELECT_NONE, x))
            elif frame.ToolBarList[x] == "Zoom In":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_ZOOM_IN, x))
            elif frame.ToolBarList[x] == "Zoom Out":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_ZOOM_OUT, x))
            elif frame.ToolBarList[x] == "Toggle Fold":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_TOGGLE_FOLD, x))
            elif frame.ToolBarList[x] == "Fold All":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_FOLD_ALL, x))
            elif frame.ToolBarList[x] == "Expand All":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_EXPAND_ALL, x))
            elif frame.ToolBarList[x] == "Select All":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SELECT_ALL, x))
            elif frame.ToolBarList[x] == "View In Left Panel":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_VIEW_IN_LEFT_PANEL, x))
            elif frame.ToolBarList[x] == "View In Right Panel":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_VIEW_IN_RIGHT_PANEL, x))
            elif frame.ToolBarList[x] == "View In Top Panel":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_VIEW_IN_TOP_PANEL, x))
            elif frame.ToolBarList[x] == "Preferences":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PREFS, x))
            elif frame.ToolBarList[x] == "Customize Shortcuts":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SHORTCUTS, x))
            elif frame.ToolBarList[x] == "Customize Pop Up Menu":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_POPUP, x))
            elif frame.ToolBarList[x] == "Customize ToolBar":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CUSTOMIZE_TOOLBAR, x))
            elif frame.ToolBarList[x] == "Toggle Prompt":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_TOGGLE_PROMPT, x))
            elif frame.ToolBarList[x] == "Toggle View Whitespace":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_TOGGLE_VIEWWHITESPACE, x))
            elif frame.ToolBarList[x] == "Run":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_RUN, x))
            elif frame.ToolBarList[x] == "Set Arguments":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_SET_ARGS, x))
            elif frame.ToolBarList[x] == "Python":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PYTHON, x))
            elif frame.ToolBarList[x] == "End":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_END, x))
            elif frame.ToolBarList[x] == "Check Syntax":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CHECK_SYNTAX, x))
            elif frame.ToolBarList[x] == "Close Prompt":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_CLOSE_PROMPT, x))
            elif frame.ToolBarList[x] == "Help":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_HELP, x))
            elif frame.ToolBarList[x] == "View Python Docs":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_PYTHON_DOCS, x))
            elif frame.ToolBarList[x] == "View WxWidgets Docs":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_WXWIDGETS_DOCS, x))
            elif frame.ToolBarList[x] == "View Regular Expression Howto":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_REHOWTO_DOCS, x))
            elif frame.ToolBarList[x] == "Import All":
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_IMPORT_ALL, x))
            elif frame.ToolBarList[x].find("<Plugin>:") > -1:
                try:
                    title = frame.ToolBarList[x][frame.ToolBarList[x].find("<Plugin>:")+9:]
                    ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_OTHER+x, x, title))
                    frame.Bind(wx.EVT_MENU, frame.OnToolBar, id=frame.ID_OTHER+x)
                except:
                    pass
            else:
                ToolBarIdList.append(AddandReturn(frame, bitmapFileArray, frame.ID_OTHER+x, x))
                frame.Bind(wx.EVT_MENU, frame.OnToolBar, id=frame.ID_OTHER+x)
            x = x + 1

        frame.toolbar.AddSeparator()

        frame.toolbar.Realize()
    except:
        sScrolledMessageDialog.ShowMessage(frame, "Error Loading the ToolBar.", "Seer Error")
        return []
    return ToolBarIdList


