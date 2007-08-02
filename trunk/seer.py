#!/usr/bin/env python

import sys, os, shutil, re, string, traceback
import wx, wx.stc
import  wx.lib.dialogs
import sScrolledMessageDialog
from sNotebook import *
from sText import sText
from sPrompt import sPrompt
from sPrinter import sPrinter
from sFindReplaceDialog import sFindReplaceDialog
from sBookmarksMenu import sBookmarksMenu
from sScriptMenu import sScriptMenu
from sPluginMenu import sPluginConfigureMenu, sPluginIndexMenu, sPluginAboutMenu, sPluginHelpMenu, sPluginPreferencesMenu
import sGetBlockInfo
import sSourceBrowserGoTo
import sFileDialog
import sPrefsFile
from sPreferences import sPreferences
import sShortcutsFile
import sShortcuts
import sToolBarFile
import sTabNanny
from sSourceBrowser import sSourceBrowserPanel
import sEncoding
from sStyleDialog import sSeparatorDialog
from sMenu import sMenu
import pydoc
import tempfile


#*******************************************************************************************************

class sObject(wx.Object):
    def __init__(self):
        #wx.Object.__init__(self)
        pass

    def VariableExists(self, varname):
        try:
            eval("self." + varname)
        except:
            return False
        return True

#*******************************************************************************************************

class sFrame(wx.Frame):
    def __init__(self, parent, id, title):

        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(680, 480), name="Seer")

        self.preferencesdirectory = ""

        #Preferences Directory:
        self.invokeuserpreferencespath = False
        if len(sys.argv) > 1:
            x = 0
            for a in sys.argv:
                if a.find('--preferencesbasepath=') == 0:
                    self.invokeuserpreferencespath = True
                    self.preferencesdirectory  = os.path.expanduser(a[22:])
                    if not os.path.exists(self.preferencesdirectory):
                        wx.MessageBox("Preferences Directory: '%s' does not exist!" % self.preferencesdirectory,
                                      "Creating Directory!", wx.ICON_INFORMATION)
                        os.makedirs(self.preferencesdirectory)
                    del sys.argv[x]
                    x -= 1
                x += 1

        self.InitializeConstants()

        self.viewinpaneltarget = 0

        self.lastprogargs = ""

        self.sScript = sObject()
        self.sPlugins = sObject()

        #Sets all image handlers.  Seer uses png, jpg, gif.
        #backward compatibility
        wx.InitAllImageHandlers()

        self.Printer = sPrinter(self)

        #Regex Line Endings:
        self.relewin = re.compile('\r\n', re.M)
        self.releunix = re.compile('[^\r]\n', re.M)
        self.relemac = re.compile('\re[^\n]', re.M)

        self.FormatMacReTarget = re.compile('((?<!\r)\n)|(\r\n)', re.M)
        self.FormatUnixReTarget = re.compile('(\r\n)|(\r(?!\n))', re.M)
        self.FormatWinReTarget = re.compile('((?<!\r)\n)|(\r(?!\n))', re.M)

        self.rechecksyntax = re.compile('line \d+', re.M)

        #Find/Replace

        self.FindHistory = []
        self.ReplaceHistory = []

        self.FindInFilesHistory = []
        self.ReplaceInFilesHistory = []

        self.FindOptions = []
        self.ReplaceOptions = []

        #Used for current directory with open/save
        self.ddirectory = ""

        self.stcshortcutlist = sShortcutsFile.GetSTCShortcutList()

        self.programdirectory = os.path.dirname(os.path.abspath(sys.argv[0])).replace("\\", "/")

        #Preferences


        self.prefs = sPreferences(self.PLATFORM_IS_WIN, self.programdirectory)
        self.prefsfile = self.preferencesdirectory + "/preferences.dat"

        self.LoadPreferences()

        #Set and check all relevant directories
        self.SetSeerDirectories()

        #File Types
        self.setupfiletypeextensions()

        WindowWidth = 640
        WindowHeight = 480
        if self.prefs.rememberwindowsizeandposition:
            if os.path.exists(self.datdirectory + "/seer.sizeandposition.dat"):
                try:
                    f = file(self.datdirectory + "/seer.sizeandposition.dat", 'r')
                    text = f.read()
                    WindowWidth, WindowHeight, WindowX, WindowY = map(int, text.split('\n'))
                    f.close()
                    self.SetSize((WindowWidth, WindowHeight))
                    self.Move(wx.Point(WindowX, WindowY))
                except:
                    self.ShowMessage('Error Loading Window Size.  The file "%s" may be corrupt.' % self.preferencesdirectory +
                                     "/seer.sizeandposition.dat", 'Error')

        #Default position is for "General" preferences.
        self.prefdialogposition = 0

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.BitmapFromImage(wx.Image(self.bitmapdirectory + "/seer.png", wx.BITMAP_TYPE_PNG)))
        self.SetIcon(icon)

        self.txtDocumentArray = []
        self.txtPromptArray = []

        self.mainpanel = sMainPanel(self, -1)

        self.mainpanel.RememberPanelSizes()

        self.SourceBrowser = None
        self.Debugger = None

        #Colour:
        self.SetBackgroundColour(self.mainpanel.GetBackgroundColour())

        self.documentnotebook = sDocNotebook(self.mainpanel.document, -1)
        self.promptnotebook = sPromptNotebook(self.mainpanel.prompt, -1)

        self.documentnotebook.AddPage(sPanel(self.documentnotebook, self.ID_APP), "Untitled 1")
        self.promptnotebook.AddPage(sPanel(self.promptnotebook, self.ID_APP), "Prompt")

        self.currentpage = self.documentnotebook.GetPage(0)
        self.currentprompt = self.promptnotebook.GetPage(0)

        self.txtDocument = sText(self.currentpage, self.ID_DOCUMENT_BASE, self)
        self.currentpage.SetSTC(self.txtDocument)
        self.txtPrompt = sPrompt(self.currentprompt, self.ID_PROMPT_BASE, self)
        self.currentprompt.SetSTC(self.txtPrompt)

        self.txtDocument.SetTargetPosition(0)
        self.txtDocument.untitlednumber = 1

        self.documentnotebook.SetPageImage(0, 0)
        self.promptnotebook.SetPageImage(0, 2)

        #Pop Up Menu

        self.popupmenulist = []

        self.LoadPopUpFile()

        #Position in the Arrays Below:
        self.docPosition = 0
        self.promptPosition = 0

        self.txtDocumentArray.append(self.txtDocument)
        self.txtPromptArray.append(self.txtPrompt)
        self.lastprogargsArray = [self.lastprogargs]

        #Shortcuts

        self.STCShortcuts = sShortcutsFile.GetDefaultSTCShortcuts()
        self.STCShortcutNames = sShortcutsFile.GetSTCShortcutList()
        self.STCShortcutsArgumentArray = sShortcuts.GetSTCCommandList()

        self.Shortcuts, self.ShortcutsIgnoreString = sShortcutsFile.GetDefaultShortcuts()
        self.ShortcutNames = sShortcutsFile.GetShortcutList()

        self.ShortcutsActionArray = []
        self.ShortcutsArgumentsArray = []

        #sScript Shortcuts

        self.sScriptShortcuts = []
        self.sScriptShortcutNames = []

        #Plugins
        self.LoadedPlugins = []
        self.PluginModules = []

        #Plugin Events

        self.EVT_SEER_DOCUMENT_CHANGED = 0
        self.EVT_SEER_FILE_OPENING = 1
        self.EVT_SEER_FILE_OPENED = 2
        self.EVT_SEER_FILE_SAVING = 3
        self.EVT_SEER_FILE_SAVED = 4
        self.EVT_SEER_FILE_CLOSING = 5
        self.EVT_SEER_FILE_CLOSED = 6
        self.EVT_SEER_NEW = 7
        self.EVT_SEER_NEW_PROMPT = 8

        #Plugin Arrays:

        self.spyevents = []

        self.PluginShortcutsLoadedArray = []

        self.PluginShortcutFunctionNames = []
        self.PluginShortcutFunctions = []

        self.PluginShortcutNames = []
        self.PluginShortcuts = []
        self.PluginAction = []

        self.PluginPopUpMenuNames = []
        self.PluginPopUpMenuLabels = []
        self.PluginPopUpMenuFunctions = []

        self.PluginToolBarLabels = []
        self.PluginToolBarIconFiles16 = []
        self.PluginToolBarIconFiles24 = []
        self.PluginToolBarFunctions = []

        #Load Shortcuts

        self.STCUseDefault = 1
        self.ShortcutsUseDefault = 1

        self.LoadShortcuts()

        #Shortcuts
        sShortcuts.SetSTCShortcuts(self.txtPrompt, self.STCShortcuts, self.STCUseDefault)
        self.STCShortcuts = sShortcuts.SetSTCShortcuts(self.txtDocument, self.STCShortcuts, self.STCUseDefault)
        self.Shortcuts, self.ShortcutsActionArray, self.ShortcutsArgumentsArray = sShortcuts.SetShortcuts(self, self.Shortcuts, self.ShortcutNames, self.ShortcutsUseDefault)

        #Sizer
        self.bSizer = wx.BoxSizer(wx.VERTICAL)

        self.windowArray = []

        self.recentfiles = []

        self.LoadRecentFiles()

        self.retrailingwhitespace = re.compile('(?<=\S)[ \t]+$', re.MULTILINE)

        #Compile Regular Expressions for Open Import:
        self.reimport = re.compile('^\s*?import\s+?.*?$', re.M)
        self.refromimport = re.compile('^\s*?from\s+?.*?import.*?$', re.M)

        #edited by seer
        if self.prefs.defaultdirectory:
            self.ddirectory = self.prefs.defaultdirectory
        else:
            #add limodou 2004/04/17
            #if defaultdirectory is empty, then use the last recently file's dir
            if self.recentfiles:
                self.ddirectory = os.path.dirname(self.recentfiles[0])
            #end limodou
            else:
                self.ddirectory = self.programdirectory

        try:
            os.chdir(self.ddirectory)
        except:
            self.ShowMessage('Error Changing to Default Directory: "%s"' % (self.ddirectory), 'Preferences Error')
            self.ddirectory = self.programdirectory
            os.chdir(self.ddirectory)

        #AB: Removed: it will be called in CreateMenus
        #self.sscriptmenu = sScriptMenu(self)

        self.txtDocument.OnModified(None)

        #sScript Shortcuts
        #AB: Removed: it will be called in CreateMenus
        #self.sScriptShortcutsAction = self.sscriptmenu.OnScript

        self.hasToolBar = False

                #Status Bar

        self.CreateStatusBar()

        self.GetStatusBar().SetFieldsCount(3)

        #First field is hidden, to absorb wxMenuHighlight events from the menu and toolbar.
        self.GetStatusBar().SetStatusWidths([-0, -6, -4])

        self.CreateMenus()
        #Sizer

        self.bSizer.Add(self.mainpanel, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.bSizer)



        self.UpdateMenuAndToolbar()

        self.Bind(wx.EVT_MENU,  self.OnNew, id=self.ID_NEW)
        self.Bind(wx.EVT_MENU,  self.OnOpen, id=self.ID_OPEN)
        self.Bind(wx.EVT_MENU,  self.OnOpenImportedModule, id=self.ID_OPEN_IMPORTED_MODULE)

        self.Bind(wx.EVT_MENU,  self.OnClose, id=self.ID_CLOSE)
        self.Bind(wx.EVT_MENU,  self.OnCloseAllDocuments, id=self.ID_CLOSE_ALL)
        self.Bind(wx.EVT_MENU,  self.OnCloseAllOtherDocuments, id=self.ID_CLOSE_ALL_OTHER_DOCUMENTS)

        self.Bind(wx.EVT_MENU,  self.OnReload, id=self.ID_RELOAD)
        self.Bind(wx.EVT_MENU,  self.OnRestoreFromBackup, id=self.ID_RESTORE_FROM_BACKUP)
        self.Bind(wx.EVT_MENU,  self.OnClearRecent, id=self.ID_CLEAR_RECENT)
        self.Bind(wx.EVT_MENU,  self.OnSave, id=self.ID_SAVE)
        self.Bind(wx.EVT_MENU,  self.OnSaveAs, id=self.ID_SAVE_AS)
        self.Bind(wx.EVT_MENU,  self.OnSaveCopy, id=self.ID_SAVE_COPY)
        self.Bind(wx.EVT_MENU,  self.OnSaveAll, id=self.ID_SAVE_ALL)
        self.Bind(wx.EVT_MENU,  self.OnSavePrompt, id=self.ID_SAVE_PROMPT)
        self.Bind(wx.EVT_MENU,  self.OnPrintSetup, id=self.ID_PRINT_SETUP)
        self.Bind(wx.EVT_MENU,  self.OnPrint, id=self.ID_PRINT)
        self.Bind(wx.EVT_MENU,  self.OnPrintPrompt, id=self.ID_PRINTPROMPT)
        self.Bind(wx.EVT_MENU,  self.OnExit, id=self.ID_EXIT)

        self.Bind(wx.EVT_MENU,  self.OnMenuFind, id=self.ID_FIND)
        self.Bind(wx.EVT_MENU,  self.OnMenuFindNext, id=self.ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU,  self.OnMenuFindPrevious, id=self.ID_FIND_PREVIOUS)
        self.Bind(wx.EVT_MENU,  self.OnMenuReplace, id=self.ID_REPLACE)

        self.Bind(wx.EVT_MENU,  self.OnInsertSeparator, id=self.ID_INSERT_SEPARATOR)
        self.Bind(wx.EVT_MENU,  self.OnInsertRegEx, id=self.ID_INSERT_REGEX)

        self.Bind(wx.EVT_MENU,  self.OnSelectAll, id=self.ID_SELECT_ALL)

        self.Bind(wx.EVT_MENU,  self.OnCommentRegion, id=self.ID_COMMENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnUnCommentRegion, id=self.ID_UNCOMMENT_REGION)

        self.Bind(wx.EVT_MENU,  self.OnIndentRegion, id=self.ID_INDENT_REGION)
        self.Bind(wx.EVT_MENU,  self.OnDedentRegion, id=self.ID_DEDENT_REGION)

        self.Bind(wx.EVT_MENU,  self.OnCheckIndentation, id=self.ID_CHECK_INDENTATION)
        self.Bind(wx.EVT_MENU,  self.OnCleanUpTabs, id=self.ID_CLEAN_UP_TABS)
        self.Bind(wx.EVT_MENU,  self.OnCleanUpSpaces, id=self.ID_CLEAN_UP_SPACES)

        self.Bind(wx.EVT_MENU,  self.OnFormatUnixMode, id=self.ID_UNIXMODE)
        self.Bind(wx.EVT_MENU,  self.OnFormatWinMode, id=self.ID_WINMODE)
        self.Bind(wx.EVT_MENU,  self.OnFormatMacMode, id=self.ID_MACMODE)

        self.Bind(wx.EVT_MENU,  self.OnFindAndComplete, id=self.ID_FIND_AND_COMPLETE)

        self.Bind(wx.EVT_MENU,  self.OnUppercase, id=self.ID_UPPERCASE)
        self.Bind(wx.EVT_MENU,  self.OnLowercase, id=self.ID_LOWERCASE)
        self.Bind(wx.EVT_MENU,  self.OnUndo, id=self.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=self.ID_REDO)

        self.Bind(wx.EVT_MENU,  self.OnGoTo, id=self.ID_GOTO)

        self.Bind(wx.EVT_MENU,  self.OnGoToBlockStart, id=self.ID_GOTO_BLOCK_START)
        self.Bind(wx.EVT_MENU,  self.OnGoToBlockEnd, id=self.ID_GOTO_BLOCK_END)
        self.Bind(wx.EVT_MENU,  self.OnGoToClassStart, id=self.ID_GOTO_CLASS_START)
        self.Bind(wx.EVT_MENU,  self.OnGoToClassEnd, id=self.ID_GOTO_CLASS_END)
        self.Bind(wx.EVT_MENU,  self.OnGoToDefStart, id=self.ID_GOTO_DEF_START)
        self.Bind(wx.EVT_MENU,  self.OnGoToDefEnd, id=self.ID_GOTO_DEF_END)

        self.Bind(wx.EVT_MENU,  self.OnSourceBrowserGoTo, id=self.ID_SOURCEBROWSER_GOTO)

        self.Bind(wx.EVT_MENU,  self.OnZoomIn, id=self.ID_ZOOM_IN)
        self.Bind(wx.EVT_MENU,  self.OnZoomOut, id=self.ID_ZOOM_OUT)

        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingPython, id=self.ID_HIGHLIGHT_PYTHON)
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingCPP, id=self.ID_HIGHLIGHT_CPP)
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingHTML, id=self.ID_HIGHLIGHT_HTML)
        self.Bind(wx.EVT_MENU,  self.OnSyntaxHighlightingText, id=self.ID_HIGHLIGHT_PLAIN_TEXT)

        self.Bind(wx.EVT_MENU,  self.OnToggleFold, id=self.ID_TOGGLE_FOLD)
        self.Bind(wx.EVT_MENU,  self.OnFoldAll, id=self.ID_FOLD_ALL)
        self.Bind(wx.EVT_MENU,  self.OnExpandAll, id=self.ID_EXPAND_ALL)

        self.Bind(wx.EVT_MENU,  self.OnViewInLeftPanel, id=self.ID_VIEW_IN_LEFT_PANEL)
        self.Bind(wx.EVT_MENU,  self.OnViewInRightPanel, id=self.ID_VIEW_IN_RIGHT_PANEL)
        self.Bind(wx.EVT_MENU,  self.OnViewInTopPanel, id=self.ID_VIEW_IN_TOP_PANEL)

        self.Bind(wx.EVT_MENU,  self.OnToggleSourceBrowser, id=self.ID_TOGGLE_SOURCEBROWSER)
        self.Bind(wx.EVT_MENU,  self.OnToggleViewWhiteSpace, id=self.ID_TOGGLE_VIEWWHITESPACE)
        self.Bind(wx.EVT_MENU,  self.OnTogglePrompt, id=self.ID_TOGGLE_PROMPT)

        self.Bind(wx.EVT_MENU,  self.OnRun, id=self.ID_RUN)
        self.Bind(wx.EVT_MENU,  self.OnSetArgs, id=self.ID_SET_ARGS)
        self.Bind(wx.EVT_MENU,  self.OnPython, id=self.ID_PYTHON)
        self.Bind(wx.EVT_MENU,  self.OnEnd, id=self.ID_END)
        self.Bind(wx.EVT_MENU,  self.OnCheckSyntax, id=self.ID_CHECK_SYNTAX)
        self.Bind(wx.EVT_MENU,  self.OnClosePrompt, id=self.ID_CLOSE_PROMPT)

        self.Bind(wx.EVT_MENU,  self.OnPrefs, id=self.ID_PREFS)
        self.Bind(wx.EVT_MENU,  self.OnCustomizeShortcuts, id=self.ID_SHORTCUTS)
        self.Bind(wx.EVT_MENU,  self.OnCustomizePopUpMenu, id=self.ID_POPUP)
        self.Bind(wx.EVT_MENU,  self.OnCustomizeToolBar, id=self.ID_CUSTOMIZE_TOOLBAR)
        self.Bind(wx.EVT_MENU,  self.OnEditBookmarks, id=self.ID_EDIT_BOOKMARKS)
        self.Bind(wx.EVT_MENU,  self.OnEditScriptMenu, id=self.ID_EDIT_SCRIPT_MENU)

        self.Bind(wx.EVT_MENU,  self.OnViewAbout, id=self.ID_ABOUT)
        self.Bind(wx.EVT_MENU,  self.OnViewHelp, id=self.ID_HELP)
        self.Bind(wx.EVT_MENU,  self.OnViewPythonDocs, id=self.ID_PYTHON_DOCS)
        self.Bind(wx.EVT_MENU,  self.OnViewWxWidgetsDocs, id=self.ID_WXWIDGETS_DOCS)
        self.Bind(wx.EVT_MENU,  self.OnViewREHowtoDocs, id=self.ID_REHOWTO_DOCS)

        self.Bind(wx.EVT_MENU, self.DoBuiltIn, id=self.ID_COPY)
        self.Bind(wx.EVT_MENU, self.DoBuiltIn, id=self.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.DoBuiltIn, id=self.ID_CUT)
        self.Bind(wx.EVT_MENU, self.DoBuiltIn, id=self.ID_DELETE)

        self.Bind(wx.EVT_MENU, self.OnSelectDocumentNext, id=self.ID_NEXT_DOCUMENT)
        self.Bind(wx.EVT_MENU, self.OnSelectDocumentPrevious, id=self.ID_PREVIOUS_DOCUMENT)
        self.Bind(wx.EVT_MENU, self.OnSelectDocumentFirst, id=self.ID_FIRST_DOCUMENT)
        self.Bind(wx.EVT_MENU, self.OnSelectDocumentLast, id=self.ID_LAST_DOCUMENT)

        # add import all button
        self.Bind(wx.EVT_TOOL, self.OnImportAll, id=self.ID_IMPORT_ALL)
        # end import all
        # add pydoc menu items
        self.Bind(wx.EVT_MENU, self.OnPyDocAll, id=self.ID_PYDOC_ALL)
        self.Bind(wx.EVT_MENU, self.OnPyDocCurrent, id=self.ID_PYDOC_CURR)
        self.Bind(wx.EVT_MENU, self.OnViewPyDoc, id=self.ID_VIEW_PYDOC)
        #end pydoc

        self.txtDocument.SetupPrefsDocument()

        self.txtDocument.SetFocus()

        self.txtDocument.OnPositionChanged(None)

        self.txtPrompt.SetReadOnly(1)

        self.txtPrompt.SetupPrefsPrompt()

        #Arguments To Program
        if len(sys.argv) > 1:
            f = sys.argv[1]
            if self.PLATFORM_IS_WIN:
                f = f.replace("\\", "/")
            if not os.path.exists(f):
                if self.Ask('"' + f + '" Does not exist.  Create?', 'File Does Not Exist'):
                    try:
                        fobj = file(f, 'wb')
                        fobj.close()
                    except:
                        self.ShowMessage('Error Creating "' + f + '"')
            if os.path.exists(f):
                self.OpenFile(f, False)
                self.txtDocument.OnModified(None)
                x = 2
                l = len(sys.argv)
                while x < l:
                    f = sys.argv[x]
                    if self.PLATFORM_IS_WIN:
                        f = f.replace("\\", "/")
                    self.OpenFile(f, True)
                    self.txtDocument.OnModified(None)
                    x = x + 1

        #Load SourceBrowser:
        if self.prefs.sourcebrowserisvisible:
            self.ShowSourceBrowser()

        self.Bind(wx.EVT_END_PROCESS,  self.OnProcessEnded, id=-1)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CLOSE, self.OnCloseW)

        self.LoadPlugins()

    def Append_Menu(self, menu, id, s, LaunchesDialog = False, AmpersandAt = -1, absolutelabel=''):
        label = s
        item = wx.MenuItem(menu, id, label, label)
        menuiconfile = self.bitmapdirectory + "/16/" + s + ".png"
        if os.path.exists(menuiconfile):
            #try:
            img = wx.Image(menuiconfile, wx.BITMAP_TYPE_PNG)
            bmp = wx.BitmapFromImage(img)
            #except?
        #else:
            #bmp = wx.EmptyBitmap(16, 16) #width the same, background colour frame colour, so alignment is assured
            item.SetBitmap(bmp)
        #item.SetBitmap(bmp)
        menu.AppendItem(item)

    def AddKeyEvent(self, function, Keycode, Control=0, Shift=0, Alt=0, Meta=0):
        if Keycode == -1:
            return

        shortcut = sShortcuts.BuildShortcutString(Keycode, Control, Shift, Alt, Meta)

        self.PluginShortcutNames.append('Plugin')
        self.PluginShortcuts.append(shortcut)
        self.PluginAction.append(function)

    def AddPluginFunction(self, plugin, label, function):
        self.PluginShortcutFunctionNames.append(plugin + ":" + label)
        self.PluginShortcutFunctions.append(function)

        self.PluginPopUpMenuNames.append(plugin)
        self.PluginPopUpMenuLabels.append(label)
        self.PluginPopUpMenuFunctions.append(function)

        self.PluginToolBarLabels.append("<Plugin>:"+label)
        self.PluginToolBarFunctions.append(function)

    def AddPluginIcon(self, name, location16, location24):
        ctbfile = self.datdirectory + "/toolbar.custom.icons.dat"
        if not os.path.exists(ctbfile):
            f = file(ctbfile, 'w')
            f.write('\n')
            f.close()
        f = file(ctbfile, 'r')
        lines = f.read().split('\n')
        f.close()
        name = "<Plugin>:" + name
        f = file(self.datdirectory + "/toolbar.custom.icons.dat", 'w')
        for line in lines:
            if line:
                currentname = sPrefsFile.ExtractPreferenceFromText(line, "Name")
                if currentname != name:
                    f.write(line + '\n')
        f.write("<Name>" + name + "</Name><16>" + location16 + "</16><24>" + \
        location24 + "</24>\n")
        f.close()

    def AddPluginShortcutFunction(self, plugin, label, function):
        self.PluginShortcutFunctionNames.append(plugin + ":" + label)
        self.PluginShortcutFunctions.append(function)

    def AddPluginPopUpMenuFunction(self, plugin, label, function):
        self.PluginPopUpMenuNames.append(plugin)
        self.PluginPopUpMenuLabels.append(label)
        self.PluginPopUpMenuFunctions.append(function)

    def AddPluginToolBarFunction(self, label, function):
        self.PluginToolBarLabels.append("<Plugin>:"+label)
        self.PluginToolBarFunctions.append(function)

    def Ask(self, question, title='Seer'):
        answer = wx.MessageBox(question, title, wx.YES_NO | wx.ICON_QUESTION)
        return (answer == wx.YES)

    def checkiffileisCPP(self, filename):
        return self.refiletypeiscpp.search(filename) is not None

    def checkiffileisHTML(self, filename):
        return self.refiletypeishtml.search(filename) is not None

    def checkiffileisPlainText(self, filename):
        return self.refiletypeistxt.search(filename) is not None

    def checkiffileisPython(self, filename):
        return self.refiletypeispy.search(filename) is not None

    def CheckSyntax(self, docnumber=-1):
        if docnumber == -1:
            docnumber = self.docPosition
        fn = self.txtDocumentArray[docnumber].GetFilename()
        if not self.txtDocumentArray[docnumber].filename:
            self.ShowMessage('Cannot Run Check on "%s"' % fn, 'Cannot Check Untitled File')
            return False
        #Check Syntax First
        try:
            encoding = self.txtDocumentArray[docnumber].GetEncoding()
            ctext = sEncoding.DecodeText(self, self.txtDocumentArray[docnumber].GetText(), encoding)
            ctext = ctext.replace('\r\n', '\n').replace('\r', '\n')
            compile(ctext, fn, 'exec')
        except Exception, e:
            excstr = str(e)
            result = self.rechecksyntax.search(excstr)
            if result is not None:
                num = result.group()[5:].strip()
                try:
                    n = int(num) - 1
                    self.setDocumentTo(docnumber)
                    self.txtDocument.ScrollToLine(n)
                    self.txtDocument.GotoLine(n)
                    self.ShowMessage('compile:\n' + excstr)
                    self.txtDocument.SetSTCFocus(True)
                    self.txtDocument.SetFocus()
                    #Stop the function here if something is found.
                    return False
                except:
                    self.ShowMessage('Line Number Error:\n\n'+excstr, 'SyntaxError')
            else:
                self.ShowMessage('No Line Number Found:\n\n' + excstr, 'Syntax Error')

        #Now Check Indentation
        result = sTabNanny.Check(fn)
        results = result.split()
        if len(results) > 1:
            num = results[1]
            try:
                n = int(num) - 1
                self.setDocumentTo(docnumber)
                self.txtDocument.ScrollToLine(n)
                self.txtDocument.GotoLine(n)
                self.ShowMessage('tabnanny:\n' + result)
                self.txtDocument.SetSTCFocus(True)
                self.txtDocument.SetFocus()
                return False
            except:
                self.ShowMessage('Line Number Error:\n\n'+result, 'TabNanny Trouble')

        return True

    def CreateRecentFileMenu(self):
        x = 0
        numfiles = len(self.recentfiles)
        while x < numfiles:
            self.recentmenu.Append(self.ID_RECENT_FILES_BASE+x, self.recentfiles[x])
            self.Bind(wx.EVT_MENU,  self.OnOpenRecentFile, id=self.ID_RECENT_FILES_BASE+x)
            x = x + 1

    def DestroyDocument(self):
        self.txtDocumentArray.pop(self.docPosition)
        self.lastprogargsArray.pop(self.docPosition)

    def DestroyRecentFileMenu(self):
        #You need to call this function BEFORE you update the list of recent files.
        x = 0
        mnuitems = self.recentmenu.GetMenuItems()
        num = len(mnuitems)
        while x < num:
            self.recentmenu.Remove(self.ID_RECENT_FILES_BASE+x)
            x = x + 1

    def DestroyToolBar(self):
        if self.toolbar is not None:
            x = 0
            toolbarsize = len(self.ToolBarIdList)
            while x < toolbarsize:
                if self.ToolBarIdList[x] == -300:
                    self.toolbar.DeleteToolByPos(0)
                else:
                    self.toolbar.DeleteTool(self.ToolBarIdList[x])
                x = x + 1
            self.toolbar.Destroy()
            self.toolbar = None

    def DoBuiltIn(self, event):
        objid = event.GetId()

        if self.txtPrompt.GetSTCFocus():
            stc = self.txtPrompt
        else:
            stc = self.txtDocument

        if objid == self.ID_COPY:
            stc.CmdKeyExecute(wx.stc.STC_CMD_COPY)
        elif objid == self.ID_PASTE:
            stc.Paste()
        elif objid == self.ID_CUT:
            stc.CmdKeyExecute(wx.stc.STC_CMD_CUT)
        elif objid == self.ID_DELETE:
            stc.CmdKeyExecute(wx.stc.STC_CMD_CLEAR)

    def dynamicsscript(self, event):
        self.sscriptmenu.OnDynamicScript(event)

    def Execute(self, command, statustext = ''):
        if not statustext:
            statustext = "Running Command"
        self.runcommand(command, statustext, command)

    def ExecutePython(self):
        self.txtPrompt.pythonintepreter = 1
        self.ExecuteWithPython('', 'Running Python Interpreter', '-i', 'Python')
        i = self.promptPosition
        try:
            wx.Yield()
        except:
            pass
        #workaround by Dunderhead.
        if self.PLATFORM_IS_WIN:
            self.txtPromptArray[i]._waitforoutput('>>>')
        #self.txtPromptArray[i]._waitforoutput('>>>')
        self.txtPromptArray[i].ExecuteCommands(self.prefs.promptstartupscript)

    def ExecuteWithPython(self, command = '', statustext = '', pythonargs='', pagetext='Python'):
        commandstring = string.join([' -u', pythonargs, self.prefs.pythonargs, command], ' ').rstrip()
        if self.PLATFORM_IS_WIN:
            self.runcommand((self.pythexecw + commandstring), statustext, pagetext)
        else:
            self.runcommand((self.pythexec + commandstring), statustext, pagetext)

    def GetActiveSTC(self):
        if self.txtPrompt.GetSTCFocus():
            return self.txtPrompt
        else:
            return self.txtDocument

    def GetAlreadyOpen(self):
        def _get_filename(x):
            return x.filename
        return map(_get_filename, self.txtDocumentArray)

    def getfileextensionstring(self, index):
        thelist = self.prefs.extensions[index].split(',')

        thestring = ''

        for t in thelist:
            thestring += '(\.' + t.strip() + '$)|'

        return thestring[:-1]

    def GetFileName(self):
        return self.txtDocument.filename

    def getmenulabel(self, label, LaunchesDialog=False, AmpersandAt=-1, absolutelabel=''):

        shortcuttext = ''

        if label in self.ShortcutNames:
            i = self.ShortcutNames.index(label)
            shortcuttext = sShortcuts.GetShortcutLabel(self.Shortcuts[i])
        elif label in self.STCShortcutNames:
            i = self.STCShortcutNames.index(label)
            shortcuttext = sShortcuts.GetShortcutLabel(self.STCShortcuts[i])

        if absolutelabel:
            label = absolutelabel

        else:

            if (AmpersandAt > -1) and (AmpersandAt < len(label)):
                label = label[:AmpersandAt] + '&' + label[AmpersandAt:]

            if LaunchesDialog:
                label += '...'

        if len(shortcuttext) > 1:
            return label + '\t' + shortcuttext
        return label

    def GetNewId(self):
        return 10000 + wx.NewId()

    #Begin Backwards Compatibility
    def GetPluginDirectory(self):
        return self.pluginsdirectory

    def GetPluginsDirectory(self):
        return self.GetPluginDirectory()
    #End Backwards Compatibility

    def GetPluginLabels(self, filename, doNotAppend = False):
        try:
            f = file(filename, 'r')
            text = f.read()
            f.close()
        except:
            self.ShowMessage('File error with: "' + filename + '".', "ERROR")
            return []

        rePopUpMenu = re.compile(r'^\s*?sFrame\.AddPluginFunction\(.*\)', re.MULTILINE)

        allPopUps = rePopUpMenu.findall(text)

        PopUpArray = []

        for s in allPopUps:
            #From the Left most '('
            start = s.find('(')
            #To the Right most ')'
            end = s.rfind(')')

            if (start > -1) and (end > -1):
                s = s[start+1:end]
                i = s.find(',')
                e = i + 1 + s[i+1:].find(',')
                arglabel = s[i+1:e].strip().strip('"')
                if doNotAppend:
                    PopUpArray.append(arglabel)
                else:
                    PopUpArray.append("<Plugin>:"+arglabel)

        return PopUpArray

    def GetPluginMenuLabel(self, plugin, functionlabel, menulabel=''):
        shortcuttext = ''

        searchlabel = plugin + ':' + functionlabel

        if searchlabel in self.PluginShortcutNames:
            i = self.PluginShortcutNames.index(searchlabel)
            shortcuttext = sShortcuts.GetShortcutLabel(self.PluginShortcuts[i])

        if not menulabel:
            menulabel = functionlabel

        if len(shortcuttext) > 1:
            return menulabel + '\t' + shortcuttext

        return menulabel

    def GetPreference(self, pref, key=None):
        if key is not None:
            return self.prefs[pref][key]
        else:
            return self.prefs[pref]

    def WriteUserPreferencesDirectoryFile(self):
        if not self.invokeuserpreferencespath:
            f = open(self.preferencesdirectoryfile, 'w')
            f.write(self.preferencesdirectory)
            f.close()

    def InitializeConstants(self):
        #Constant messages for file format checking.
        self.FFMESSAGE = ["Unix Mode ('\\n')", "DOS/Windows Mode ('\\r\\n')", "Mac Mode ('\\r')"]
        self.TABMESSAGE = ['Spaces', 'Mixed', 'Tabs', 'None']

        self.ID_DOCUMENT_BASE = 50
        self.ID_PROMPT_BASE = 340

        #Application ID Constants
        self.ID_APP = 101
        self.ID_NEW = 102
        self.ID_OPEN = 103
        self.ID_OPEN_IMPORTED_MODULE = 1000
        self.ID_OPEN_RECENT = 104
        self.ID_RELOAD = 105
        self.ID_RESTORE_FROM_BACKUP = 1051
        self.ID_CLOSE = 106
        self.ID_CLOSE_ALL = 6061
        self.ID_CLOSE_ALL_OTHER_DOCUMENTS = 6062
        self.ID_CLEAR_RECENT = 107
        self.ID_SAVE = 108
        self.ID_SAVE_AS = 109
        self.ID_SAVE_COPY = 1092
        self.ID_SAVE_ALL = 1098
        self.ID_SAVE_PROMPT = 1091
        self.ID_PRINT_SETUP = 1010
        self.ID_PRINT = 1011
        self.ID_PRINTPROMPT = 1012
        self.ID_EXIT = 1014
        # define import all id
        self.ID_IMPORT_ALL = self.GetNewId()

        # end import all

        # define pydoc ids
        self.ID_PYDOC_ALL = 1016
        self.ID_PYDOC_CURR = 1017
        self.ID_VIEW_PYDOC = 1018
        # end pydoc

        self.ID_NEXT_DOCUMENT = 801
        self.ID_PREVIOUS_DOCUMENT = 802
        self.ID_FIRST_DOCUMENT = 803
        self.ID_LAST_DOCUMENT = 804
        self.ID_DOCUMENT_NAVIGATION_MENU = 810
        self.ID_DOCUMENTS_BASE = 8000
        self.ID_DOCUMENTS_MENU_BASE = 7950

        self.ID_COPY = 850
        self.ID_PASTE = 851
        self.ID_CUT = 852
        self.ID_DELETE = 853

        self.ID_FIND = 111
        self.ID_FIND_NEXT = 112
        self.ID_FIND_PREVIOUS = 1122
        self.ID_REPLACE = 113
        self.ID_GOTO = 115
        self.ID_GOTO_MENU = 1150
        self.ID_GOTO_BLOCK_START = 1151
        self.ID_GOTO_BLOCK_END = 1152
        self.ID_GOTO_CLASS_START = 1153
        self.ID_GOTO_CLASS_END = 1154
        self.ID_GOTO_DEF_START = 1155
        self.ID_GOTO_DEF_END = 1156

        self.ID_SOURCEBROWSER_GOTO = 1157

        self.ID_SELECT_ALL = 1161

        self.ID_INSERT_REGEX = 1163

        self.ID_INSERT_SEPARATOR = 1164

        self.ID_COMMENT = 1116
        self.ID_COMMENT_REGION = 116
        self.ID_UNCOMMENT_REGION = 117

        self.ID_WHITESPACE = 1118
        self.ID_INDENT_REGION = 118
        self.ID_DEDENT_REGION = 119
        self.ID_CHECK_INDENTATION = 1650

        self.ID_CLEAN_UP_TABS = 1670
        self.ID_CLEAN_UP_SPACES = 1671

        self.ID_FORMATMENU = 2000
        self.ID_UNIXMODE = 2001
        self.ID_WINMODE = 2002
        self.ID_MACMODE = 2003

        self.ID_FIND_AND_COMPLETE = 2071

        self.ID_CASE = 1191
        self.ID_UPPERCASE = 1192
        self.ID_LOWERCASE = 1193

        self.ID_UNDO = 1111
        self.ID_REDO = 1112

        self.ID_ZOOM_IN = 161
        self.ID_ZOOM_OUT = 162
        self.ID_FOLDING = 1610
        self.ID_TOGGLE_FOLD = 1613
        self.ID_FOLD_ALL = 1611
        self.ID_EXPAND_ALL = 1612
        self.ID_TOGGLE_SOURCEBROWSER = 163
        self.ID_TOGGLE_VIEWWHITESPACE = 164
        self.ID_TOGGLE_PROMPT = 165

        self.ID_VIEW_IN_PANEL = 170
        self.ID_VIEW_IN_LEFT_PANEL = 171
        self.ID_VIEW_IN_RIGHT_PANEL = 172
        self.ID_VIEW_IN_TOP_PANEL = 173

        self.ID_VIEW_IN_PANEL_BASE = 1700

        self.ID_HIGHLIGHT = 580

        self.ID_HIGHLIGHT_PYTHON = 585
        self.ID_HIGHLIGHT_CPP = 586
        self.ID_HIGHLIGHT_HTML = 587
        self.ID_HIGHLIGHT_PLAIN_TEXT = 589

        self.ID_RUN = 121
        self.ID_SET_ARGS = 122
        self.ID_PYTHON = 123
        self.ID_END = 125
        self.ID_CLOSE_PROMPT = 1250
        self.ID_CHECK_SYNTAX = 126

        self.ID_PREFS = 131
        self.ID_SHORTCUTS = 133
        self.ID_POPUP = 134
        self.ID_CUSTOMIZE_TOOLBAR = 135

        self.ID_CONFIGURE_PLUGINS = 4005
        self.ID_LOAD_PLUGIN = 4050
        self.ID_PLUGIN_HELP = 4051
        self.ID_PLUGIN_PREFS = 4052
        self.ID_PLUGIN_ABOUT = 4053

        self.ID_EDIT_BOOKMARKS = 301
        self.ID_EDIT_SCRIPT_MENU = 3004

        self.ID_ABOUT = 140
        self.ID_HELP = 141
        self.ID_PYTHON_DOCS = 142
        self.ID_WXWIDGETS_DOCS = 143
        self.ID_REHOWTO_DOCS = 144

        self.ID_OTHER = 9000

        self.ID_RECENT_FILES_BASE = 9930

        self.ID_RECENT_SESSIONS_BASE = 8330

        self.ID_SCRIPT_BASE = 7500

        #STC Shortcut List:

        self.STCCOMMANDLIST = sShortcuts.GetSTCCommandList()

        #System constants

        self.PLATFORM_IS_WIN = (sys.platform == "win32")

        #Thanks to Mark Rees.
        #Thanks to Guillermo Fernandez.
        #Thanks Bjorn Breid

        #Preferences Directory Initial Setup:

        self.userhomedirectory = wx.StandardPaths.Get().GetUserConfigDir().replace('\\', '/')
        if not self.preferencesdirectory:

            self.preferencesdirectory = self.userhomedirectory

            self.preferencesdirectoryprefix = "/.seer"
            if self.PLATFORM_IS_WIN:
                self.preferencesdirectoryprefix = "/seer"
            self.preferencesdirectory += self.preferencesdirectoryprefix
            self.preferencesdirectoryfile = self.preferencesdirectory + "/userpreferencesdirectory.dat"

            if not os.path.exists(self.preferencesdirectory):
                os.mkdir(self.preferencesdirectory)

            if not os.path.exists(self.preferencesdirectoryfile):
                self.WriteUserPreferencesDirectoryFile()

            f = open(self.preferencesdirectoryfile, 'r')
            pth = f.read()
            f.close()

            if os.path.exists (pth):
                self.preferencesdirectory = pth
            else:
                wx.MessageBox("Changing Userpreferences directory to default:\n '%s'" % \
                    self.preferencesdirectory,
                    "Userpreferences Directory not found:",
                    wx.ICON_EXCLAMATION)
                self.WriteUserPreferencesDirectoryFile()

        #backwards compatibility todo remove that later
        self.homedirectory = os.path.expanduser('~')

        if self.PLATFORM_IS_WIN:
            self.pythexec = sys.prefix.replace("\\", "/") + "/python.exe"
            self.pythexecw = sys.prefix.replace("\\", "/") + "/pythonw.exe"
        else:
            self.pythexec = sys.executable

    def InitializePlugin(self, plugin, ShowDialog = True):
        #Check to see if the plugin is already loaded:
        if plugin in self.LoadedPlugins:
            if ShowDialog:
                self.ShowMessage(('"' + plugin + '" has already been loaded.\Seer will not reload this plugin.'), "Plugin Already Loaded")
            return

        #Load the Plugin
        pluginfile = os.path.join (self.pluginsdirectory, plugin + ".py")
        self.LoadedPlugins.append(plugin)
        try:
            exec(compile("import " + plugin, pluginfile, 'exec'))
            exec(compile(plugin + ".Plugin(self)", pluginfile, 'exec'))
            exec(compile('self.PluginModules.append('+plugin+')', pluginfile, 'exec'))
        except:
            self.ShowMessage("Error with: " + plugin + "\nSeer will not load this plugin.", "Plugin Error")

        #Menus
        self.pluginsaboutmenu.AddItem(plugin)
        self.pluginshelpmenu.AddItem(plugin)
        self.pluginsprefsmenu.AddItem(plugin)

    def LoadPlugins(self, plugins_file = ""):
        #todo remove this? is this used? franz 22.03.2007:
        if plugins_file:
            pluginsfile = plugins_file
        else:
            #end todo remove this? is this used? franz 22.03.2007:
            pluginsfile = self.preferencesdirectory  + "/default.idx"
        if os.path.exists(pluginsfile):
            try:
                f = file(pluginsfile, 'rU')
                pluginstoload = [x.strip() for x in f]
                f.close()

                for plugin in pluginstoload:
                    if plugin:
                        self.InitializePlugin(plugin)
            except:
                self.ShowMessage(("Error with: " + pluginsfile + "\nSeer will not load plugins."), "Plugins Error")
        else:
            try:
                f = file(pluginsfile, 'wb')
                #f.write('\n')
                f.close()
            except:
                self.ShowMessage('Error Ceating Default Index for Plugins.\n\nPlugins may not work correctly.', 'Plugins Error')

    def LoadPluginShortcuts(self, plugin):
        if plugin in self.PluginShortcutsLoadedArray:
            return
        self.PluginShortcutsLoadedArray.append(plugin)

        shortcutfile = os.path.join (self.pluginsshortcutsdirectory, plugin + ".shortcuts.dat")
        if not os.path.exists(shortcutfile):
            return
        try:
            shortcuts, names, ignorestring = sShortcutsFile.ReadShortcuts(shortcutfile, 0)
            x = 0
            l = len(shortcuts)
            while x < l:
                shortcut = shortcuts[x]
                try:
                    i = self.PluginShortcutFunctionNames.index(plugin + ":" + names[x])
                    self.PluginAction.append(self.PluginShortcutFunctions[i])
                    self.PluginShortcutNames.append(plugin + ":" + names[x])
                    self.PluginShortcuts.append(shortcut)
                except:
                    pass
                x += 1
        except:
            self.ShowMessage(("Error with: " + plugin + "\nSeer will not load shortcuts for this plugin."), "Plugin Shortcuts Error")


    def LoadPopUpFile(self):
        #check for preferences file in user userpreferencesdirectory
        popupfile = self.datdirectory + "/popupmenu.dat"

        if os.path.exists(popupfile):
            try:
                f = file(popupfile, 'r')
                line = f.readline()
                while len(line) > 0:
                    self.popupmenulist.append(line.rstrip())
                    line = f.readline()
                f.close()
            except:
                self.ShowMessage("Error with: " + popupfile + "\nSeer will use the program defaults.", "Pop Up Menu Error")


    def SetSeerDirectories(self):

        #bitmaps code directory
        self.bitmapdirectory = self.programdirectory + "/bitmaps"
        if not os.path.exists(self.bitmapdirectory):
            self.ShowMessage("Bitmap Directory (" + self.bitmapdirectory + ") does Not Exist.", "Seer Fatal Error")
            sys.exit(1)

        #for backward compatibility (can be removed in the future).
        self.userpreferencesdirectory = self.preferencesdirectory

        #plugins code directory
        if not os.path.exists(self.prefs.pluginsdirectory):
            os.mkdir(self.prefs.pluginsdirectory)

        self.pluginsdirectory = self.prefs.pluginsdirectory
        sys.path.append(self.pluginsdirectory)

        #sscripts code directory
        if not os.path.exists(self.prefs.sscriptsdirectory):
            os.mkdir(self.prefs.sscriptsdirectory)
        self.sscriptsdirectory = self.prefs.sscriptsdirectory

        #dat directory
        self.datdirectory = os.path.join(self.preferencesdirectory, 'dat')
        if not os.path.exists(self.datdirectory):
            os.mkdir(self.datdirectory)

        #shortcuts directory
        self.shortcutsdirectory = os.path.join(self.preferencesdirectory, 'shortcuts')
        if not os.path.exists(self.shortcutsdirectory):
            os.mkdir(self.shortcutsdirectory)

        #plugins directory
        self.pluginsbasepreferencesdir = os.path.join(self.preferencesdirectory, '.plugins')
        if not os.path.exists(self.pluginsbasepreferencesdir):
            os.mkdir(self.pluginsbasepreferencesdir)

        #plugins preferences directory
        self.pluginspreferencesdirectory = os.path.join(self.pluginsbasepreferencesdir, 'preferences')
        if not os.path.exists(self.pluginspreferencesdirectory):
            os.mkdir(self.pluginspreferencesdirectory)

        #plugins shortcuts directory
        self.pluginsshortcutsdirectory = os.path.join(self.pluginsbasepreferencesdir, 'shortcuts')
        if not os.path.exists(self.pluginsshortcutsdirectory):
            os.mkdir(self.pluginsshortcutsdirectory)

        #plugins dat directory
        self.pluginsdatdirectory = os.path.join(self.pluginsbasepreferencesdir, 'dat')
        if not os.path.exists(self.pluginsdatdirectory):
            os.mkdir(self.pluginsdatdirectory)

    def LoadPreferences(self):
        #check for preferences file in user userpreferencesdirectory
        if os.path.exists(self.prefsfile):
            try:
                sPrefsFile.ReadPreferences(self.prefs, self.prefsfile)
            except:
                self.ShowMessage(("Error with: " + prefsfile + "\nSeer will load the program defaults."), "Preferences Error")
                self.prefs.reset()
                sPrefsFile.WritePreferences(self.prefs, self.prefsfile)
        else:
            sPrefsFile.WritePreferences(self.prefs, self.prefsfile)
        # already restted
        if self.prefs.defaultencoding:
            reload(sys)  #this is needed because of wine and linux
            sys.setdefaultencoding(self.prefs.defaultencoding)
            wx.SetDefaultPyEncoding(self.prefs.defaultencoding)

    def LoadRecentFiles(self):
        f = self.datdirectory + "/recent_files.log"
        if not os.path.exists(f):
            try:
                t = open(f, 'w')
                t.close()
            except IOError:
                self.ShowMessage(("Error Creating: " + f), "Recent Files Error")
        try:
            fin = open(f, 'r')
            s = fin.readline()
            x = 0
            while (len(s) > 0) and (x < self.prefs.recentfileslimit):
                s = s.rstrip()
                if s:
                    self.recentfiles.append(s)
                x = x + 1
                s = fin.readline()
            fin.close()
        except IOError:
            self.ShowMessage(("Error Reading: " + f), "Recent Files Error")

    def LoadShortcuts(self, UseDefault = False):
        #Load STC Shortcuts
        stcshortcutsfile = self.shortcutsdirectory + "/stcshortcuts.dat"
        if os.path.exists(stcshortcutsfile) and (not UseDefault):
            try:
                self.STCShortcuts, self.STCShortcutNames, t = sShortcutsFile.ReadSTCShortcuts(stcshortcutsfile)
                self.STCUseDefault = 0
            except:
                self.ShowMessage(("Error with: " + stcshortcutsfile + "\nSeer will not load STC shortcuts."),
                                  "STC Shortcuts Error")

        #check for shortcuts file in user userpreferencesdirectory
        shortcutsfile = self.shortcutsdirectory + "/shortcuts.dat"
        if os.path.exists(shortcutsfile) and (not UseDefault):
            try:
                self.Shortcuts, self.ShortcutNames, self.ShortcutsIgnoreString = sShortcutsFile.ReadShortcuts(shortcutsfile)
                self.ShortcutsUseDefault = 0
            except:
                self.ShowMessage(("Error with: " + shortcutsfile + "\nSeer will load the program defaults."),
                                  "Shortcuts Error")
                self.LoadShortcuts(True)

        #Load sScript Shortcuts
        sscriptsshortcutsfile = self.shortcutsdirectory + "/sscript.shortcuts.dat"
        if os.path.exists(sscriptsshortcutsfile) and (not UseDefault):
            try:
                self.sScriptShortcuts, self.sScriptShortcutNames, t = sShortcutsFile.ReadShortcuts(sscriptsshortcutsfile, 0)
            except:
                self.ShowMessage(("Error with: " + sscriptsshortcutsfile + "\nSeer will not load sScript shortcuts."),
                                  "sScript Shortcuts Error")

    def OnActivate(self):
        if self.prefs.docautoreload:
            x = 0
            for Document in self.txtDocumentArray:
                if Document.filename:
                    #Get Stat Info:
                    current_mtime = int(os.stat(Document.filename).st_mtime)

                    #Check Stat Info:
                    if Document.mtime > -1:
                        if current_mtime != Document.mtime:
                            if self.Ask('"%s" has been modified by an outside source.  Would you like to reload?' % (Document.filename), "Reload File?"):
                                self.setDocumentTo(x)
                                self.OpenFile(Document.filename, False)
                            else:
                                Document.mtime = current_mtime
                x += 1

    def OnCheckIndentation(self, event):
        wx.BeginBusyCursor()
        result = self.txtDocument.CheckIndentation()
        if result == 2:
            msg = "No indentation was found in this document."
        elif result == -1:
            msg = "This document uses spaces for indentation."
        elif result == 1:
            msg = "This document uses tabs for indentation."
        elif result == 0:
            msg = "This document is mixed.  It uses tabs and spaces for indentation."
        wx.EndBusyCursor()
        self.ShowMessage(msg, "Check Indentation Results")

    def OnCheckSyntax(self, event):
        if self.CheckSyntax(self.docPosition):
            if self.prefs.enablefeedback:
                self.ShowMessage(self.txtDocument.GetFilename() + '\nPassed Syntax Check', 'Syntax Check Ok')
            else:
                self.SetStatusText('Passed Syntax Check', 2)

    def OnCleanUpSpaces(self, event):
        d = wx.TextEntryDialog(self, "Replace a tab with how many spaces?:", "Replace Tabs With Spaces", str(self.prefs.doctabwidth[0]))
        answer = d.ShowModal()
        value = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            wx.BeginBusyCursor()
            wx.Yield()
            try:
                x = int(value)
            except:
                self.ShowMessage("You must enter an integer (number, eg 1,2,128)", "Seer")
                wx.EndBusyCursor()
                return
            if (x > -1) and (x <= 128):
                self.txtDocument.SetToSpaces(x)
            else:
                self.ShowMessage("That number seems WAY too high.  Just what are you doing, replacing  a tab with more than 128 spaces?", "Seer Foolish Error")
                wx.EndBusyCursor()
                return
            self.txtDocument.OnModified(None)
            wx.EndBusyCursor()

    def OnCleanUpTabs(self, event):
        d = wx.TextEntryDialog(self, "Number of spaces to replace with a tab:", "Replace Spaces With Tabs", str(self.prefs.doctabwidth[0]))
        answer = d.ShowModal()
        value = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            wx.BeginBusyCursor()
            wx.Yield()
            try:
                x = int(value)
            except:
                self.ShowMessage("You must enter an integer (number, eg 1,2,128)", "Seer")
                wx.EndBusyCursor()
                return
            if (x > -1) and (x <= 128):
                self.txtDocument.SetToTabs(x)
            else:
                self.ShowMessage("That number seems WAY too high.  Just what are you doing, replacing more than 128 spaces with a tab?", "Seer Foolish Error")
                wx.EndBusyCursor()
                return
            self.txtDocument.OnModified(None)
            wx.EndBusyCursor()

    def OnClearRecent(self, event):
        if self.Ask("This will clear all recent files.\nAre you sure you want to do this?", "Seer"):
            self.recentfiles = []
            self.DestroyRecentFileMenu()
            self.WriteRecentFiles()

    def OnClose(self, event):
        self.PPost(self.EVT_SEER_FILE_CLOSING)
        if self.txtDocument.GetModify():
            #prompt saving filename limodou 2004/04/19
            answer = wx.MessageBox('Would you like to save "%s"?' % self.txtDocument.GetFilename(), "Seer", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            #end limodou
            if answer == wx.YES:
                if not self.OnSave(event):
                    return
            elif answer == wx.CANCEL:
                return

        #franz: oldpos is not used
        #11/24: :) It is now!  (Adding Franz's BugFix, ironically enough).
        oldpos = self.docPosition
        oldfinder = self.txtDocumentArray[oldpos].Finder
        if len(self.txtDocumentArray) > 1:
            self.DestroyDocument()
            #Update txtDocument.targetPosition
            x = 0
            l = len(self.txtDocumentArray)
            while x < l:
                self.txtDocumentArray[x].targetPosition = x
                x = x + 1
            self.documentnotebook.DeletePage(self.docPosition)
            if self.docPosition > 0:
                self.docPosition = self.docPosition - 1
            elif len(self.txtDocumentArray) > 1:
                if self.docPosition > 0:
                    self.docPosition = self.docPosition + 1
            self.setDocumentTo(self.docPosition, 1)
            #11/24:
            if oldpos > self.docPosition:
                if self.txtDocument.Finder:
                    self.txtDocument.Finder.Copy(oldfinder)
        else:
            #Clear the current document:
            self.txtDocument.SetText("")
            self.txtDocument.filename = ""
            self.txtDocument.mtime = -1
            self.txtDocument.EmptyUndoBuffer()
            self.txtDocument.SetSavePoint()
            self.UpdateMenuAndToolbar()
            #The set size stuff ensures that wx.widgets repaints the tab.
            x, y = self.GetSizeTuple()
            self.SetSize(wx.Size(x-1, y-1))
            self.SetSize(wx.Size(x, y))
            self.txtDocument.untitlednumber = 1

        self.txtDocument.IsActive = True
        self.txtDocument.OnModified(None)
        self.documentnotebook.OnPageChanged(None)
        self.reloaddocumentsmenu()
        if self.SourceBrowser is not None:
            self.SourceBrowser.Browse()

        self.txtDocument.SetupLineNumbersMargin()

        self.PPost(self.EVT_SEER_FILE_CLOSED)

    # Feb. 17 05 - Adding import all function

    def OnImportAll(self, event):
        """When the Import All button is clicked, get the path of each open file,
        and append it to sys.path, then import each file into the interpreter
        (via ExecuteCommands)"""

        if self.txtPrompt.pythonintepreter == 0:
            self.ExecutePython()
        self.promptSaveAll()
        x = len(self.txtDocumentArray) - 1
        while x > -1:
            filePath = self.getFilePath(self.txtDocumentArray[x].GetFilename())
            self.txtPrompt.ExecuteCommands("sys.path.append(\"" + filePath[0] + "\")")
            self.txtPrompt.ExecuteCommands("import " + filePath[1])
            x = x - 1


    def getFilePath(self, path):
        """Takes a path including a file name, and returns a tuple
        containing the path (minus file name), and just the file name."""
        if path.find("\\") == -1:
            return (path[:path.rfind("/") + 1], path[path.rfind("/") +1:path.rfind(".")])
        else:
            return (path[:path.rfind("\\") + 1], path[path.rfind("\\") + 1:path.rfind(".")])

    # End Feb. 17 05 import all changes.

    # Feb. 17 05 - Adding pydoc functions
    def OnPyDocAll(self, event):
        """When the generate pydoc for all files item is selected, get the path of each open file,
        and append it to sys.path, then document each file (via pydoc.writedoc))"""

        self.promptSaveAll()

        # specify output directory to save html files to
        dir = self.promptDir("Select output directory:")
        if dir:
            cwd = os.getcwd()
            os.chdir(dir)

            # grab output of pydoc commands in a temp file
            oldstdout = sys.stdout
            fd, tempname = tempfile.mkstemp()
            temp = open(tempname, 'w')

            # go through each open file, documenting
            for x in range(len(self.txtDocumentArray)):
                filePath = self.getFilePath(self.txtDocumentArray[x].GetFilename())
                sys.path.append(filePath[0])
                # create html doc
                sys.stdout = temp
                pydoc.writedoc(str(filePath[1]))
            sys.stdout = oldstdout
            temp.close()
            temp = open(tempname, 'r')
            msg = temp.read()
            temp.close()
            os.chdir(cwd)
            # pop up a message to say it generated the file
            wx.MessageBox('PyDoc: \n'+msg+'\nLocation: '+dir, 'PyDoc', wx.OK)
        else:
            wx.MessageBox ("Please specify a valid directory!", "PyDoc All", wx.ICON_INFORMATION)

    def OnPyDocCurrent(self, event):
        """When the generate pydoc for current file item is selected, get the path of the current file,
        and append it to sys.path, then document it (via pydoc.writedoc))"""

        self.promptSaveCurrent()

        # specify output directory to save html files to
        dir = self.promptDir("Specify output directory:")
        if dir:
            cwd = os.getcwd()
            os.chdir(dir)

            # grab output of pydoc commands in a temp file
            oldstdout = sys.stdout
            fd, tempname = tempfile.mkstemp()
            temp = open(tempname, 'w')

            filePath = self.getFilePath(self.txtDocument.GetFilename())
            sys.path.append(filePath[0])
            # grab output of commands in a temp file
            oldstdout = sys.stdout
            sys.stdout = temp
            # create html file documenting python module
            pydoc.writedoc(str(filePath[1]))
            #pydoc.writedoc(filePath[1].encode (self.prefs.defaultencoding))
            sys.stdout = oldstdout
            temp.close()
            temp = open(tempname, 'r')
            msg = temp.read()
            temp.close()
            # pop up a message to say it generated the file
            os.chdir(cwd)
            wx.MessageBox('PyDoc: '+msg+'Location: '+dir, 'PyDoc', wx.OK)
        else:
            wx.MessageBox ("Please specify a valid directory!", "PyDoc Current File", wx.ICON_INFORMATION, self)

    def OnViewPyDoc(self, event):
        """ Pop up PoyDoc view window, which allows the user to view pydoc in a browser for all
        files on the path"""

        self.promptSaveAll()

        if self.txtPrompt.pythonintepreter == 0:
            self.ExecutePython()
        self.txtPrompt.ExecuteCommands("import pydoc")
        for x in range(len(self.txtDocumentArray)):
            filePath = self.getFilePath(self.txtDocumentArray[x].GetFilename())
            self.txtPrompt.ExecuteCommands("sys.path.append(\"" + filePath[0] + "\")")

        # pydoc gui doesn't close from within seer, display a message to
        # tell the user to close it with the end button
        self.txtPrompt.AddText('\n***Press the red "End" button on the Seer toolbar (or CTRL+D) to stop***\n')
        self.txtPrompt.ExecuteCommands("pydoc.gui()")

    # End Feb. 17 05 pydoc changes.

    def OnCloseAllDocuments(self, event):
        x = len(self.txtDocumentArray) - 1
        while x > -1:
            self.setDocumentTo(x, True)
            if self.txtDocument.GetModify():
                #prompt saving filename limodou 2004/04/19
                if self.Ask('Would you like to save "%s"?' % self.txtDocument.GetFilename(), "Seer"):
                #end limodou
                    self.OnSave(event)
            self.OnClose(event)
            x = x - 1

    def OnCloseAllOtherDocuments(self, event):
        if not self.txtDocument.filename:
            self.ShowMessage("Sorry, does not work when an untitled file is selected.", "Seer Error")
            return
        farray = map(lambda document: document.filename, self.txtDocumentArray)
        try:
            i = farray.index(self.txtDocument.filename)
        except:
            #franz: (Updated Namespace)
            self.ShowMessage("Something went wrong trying to close all other tabs.", "Seer Error")
            return

        x = len(farray) - 1
        while x > -1:
            if x != i:
                self.setDocumentTo(x, True)
                if self.txtDocument.GetModify():
                    #prompt saveing filename limodou 2004/04/19
                    if self.Ask('Would you like to save "%s"?' % self.txtDocument.GetFilename(), "Seer"):
                    #end limodou
                        self.OnSave(event)
                self.OnClose(event)
            x = x - 1

    def OnClosePrompt(self, event):
        oldpos = self.promptPosition
        oldfinder = self.txtPromptArray[oldpos].Finder
        self.OnEnd(None)

        if len(self.txtPromptArray) > 1:
            self.txtPromptArray.pop(self.promptPosition)

            self.promptnotebook.DeletePage(self.promptPosition)
            if self.promptPosition > 0:
                self.promptPosition = self.promptPosition - 1
            elif len(self.txtPromptArray) > 1:
                if self.promptPosition > 0:
                    self.promptPosition = self.promptPosition + 1
            self.setPromptTo(self.promptPosition)
            #11/24:
            if oldpos > self.promptPosition:
                if self.txtPrompt.Finder:
                    self.txtPrompt.Finder.Copy(oldfinder)
        else:
            self.txtPrompt.SetText("")
            self.txtPrompt.EmptyUndoBuffer()
            self.txtPrompt.SetSavePoint()
            self.UpdateMenuAndToolbar()
            self.promptnotebook.SetPageText(self.promptPosition, "Prompt")
            #The set size stuff ensures that wx.widgets repaints the tab.
            x, y = self.GetSizeTuple()
            self.SetSize(wx.Size(x-1, y-1))
            self.SetSize(wx.Size(x, y))


        self.promptnotebook.OnPageChanged(None)

    def OnCloseW(self, event):
        if event.CanVeto():
            try:
                x = self.docPosition
                if self.docPosition > 0:
                    fromzero = self.docPosition
                l = len(self.txtDocumentArray)
                while x < l:
                    if self.txtDocumentArray[x].GetModify():
                        answer = wx.MessageBox('Would you like to save "%s"?' % self.txtDocumentArray[x].GetFilename(),
                            "Seer", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                        if answer == wx.YES:
                            self.setDocumentTo(x)
                            self.OnSave(event)
                        elif answer == wx.CANCEL:
                            return
                    x = x + 1

                if fromzero > 0:
                    x = 0
                    l = fromzero
                    while x < l:
                        if self.txtDocumentArray[x].GetModify():
                            answer = wx.MessageBox('Would you like to save "%s"?' % self.txtDocumentArray[x].GetFilename(),
                                "Seer", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                            if answer == wx.YES:
                                self.setDocumentTo(x)
                                self.OnSave(event)
                            elif answer == wx.CANCEL:
                                return
                        x = x + 1
            except:
                if self.prefs.alwayspromptonexit:
                    if not self.Ask("Are you sure you want to exit?   ", "Seer"):
                        return

        if self.prefs.rememberwindowsizeandposition:
            try:
                f = file(self.datdirectory + "/seer.sizeandposition.dat", 'w')
                x, y = self.GetSizeTuple()
                px, py = self.GetPositionTuple()
                f.write(str(x) + '\n' + str(y) + '\n' + str(px) + '\n' + str(py))
                f.close()
            except:
                self.ShowMessage("Error Saving Window Size", 'Error')

        self.mainpanel.MemorizePanelSizes()

        event.Skip()

    def OnCommentRegion(self, event):
        selstart, selend = self.txtDocument.GetSelection()
        #From the start of the first line selected
        startline = self.txtDocument.LineFromPosition(selstart)
        self.txtDocument.GotoLine(startline)
        start = self.txtDocument.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        end = self.txtDocument.GetLineEndPosition(self.txtDocument.LineFromPosition(tend))
        #End Bugfix Chris Wilson
        eol = self.txtDocument.GetEndOfLineCharacter()
        if self.prefs.doccommentmode == 0:
            self.txtDocument.SetSelection(start, end)
            text = self.prefs.doccommentstring[self.txtDocument.filetype] + self.txtDocument.GetSelectedText()
            text = text.replace(eol, eol + self.prefs.doccommentstring[self.txtDocument.filetype])
            self.txtDocument.ReplaceSelection(text)
        else:
            mask = self.txtDocument.GetModEventMask()
            self.txtDocument.SetModEventMask(0)
            wpos = start
            while wpos < end:
                ws = self.txtDocument.GetLineIndentPosition(startline)
                le = self.txtDocument.GetLineEndPosition(startline)
                if ws != le:
                    self.txtDocument.InsertText(ws, self.prefs.doccommentstring[self.txtDocument.filetype])
                startline += 1
                wpos = self.txtDocument.PositionFromLine(startline)
            self.txtDocument.SetModEventMask(mask)
        self.txtDocument.GotoPos(start)

    def OnCustomizePopUpMenu(self, event):
        from sPopUpMenuDialog import sPopUpMenuDialog
        d = sPopUpMenuDialog(self)
        d.ShowModal()
        d.Destroy()

    def OnCustomizeToolBar(self, event):
        from sToolBarDialog import sToolBarDialog
        d = sToolBarDialog(self)
        d.ShowModal()
        d.Destroy()

    def OnCustomizeShortcuts(self, event):
        from sShortcutsDialog import sShortcutsDialog
        d = sShortcutsDialog(self)
        d.ShowModal()
        d.Destroy()

    def OnDedentRegion(self, event):
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.txtDocument.GetSelection()
        begline = self.txtDocument.LineFromPosition(beg)
        endline = self.txtDocument.LineFromPosition(end)

        mask = self.txtDocument.GetModEventMask()
        self.txtDocument.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.txtDocument.PositionFromLine(begline)
            self.txtDocument.SetSelection(pos, pos)
            self.txtDocument.GotoPos(pos)
            self.txtDocument.BackTab()
            self.txtDocument.SetSelection(pos, self.txtDocument.GetLineEndPosition(begline))
            self.txtDocument.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.txtDocument.BackTab()
        self.txtDocument.SetModEventMask(mask)

    def OnEditBookmarks(self, event):
        from sBookmarksDialog import sBookmarksDialog
        d = sBookmarksDialog(self, self.datdirectory + "/bookmarks.dat")
        d.ShowModal()
        d.Destroy()
        self.bookmarksmenu.reloadBookmarks()

    def OnEditScriptMenu(self, event):
        from sScriptDialog import sScriptDialog
        d = sScriptDialog(self)
        d.ShowModal()
        d.Destroy()
        self.sscriptmenu.reloadscripts()

    def OnEnd(self, event):
        if self.txtPrompt.pid != -1:
            self.promptnotebook.SetPageImage(self.promptPosition, 2)
            self.UpdateMenuAndToolbar()
            wx.Process_Kill(self.txtPrompt.pid, wx.SIGKILL)
            self.txtPrompt.SetReadOnly(1)

    def OnExit(self, event):
        self.Close(False)

    def OnExpandAll(self, event):
        if self.prefs.docfolding[self.txtDocument.filetype]:
            wx.BeginBusyCursor()
            self.txtDocument.FoldAll(True)
            wx.EndBusyCursor()

    def OnFindAndComplete(self, event):
        #Submitted Patch by Martinho
        #now stops at '.' (repre)
        #re-ordered the text so the list shows the nearer completion words first.

        #Get The Current Word
        text = self.txtDocument.GetText()
        pos = self.txtDocument.GetCurrentPos()
        repre = re.compile("\(|\)|\[|\]|\{|\}|\<|\>|\.", re.IGNORECASE | re.MULTILINE)
        regex = re.compile("\w*\Z", re.IGNORECASE | re.MULTILINE)
        #franz: regexend is not used
        eol = self.txtDocument.GetEndOfLineCharacter()

        #Get the left bit
        i = text[0:pos].rfind(eol)
        if i == -1:
            i = 0
        else:
            i = i + len(eol)

        #Check for characters to stop at.
        t = re.finditer(repre, text[i:pos])
        if t is not None:
            try:
                preresult = t.next()
            except:
                preresult = None
            try:
                while t.next() is not None:
                    preresult = t.next()
            except:
                if preresult is not None:
                    t = i + preresult.start() + 1
                    #If t == pos, then you do not want to stop
                    #at the character.
                    if t < pos:
                        i = t

        #Find Non Whitespace Characters.
        result = regex.search(text[i:pos])

        if result is None:
            start = i
        else:
            start = i + result.start()

        if (pos - start) <= 0:
            return

        #Handle special characters
        oword = text[start:pos]
        word = oword.replace('\\', "\\\\").replace('^', "\\^").replace('*', "\\*").replace('$', "\\$")
        word = word.replace('+', "\\+").replace('?', "\\?").replace('{', "\\{").replace('}', "\\}")
        word = word.replace('[', "\\[").replace(']', "\\]").replace('(', "\\(").replace(')', "\\)")
        word = word.replace('.', "\\.").replace('|', "\\|").replace('<', "\\<").replace('>', "\\>")

        #Find all matches in the document.
        findandcompleteregex = re.compile(r"\b" + word + r"\w*\b", re.MULTILINE)

        text_lines = text.split(eol)
        cl = self.txtDocument.GetCurrentLine()
        s_i = cl
        e_i = cl
        sorted_text = ""
        while (s_i>=0) or (e_i < len(text_lines)):
            if s_i>=0 :
                sorted_text += text_lines[s_i] + eol
                s_i = s_i - 1
            if e_i < len(text_lines) :
                sorted_text += text_lines[e_i] + eol
                e_i = e_i + 1

        r = findandcompleteregex.findall(sorted_text)

        results = ""
        tr = []
        for item in r:
            try:
                tr.index(item)
            except:
                if not item == oword:
                    results = results + " " + item
                    tr.append(item)

        results = results.strip()

        if tr:
            try:
                self.txtDocument.AutoCompShow(len(oword), results)
            except:
                #What is this mess?
                pass

    def OnFoldAll(self, event):
        if self.prefs.docfolding[self.txtDocument.filetype]:
            wx.BeginBusyCursor()
            self.txtDocument.FoldAll(False)
            wx.EndBusyCursor()

    def OnFormatMacMode(self, event):
        wx.BeginBusyCursor()
        wx.Yield()
        self.txtDocument.SetEOLMode(wx.stc.STC_EOL_CR)
        text = self.txtDocument.GetText()
        text = self.FormatMacReTarget.sub('\r', text)
        self.txtDocument.SetText(text)
        self.txtDocument.OnModified(None)
        wx.EndBusyCursor()

    def OnFormatUnixMode(self, event):
        wx.BeginBusyCursor()
        wx.Yield()
        self.txtDocument.SetEOLMode(wx.stc.STC_EOL_LF)
        text = self.txtDocument.GetText()
        text = self.FormatUnixReTarget.sub('\n', text)
        self.txtDocument.SetText(text)
        self.txtDocument.OnModified(None)
        wx.EndBusyCursor()

    def OnFormatWinMode(self, event):
        wx.BeginBusyCursor()
        wx.Yield()
        self.txtDocument.SetEOLMode(wx.stc.STC_EOL_CRLF)
        text = self.txtDocument.GetText()
        text = self.FormatWinReTarget.sub('\r\n', text)
        self.txtDocument.SetText(text)
        self.txtDocument.OnModified(None)
        wx.EndBusyCursor()

    def OnGoTo(self, event):
        d = wx.TextEntryDialog(self, "Go To Line Number:", "Seer - Go To", "")
        answer = d.ShowModal()
        v = d.GetValue()
        d.Destroy()
        if answer == wx.ID_OK:
            try:
                v = int(v) - 1
                if (v >= 0) and (v < self.txtDocument.GetLineCount()):
                    self.txtDocument.EnsureVisible(v)
                    self.txtDocument.ScrollToLine(v)
                    self.txtDocument.GotoLine(v)
                else:
                    sScrolledMessageDialog.ShowMessage(self, "That line does not exist", "Seer Error")
            except StandardError:
                sScrolledMessageDialog.ShowMessage(self, "You must enter an integer (1, 2, 3, etc)", "Seer Error")

    def OnGoToBlockEnd(self, event):
        sGetBlockInfo.GoToBlockEnd(self.txtDocument)

    def OnGoToBlockStart(self, event):
        sGetBlockInfo.GoToBlockStart(self.txtDocument)

    def OnGoToClassEnd(self, event):
        sGetBlockInfo.GoToBlockEnd(self.txtDocument, 'class')

    def OnGoToClassStart(self, event):
        sGetBlockInfo.GoToBlockStart(self.txtDocument, 'class')

    def OnGoToDefEnd(self, event):
        sGetBlockInfo.GoToBlockEnd(self.txtDocument, 'def')

    def OnGoToDefStart(self, event):
        sGetBlockInfo.GoToBlockStart(self.txtDocument, 'def')

    def OnIndentRegion(self, event):
        #Submitted Patch:  Franz Steinhausler
        #Submitted Patch (ModEvent Mask), Franz Steinhausler
        beg, end = self.txtDocument.GetSelection()
        begline = self.txtDocument.LineFromPosition(beg)
        endline = self.txtDocument.LineFromPosition(end)

        mask = self.txtDocument.GetModEventMask()
        self.txtDocument.SetModEventMask(0)

        if begline == endline:
            #This section modified by Dan
            pos = self.txtDocument.PositionFromLine(begline)
            self.txtDocument.SetSelection(pos, pos)
            self.txtDocument.GotoPos(pos)
            self.txtDocument.Tab()
            self.txtDocument.SetSelection(pos, self.txtDocument.GetLineEndPosition(begline))
            self.txtDocument.SetModEventMask(mask)
            return

        #Submitted Patch:  Christian Daven
        self.txtDocument.Tab()
        self.txtDocument.SetModEventMask(mask)

    def OnInsertRegEx(self, event):
        from sRegularExpressionDialog import sRegularExpressionDialog
        d = sRegularExpressionDialog(self, -1, "Insert Regular Expression", self.txtPrompt.GetSTCFocus())
        d.Show()

    def OnInsertSeparator(self, event):
        d = sSeparatorDialog(self, 'Insert Separator')
        answer = d.ShowModal()
        label = d.GetLabel()
        d.Destroy()
        if answer == wx.ID_OK:
            pos = self.txtDocument.GetCurrentPos()
            self.txtDocument.InsertText(pos, label)
            self.txtDocument.GotoPos(pos + len(label))

    def OnKeyDown(self, event):
        self.RunShortcuts(event)

        event.Skip()

    def OnLowercase(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.CmdKeyExecute(wx.stc.STC_CMD_LOWERCASE)
        else:
            self.txtDocument.CmdKeyExecute(wx.stc.STC_CMD_LOWERCASE)

    def OnMenuFind(self, event):
        stc = self.GetActiveSTC()
        d = sFindReplaceDialog(self, -1, "Find", stc)
        d.SetOptions(self.FindOptions)
        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetSelectedText())
        elif self.prefs.findreplaceundercursor:
            pos = stc.GetCurrentPos()
            d.SetFindString(stc.GetTextRange(stc.WordStartPosition(pos, 1), stc.WordEndPosition(pos, 1)))
        d.Show(True)

    def OnMenuFindNext(self, event):
        self.GetActiveSTC().Finder.DoFindNext()

    def OnMenuFindPrevious(self, event):
        self.GetActiveSTC().Finder.DoFindPrevious()

    def OnMenuReplace(self, event):
        stc = self.GetActiveSTC()
        d = sFindReplaceDialog(self, -1, "Replace", stc, 1)
        d.SetOptions(self.ReplaceOptions)
        if stc.GetSelectionStart() < stc.GetSelectionEnd():
            d.SetFindString(stc.GetTextRange(stc.GetSelectionStart(), stc.GetSelectionEnd()))
        else:
            d.SetFindString(stc.Finder.GetFindText())
        d.Show(True)

    def OnNew(self, event):
        l = len(self.txtDocumentArray)
        unumbers = map(lambda x: x.untitlednumber, self.txtDocumentArray)
        unumbers.sort()
        x = 0
        last = 0
        while x < l:
            if unumbers[x] > 0:
                if unumbers[x] != (last + 1):
                    x = l
                else:
                    last = unumbers[x]
                    x = x + 1
            else:
                x = x + 1
        last = last + 1

        nextpage = sPanel(self.documentnotebook, self.ID_APP)
        self.txtDocumentArray.append(sText(nextpage, self.ID_APP, self))
        nextpage.SetSTC(self.txtDocumentArray[l])
        self.documentnotebook.AddPage(nextpage, "Untitled " + str(last))
        self.txtDocumentArray[l].untitlednumber = last

        self.txtDocumentArray[l].Finder.Copy(self.txtDocument.Finder)

        self.lastprogargsArray.append("")
        self.txtDocumentArray[l].SetTargetPosition(l)
        self.txtDocument.IsActive = False
        self.txtDocument.OnModified(None)
        self.setDocumentTo(l)

        self.txtDocument.SetupPrefsDocument(1)

        self.reloaddocumentsmenu()

        self.txtDocument.SetSTCFocus(True)

        self.PPost(self.EVT_SEER_NEW)

    def OnNewPrompt(self, event):
        l = len(self.txtPromptArray)

        nextpage = sPanel(self.promptnotebook, self.ID_APP)
        self.txtPromptArray.append(sPrompt(nextpage, self.ID_APP, self))
        nextpage.SetSTC(self.txtPromptArray[l])
        self.promptnotebook.AddPage(nextpage, "Prompt")

        self.txtPromptArray[l].Finder.Copy(self.txtPrompt.Finder)

        self.setPromptTo(l)

        self.txtPrompt.SetupPrefsPrompt(1)

        self.txtPrompt.SetSTCFocus(True)

        self.PPost(self.EVT_SEER_NEW_PROMPT)

    def OnOpen(self, event):
        dlg = sFileDialog.FileDialog(self, "Open", self.prefs.wildcard, MultipleSelection=True, ShowRecentFiles=True)
        if self.ddirectory:
            try:
                dlg.SetDirectory(self.ddirectory)
            except:
                self.ShowMessage(("Error Setting Default Directory To: " + self.ddirectory), "Seer Error")
        if dlg.ShowModal() == wx.ID_OK:
            alreadyopen = self.GetAlreadyOpen()
            theencoding = dlg.GetEncoding()
            old = self.txtDocument.filename
            filenames = dlg.GetPaths()
            filenames = map(lambda x: x.replace("\\", '/'), filenames)
            l = len(filenames)
            c = 0
            while c < l:
                if filenames[c] in alreadyopen:
                    #franz: pychecker: i is not referenced
                    #Franz Fixed the fix.
                    i = alreadyopen.index(filenames[c])
                    self.setDocumentTo(i)
                    filenames.pop(c)
                    c = c - 1
                    l = l - 1
                c = c + 1
            if l < 1:
                return
            x = 1
            if l > 1:
                self.OpenFile(filenames[0], len(old) > 0, encoding=theencoding)
            while x < l:
                self.OpenFile(filenames[x], True, encoding=theencoding)
                x = x + 1
            if l <= 1:
                if (len(old) > 0) or (self.txtDocument.GetModify()):
                    self.OpenFile(filenames[0], True, encoding=theencoding)
                else:
                    self.OpenFile(filenames[0], False, encoding=theencoding)
            dlg.Destroy()

    def OnOpenImportedModule(self, event):
        from sOpenImportedModuleDialog import sOpenImportedModuleDialog, GetModulePath, ParseImportStatement
        text = self.txtDocument.GetText()
        importmatches = self.reimport.findall(text)
        fromimportmatches = self.refromimport.findall(text)

        modulelist = []

        rmodulelist = []
        imatchesarray = ParseImportStatement(importmatches)
        for imatch in imatchesarray:
            rmodulelist.extend(imatch)
        fmatchesarray = ParseImportStatement(fromimportmatches)
        for fmatch in fmatchesarray:
            rmodulelist.extend(fmatch)

        for mod in rmodulelist:
            modulelist.append(mod.strip(','))

        docpath = os.path.split(self.txtDocument.filename)[0]

        pathlist = []

        x = 0
        l = len(modulelist)
        while x < l:
            if modulelist.count(modulelist[x]) > 1:
                modulelist.pop(x)
                x -= 1
                l -= 1
            else:
                n, mpath = GetModulePath(docpath, modulelist[x], self.PLATFORM_IS_WIN)
                if mpath is None:
                    modulelist.pop(x)
                    x -= 1
                    l -= 1
                else:
                    pathlist.append([n, mpath])
            x = x + 1

        modulelist.sort()

        pathdictionary = dict(pathlist)

        d = sOpenImportedModuleDialog(self, modulelist)
        answer = d.ShowModal()
        d.Destroy()

        if answer == wx.ID_OK:
            selectedmodule = d.GetSelectedModule()

            modulefile = pathdictionary[selectedmodule]

            alreadyopen = self.GetAlreadyOpen()
            if modulefile in alreadyopen:
                self.setDocumentTo(alreadyopen.index(modulefile))
                return

            self.OpenFile(modulefile, True)

    def OnOpenRecentFile(self, event):
        recentmenuindex = event.GetId() - self.ID_RECENT_FILES_BASE
        alreadyopen = self.GetAlreadyOpen()
        if self.recentfiles[recentmenuindex] in alreadyopen:
            #franz: pychecker: i is not referenced
            #Franz fixed the fix.
            c = alreadyopen.index(self.recentfiles[recentmenuindex])
            self.setDocumentTo(c)
            return
        if not os.path.exists(self.recentfiles[recentmenuindex]):
            self.ShowMessage(('"' + self.recentfiles[recentmenuindex] + '" Does Not Exist.'), "Recent File No Longer Exists")
            return
        old = self.txtDocument.filename
        filename = self.recentfiles[recentmenuindex]
        if (len(old) > 0) or (self.txtDocument.GetModify()):
            self.OpenFile(filename, True)
        else:
            self.OpenFile(filename, False)

    def OnPrefs(self, event):
        from sPrefsDialog import sPrefsDialog
        d = sPrefsDialog(self, -1, "Seer - Preferences")
        d.ShowModal()
        d.Destroy()

    def OnPrint(self, event):
        self.Printer.Print(self.txtDocument.GetText(), self.txtDocument.filename, self.prefs.printdoclinenumbers)

    def OnPrintSetup(self, event):
        self.Printer.PrinterSetup(self)

    def OnPrintPrompt(self, event):
        self.Printer.Print(self.txtPrompt.GetText(), self.txtDocument.filename, self.prefs.printpromptlinenumbers)

    def OnProcessEnded(self, event):
        #Set the process info to the correct position in the array.
        i = 0
        epid = event.GetPid()
        try:
            i = map(lambda tprompt: tprompt.pid == epid, self.txtPromptArray).index(True)
        except:
            return

        #First, check for any leftover output.
        self.txtPromptArray[i].OnIdle(event)

        #If this is the process for the current window:
        if self.promptPosition == i:
            self.txtPrompt.process.Destroy()
            self.txtPrompt.process = None
            self.txtPrompt.pid = -1
            self.txtPrompt.SetReadOnly(1)
            self.txtPrompt.pythonintepreter = 0
            self.UpdateMenuAndToolbar()
            self.SetStatusText("", 2)
            self.promptnotebook.SetPageImage(i, 2)
        else:
            self.txtPromptArray[i].process.Destroy()
            self.txtPromptArray[i].process = None
            self.txtPromptArray[i].pid = -1
            self.txtPromptArray[i].SetReadOnly(1)
            self.txtPromptArray[i].pythonintepreter = 0
            self.promptnotebook.SetPageImage(i, 0)
        self.txtDocument.SetFocus()

    def OnPython(self, event):
        self.ExecutePython()

    def OnRedo(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.Redo()
        else:
            self.txtDocument.Redo()

    def OnReload(self, event):
        if self.Ask("This will reload the current file.\nAny changes will be lost.\nAre you sure you want to do this?", "Seer"):
            if self.txtDocument.filename:
                self.OpenFile(self.txtDocument.filename, False)
        event.Skip()

    def OnRestoreFromBackup(self, event):
        if os.path.exists(self.txtDocument.filename + ".bak"):
            if self.Ask("This will restore the current file from the last backup.\nAny changes will be lost.\nAre you sure you want to do this?", "Seer"):
                if self.txtDocument.filename:
                    old = self.txtDocument.filename
                    filename = self.txtDocument.filename + ".bak"
                    self.OpenFile(filename, False, False)
                    self.txtDocument.filename = old
                    self.txtDocument.OnModified(None)
        else:
            self.ShowMessage(("No Backup File For: \"" + self.txtDocument.filename + "\""), "Seer Error")

    def OnRun(self, event):
        if self.prefs.saveonrun:
            self.OnSave(event)
        elif self.txtDocument.GetModify():
            if self.Ask("The file has been modified.\nIt would be wise to save before running.\nWould you like to save the file?", "Seer"):
                self.OnSave(event)
        if self.txtDocument.filename:
            cdir, filen = os.path.split(self.txtDocument.filename)
            cwd = os.getcwd()
            try:
                os.chdir(cdir)
            except:
                self.ShowMessage("Error Setting current directory for Python.", "Seer RunError")
            largs = ""
            if self.lastprogargs:
                largs = ' ' + self.lastprogargs
            if self.PLATFORM_IS_WIN:
                self.runcommand((self.pythexecw + " -u " +  self.prefs.pythonargs + ' "' + self.txtDocument.filename.replace("\\", "/") + '"' + largs), "Running " + filen, filen)
            else:
                self.runcommand((self.pythexec + " -u " +  self.prefs.pythonargs + ' "' + self.txtDocument.filename + '"'  + largs), "Running " + filen, filen)
            os.chdir(cwd)

    def OnSave(self, event):
        if not self.txtDocument.filename:
            return self.OnSaveAs(event)
        else:
            self.SaveFile(self.docPosition)
            if self.prefs.sourcebrowserautorefreshonsave and (self.SourceBrowser is not None):
                self.SourceBrowser.Browse()
        return True

    def OnSaveAll(self, event):
        oldpos = self.docPosition

        x = 0
        if self.prefs.promptonsaveall:
            tosaveArray = []
            tosaveLabels = []
            for document in self.txtDocumentArray:
                if self.txtDocumentArray[x].GetModify():
                    tosaveArray.append(x)
                    tosaveLabels.append(self.txtDocumentArray[x].GetFilenameTitle())
                x += 1
            if not tosaveLabels:
                self.ShowMessage('No Modified Documents.', 'Save All')
                return
            d = wx.lib.dialogs.MultipleChoiceDialog(self, "Save All Modified Documents?", "Save All", tosaveLabels, size=(300, 300))
            l = len(tosaveArray)
            y = 0
            while y < l:
                d.lbox.SetSelection(y)
                y += 1
            answer = d.ShowModal()
            selections = d.GetValue()
            d.Destroy()
            if answer == wx.ID_OK:
                for selection in selections:
                    if not self.txtDocumentArray[tosaveArray[selection]].filename:
                        self.setDocumentTo(tosaveArray[selection])
                        self.OnSaveAs(None)
                    else:
                        self.SaveFile(tosaveArray[selection])
            else:
                return False
        else:
            for document in self.txtDocumentArray:
                if self.txtDocumentArray[x].GetModify():
                    if not self.txtDocumentArray[x].filename:
                        self.setDocumentTo(x)
                        self.OnSaveAs(None)
                    else:
                        self.SaveFile(x)
                x += 1

        self.setDocumentTo(oldpos)

        return True

    def OnSaveAs(self, event):
        dlg = sFileDialog.FileDialog(self, "Save File As", self.prefs.wildcard, IsASaveDialog=True)
        if self.ddirectory:
            try:
                dlg.SetDirectory(self.ddirectory)
            except:
                #franz: ddirectory
                self.ShowMessage(("Error Setting Default Directory To: " + self.ddirectory), "Seer Error")
        if dlg.ShowModal() == wx.ID_OK:
            old = self.txtDocument.filename
            if self.txtDocument.untitlednumber > 0:
                self.txtDocument.untitlednumber = -1
            self.txtDocument.filename = dlg.GetPath().replace("\\", "/")
            self.ddirectory = os.path.dirname(self.txtDocument.filename)
            self.DestroyRecentFileMenu()
            if not self.SaveFile(self.docPosition, not (old == self.txtDocument.filename)):
                self.txtDocument.filename = old
                self.CreateRecentFileMenu()
                return
            self.UpdateMenuAndToolbar()

            #Highlighting
            if not self.prefs.doconlyusedefaultsyntaxhighlighting:
                if self.checkiffileisPython(self.txtDocument.filename):
                    #Python
                    self.txtDocument.filetype = 0
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_PYTHON, True)
                elif self.checkiffileisCPP(self.txtDocument.filename):
                    #C/C++
                    self.txtDocument.filetype = 1
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_CPP, True)
                elif self.checkiffileisHTML(self.txtDocument.filename):
                    #HTML
                    self.txtDocument.filetype = 2
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_HTML, True)
                elif self.checkiffileisPlainText(self.txtDocument.filename):
                    #Plain Text
                    self.txtDocument.filetype = 3
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_PLAIN_TEXT, True)
                else:
                    #Default
                    pass
                self.txtDocument.SetupPrefsDocument()

            #Update Recent Files
            if self.recentfiles.count(self.txtDocument.filename) != 0:
                self.recentfiles.remove(self.txtDocument.filename)
            if len(self.recentfiles) == self.prefs.recentfileslimit:
                self.recentfiles.pop()
            self.recentfiles.insert(0, self.txtDocument.filename)
            self.WriteRecentFiles()
            self.CreateRecentFileMenu()
            dlg.Destroy()
            self.reloaddocumentsmenu()
            #Refreshes the tab.
            x, y = self.documentnotebook.GetSizeTuple()
            self.documentnotebook.SetSize(wx.Size(x+1, y+1))
            self.documentnotebook.SetSize(wx.Size(x, y))
        else:
            return False
        return True

    def OnSaveCopy(self, event):
        #add feature to save a copy, midtoad 2005-10-03
        dlg = sFileDialog.FileDialog(self, "Save Copy To", self.prefs.wildcard, IsASaveDialog=True)
        if self.ddirectory:
            try:
                dlg.SetDirectory(self.ddirectory)
            except:
                self.ShowMessage(("Error Setting Default Directory To: " + self.ddirectory), "Seer Error")
        if dlg.ShowModal() == wx.ID_OK:
            cfilename = dlg.GetPath().replace("\\", "/")
            self.ddirectory = os.path.dirname(cfilename)
            try:
                shutil.copyfile(self.txtDocument.filename, cfilename)
                self.ShowMessage("Saved %s to %s" % (self.txtDocument.filename, cfilename), "Save as Copy")
            except IOError:
                self.ShowMessage(("Error copying file to: " + cfilename), "Seer Error")
        dlg.Destroy()

    def OnSavePrompt(self, event):
        dlg = sFileDialog.FileDialog(self, 'Save Prompt Text To', 'Text File (*.txt)|*.txt|All files (*)|*', IsASaveDialog=True)
        if self.ddirectory:
            try:
                dlg.SetDirectory(self.ddirectory)
            except:
                #franz: ddirectory
                self.ShowMessage(("Error Setting Default Directory To: " + self.ddirectory), "Seer Error")
        if dlg.ShowModal() == wx.ID_OK:
            pfilename = dlg.GetPath().replace("\\", "/")
            self.ddirectory = os.path.dirname(pfilename)
            try:
                ctext = sEncoding.DecodeText(self, self.txtPrompt.GetText())

                cfile = file(pfilename, 'wb')
                cfile.write(ctext)
                cfile.close()
            except:
                self.ShowMessage(("Error Writing: " + pfilename), "Seer Error")
            dlg.Destroy()

    def OnSelectAll(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.SelectAll()
        else:
            self.txtDocument.SelectAll()

    def OnSelectDocument(self, event):
        eid = event.GetId()
        i = eid - self.ID_DOCUMENTS_BASE
        self.documentnotebook.SetSelection(i)
        self.documentnotebook.SetTab()

    def OnSelectDocumentFirst(self, event):
        self.documentnotebook.SetSelection(0)
        self.documentnotebook.SetTab()

    def OnSelectDocumentLast(self, event):
        self.documentnotebook.SetSelection(self.documentnotebook.GetPageCount()-1)
        self.documentnotebook.SetTab()

    def OnSelectDocumentNext(self, event):
        self.documentnotebook.AdvanceSelection(True)
        self.documentnotebook.SetTab()

    def OnSelectDocumentPrevious(self, event):
        self.documentnotebook.AdvanceSelection(False)
        self.documentnotebook.SetTab()

    def OnSetArgs(self, event):
        d = wx.TextEntryDialog(self, "Arguments:", "Seer - Set Arguments", self.lastprogargs)
        if d.ShowModal() == wx.ID_OK:
            self.lastprogargs = d.GetValue()
            self.lastprogargsArray[self.docPosition] = self.lastprogargs
        d.Destroy()

    def OnSourceBrowserGoTo(self, event):
        sSourceBrowserGoTo.SourceBrowserGoTo(self, self.txtDocument)

    def OnSyntaxHighlightingPython(self, event):
        self.txtDocument.filetype = 0
        self.txtDocument.SetupPrefsDocument()

    def OnSyntaxHighlightingCPP(self, event):
        self.txtDocument.filetype = 1
        self.txtDocument.SetupPrefsDocument()

    def OnSyntaxHighlightingHTML(self, event):
        self.txtDocument.filetype = 2
        self.txtDocument.SetupPrefsDocument()

    def OnSyntaxHighlightingText(self, event):
        self.txtDocument.filetype = 3
        self.txtDocument.SetupPrefsDocument()

    def OnToggleFold(self, event):
        try:
            self.txtDocument.ToggleFold(self.txtDocument.GetCurrentLine())
        except:
            self.ShowMessage('Error Folding Line', 'Fold Error')

    def OnTogglePrompt(self, event):
        if self.mainpanel.PromptIsVisible:
            self.mainpanel.PromptIsVisible = False
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  False)
            self.mainpanel.OnSize(None)
            self.txtDocument.SetFocus()
        else:
            self.mainpanel.PromptIsVisible = True
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  True)
            self.mainpanel.OnSize(None)
            self.txtPrompt.SetFocus()

    def OnToggleSourceBrowser(self, event):
        if self.SourceBrowser is None:
            target, i = self.mainpanel.GetTargetNotebookPage(self.prefs.sourcebrowserpanel, 'Source Browser')
            self.SourceBrowser = sSourceBrowserPanel(target, -1, self.prefs.sourcebrowserpanel, i)
            self.mainpanel.SetPanelSize(self.prefs.sourcebrowserpanel, self.prefs.sourcebrowsersize)
            target.SetPanel(self.SourceBrowser)
            self.mainpanel.ShowPanel(self.prefs.sourcebrowserpanel, i)
        else:
            if not self.mainpanel.IsVisible(self.SourceBrowser.position, self.SourceBrowser.Index):
                self.SourceBrowser.Browse()
            self.mainpanel.TogglePanel(self.SourceBrowser.position, self.SourceBrowser.Index)

    def OnToggleViewWhiteSpace(self, event):
        if self.txtPrompt.GetSTCFocus():
            c = self.txtPrompt.GetViewWhiteSpace()
            self.txtPrompt.SetViewWhiteSpace(not c)
            if self.prefs.vieweol:
                self.txtPrompt.SetViewEOL(not c)
        else:
            c = self.txtDocument.GetViewWhiteSpace()
            self.txtDocument.SetViewWhiteSpace(not c)
            if self.prefs.vieweol:
                self.txtDocument.SetViewEOL(not c)

    def OnToolBar(self, event):
        try:
            i = event.GetId() - self.ID_OTHER
            txt = self.ToolBarList[i]
            if txt in self.stcshortcutlist:
                pos = self.stcshortcutlist.index(txt)
                if self.txtPrompt.GetSTCFocus():
                    self.txtPrompt.CmdKeyExecute(self.txtPrompt.STCCOMMANDLIST[pos])
                else:
                    self.txtDocument.CmdKeyExecute(self.txtDocument.STCCOMMANDLIST[pos])
            else:
                if txt in self.PluginToolBarLabels:
                    pos = self.PluginToolBarLabels.index(txt)
                    self.PluginToolBarFunctions[pos](event)
        except:
            self.ShowMessage("ToolBar Action Error", "Seer Error")

    def OnUnCommentRegion(self, event):
        #franz: pos is not used
        selstart, selend = self.txtDocument.GetSelection()
        #From the start of the first line selected
        startline = self.txtDocument.LineFromPosition(selstart)
        self.txtDocument.GotoLine(startline)
        start = self.txtDocument.GetCurrentPos()
        #To the end of the last line selected
        #Bugfix Chris Wilson
        #Edited by Dan (selend fix)
        if selend == selstart:
            tend = selend
        else:
            tend = selend - 1
        end = self.txtDocument.GetLineEndPosition(self.txtDocument.LineFromPosition(tend))
        #End Bugfix Chris Wilson

        mask = self.txtDocument.GetModEventMask()
        self.txtDocument.SetModEventMask(0)
        lpos = start
        newtext = ""
        ldocstring = len(self.prefs.doccommentstring[self.txtDocument.filetype])
        while lpos < end:
            lpos = self.txtDocument.PositionFromLine(startline)
            line = self.txtDocument.GetLine(startline)
            lc = line.find(self.prefs.doccommentstring[self.txtDocument.filetype])
            if lc > -1:
                prestyle = self.txtDocument.GetStyleAt(lpos + lc - 1)
                style = self.txtDocument.GetStyleAt(lpos + lc)
                if self.txtDocument.filetype == 1:
                    if not ((not (prestyle == wx.stc.STC_C_COMMENTLINE) and not (prestyle == wx.stc.STC_C_COMMENT) and not (prestyle == wx.stc.STC_C_COMMENTDOC)) and ((style == wx.stc.STC_C_COMMENTLINE) or (style == wx.stc.STC_C_COMMENT) or (style == wx.stc.STC_C_COMMENTDOC))):
                        newtext += line
                    else:
                        newtext += line[0:lc] + line[lc+ldocstring:]
                else:
                    if not ((not (prestyle == wx.stc.STC_P_COMMENTLINE) and not (prestyle == wx.stc.STC_P_COMMENTBLOCK)) and ((style == wx.stc.STC_P_COMMENTLINE) or (style == wx.stc.STC_P_COMMENTBLOCK))):
                        newtext += line
                    else:
                        newtext += line[0:lc] + line[lc+ldocstring:]
            else:
                newtext += line
            startline += 1
            lpos = self.txtDocument.PositionFromLine(startline)
        self.txtDocument.SetModEventMask(mask)
        self.txtDocument.SetSelection(start, end)
        self.txtDocument.ReplaceSelection(newtext.rstrip(self.txtDocument.GetEndOfLineCharacter()))

    def OnUndo(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.Undo()
        else:
            self.txtDocument.Undo()

    def OnUppercase(self, event):
        if self.txtPrompt.GetSTCFocus():
            self.txtPrompt.CmdKeyExecute(wx.stc.STC_CMD_UPPERCASE)
        else:
            self.txtDocument.CmdKeyExecute(wx.stc.STC_CMD_UPPERCASE)

    def OnViewAbout(self, event):
        import sAboutDialog
        sAboutDialog.Show(self)

    def OnViewHelp(self, event):
        self.ViewURLInBrowser(self.programdirectory + "/documentation/help.html")


    def OnViewInLeftPanel(self, event):
        self.viewinpaneltarget = 0

        self.ViewInPanelMenu(event)

    def OnViewInRightPanel(self, event):
        self.viewinpaneltarget = 1

        self.ViewInPanelMenu(event)

    def OnViewInTopPanel(self, event):
        self.viewinpaneltarget = 2

        self.ViewInPanelMenu(event)

    def OnViewPythonDocs(self, event):
        self.ViewURLInBrowser(self.prefs.documentationpythonlocation)

    def OnViewREHowtoDocs(self, event):
        self.ViewURLInBrowser(self.prefs.documentationrehowtolocation)

    def OnViewWxWidgetsDocs(self, event):
        self.ViewURLInBrowser(self.prefs.documentationwxwidgetslocation)

    def OnZoomIn(self, event):
        if self.txtPrompt.GetSTCFocus():
            zoom = self.txtPrompt.GetZoom()
            if zoom < 20:
                self.txtPrompt.SetZoom(zoom + 1)
        else:
            zoom = self.txtDocument.GetZoom()
            if zoom < 20:
                self.txtDocument.SetZoom(zoom + 1)

    def OnZoomOut(self, event):
        if self.txtPrompt.GetSTCFocus():
            zoom = self.txtPrompt.GetZoom()
            if zoom > -9:
                self.txtPrompt.SetZoom(zoom - 1)
        else:
            zoom = self.txtDocument.GetZoom()
            if zoom > -9:
                self.txtDocument.SetZoom(zoom - 1)

    def OpenFile(self, filename, OpenInNewTab, editrecentfiles = True, encoding='<Default Encoding>'):
        wx.BeginBusyCursor()
        self.PPost(self.EVT_SEER_FILE_OPENING)
        filename = os.path.abspath(filename).replace("\\", '/')
        if not os.path.exists(filename):
            self.ShowMessage(("Error Opening: " + filename), "Seer Error")
            wx.EndBusyCursor()
            return
        try:
            cfile = file(filename, 'rb')
        except:
            self.ShowMessage(("Error Opening: " + filename), "Seer Error")
            wx.EndBusyCursor()
            return
        if (self.txtDocument.untitlednumber > 0) and not OpenInNewTab:
            self.txtDocument.untitlednumber = -1
        if editrecentfiles:
            self.DestroyRecentFileMenu()
            if self.recentfiles.count(filename) != 0:
                self.recentfiles.remove(filename)
            if len(self.recentfiles) == self.prefs.recentfileslimit:
                self.recentfiles.pop()
            self.recentfiles.insert(0, filename)
            self.WriteRecentFiles()

        if (((not (self.txtDocument.filename == filename))) and (self.txtDocument.GetModify())) or OpenInNewTab:
            self.OnNew(None)

        self.txtDocumentArray[self.docPosition].filename = filename
        self.txtDocumentArray[self.docPosition].untitlednumber = -1

        try:
            oof = cfile.read()
            if not self.prefs.doconlyusedefaultsyntaxhighlighting:
                if self.checkiffileisPython(filename):
                    #Python
                    self.txtDocument.filetype = 0
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_PYTHON, True)
                elif self.checkiffileisCPP(filename):
                    #C/C++
                    self.txtDocument.filetype = 1
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_CPP, True)
                elif self.checkiffileisHTML(filename):
                    #HTML
                    self.txtDocument.filetype = 2
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_HTML, True)
                elif self.checkiffileisPlainText(filename):
                    #Plain Text
                    self.txtDocument.filetype = 3
                    self.highlightmenu.Check(self.ID_HIGHLIGHT_PLAIN_TEXT, True)
                else:
                    #Default
                    pass
                self.txtDocument.SetupPrefsDocument()

            #Encoding

            try:
                oof, e = sEncoding.EncodeText(self, oof, encoding, True)
                self.txtDocument.SetText(oof)
                self.txtDocument.SetEncoding(e)
            except:
                self.ShowMessage('There was an error opening the document %s.' % (filename), 'Open Error')
                wx.EndBusyCursor()
                self.OnClose(None)
                return

            self.txtDocument.EmptyUndoBuffer()
            self.txtDocument.SetSavePoint()
            cfile.close()

            self.txtDocument.SetupLineNumbersMargin()

            #Indentation Type:
            self.txtDocument.indentationtype = self.txtDocument.CheckIndentation()

            #Save Stat Info:
            self.txtDocument.mtime = int(os.stat(filename).st_mtime)

            self.txtDocument.SetScrollWidth(1)

            self.UpdateMenuAndToolbar()

            #Indentation
            if self.prefs.docusefileindentation:
                indentation = self.txtDocument.CheckIndentation(oof)
                if self.prefs.checkindentation:
                    if self.prefs.docusetabs[self.txtDocument.filetype]:
                        i = 1
                    else:
                        i = -1
                    if (indentation != i) and (indentation != 2):
                        answer = self.Ask((filename + ' is currently '\
                            + self.TABMESSAGE[indentation+1] +
                            ".\nWould you like to change it to the default?\nThe Default is: " +
                            self.TABMESSAGE[i+1]), "Indentation Not Default")
                        if answer:
                            indentation = i
                            if i == 1:
                                self.txtDocument.SetToTabs(self.prefs.doctabwidth[self.txtDocument.filetype])
                            else:
                                self.txtDocument.SetToSpaces(self.prefs.doctabwidth[self.txtDocument.filetype])
                if indentation == -1:
                    usetabs = False
                elif indentation == 1:
                    usetabs = True
                else:
                    usetabs = self.prefs.docusetabs[self.txtDocument.filetype]
                self.txtDocument.SetUseTabs(usetabs)
                self.txtDocument.SetupTabs(usetabs)

            #Line Endings

            self.txtDocument.lineendingsaremixed = 0

            winresult = self.relewin.search(oof)
            unixresult = self.releunix.search(oof)
            macresult = self.relemac.search(oof)

            win = winresult is not None
            unix = unixresult is not None
            mac = macresult is not None

            if (win + unix + mac) > 1:
                #Which came first, unix, mac, or win?
                first = -1
                useemode = 0
                if winresult is not None:
                    first = winresult.start()
                    useemode = 1
                if unixresult is not None:
                    if first == -1:
                        first = unixresult.start()
                    else:
                        i = unixresult.start()
                        if i < first:
                            first = i
                            useemode = 0
                if macresult is not None:
                    if first == -1:
                        first = macresult.start()
                    else:
                        i = macresult.start()
                        if i < first:
                            first = i
                            useemode = 2
                self.txtDocument.lineendingsaremixed = 1
                emodenum = useemode
            else:
                if win:
                    emodenum = 1
                elif unix:
                    emodenum = 0
                elif mac:
                    emodenum = 2
                else:
                    emodenum = self.prefs.doceolmode[self.txtDocument.filetype]
                self.txtDocument.lineendingsaremixed = 0

            dmodenum = self.prefs.doceolmode[self.txtDocument.filetype]

            if self.prefs.checkeol:
                if not emodenum == self.prefs.doceolmode[self.txtDocument.filetype]:
                    if self.txtDocument.lineendingsaremixed:
                        answer = self.Ask((filename + " is currently "+ self.FFMESSAGE[emodenum] +
                            "(Mixed).\nWould you like to change it to the default?\n(Since the file is mixed, this is highly recommended.\nThe Default is: " +
                            self.FFMESSAGE[dmodenum]), "Mixed Line Ending")
                    else:
                        answer = self.Ask((filename + " is currently " + self.FFMESSAGE[emodenum] +
                            ".\nWould you like to change it to the default?  The Default is: " +
                            self.FFMESSAGE[dmodenum]), "Line Ending")
                    if answer:
                        #Bugfix, Thanks Stephen Anderson.
                        if self.prefs.doceolmode[self.txtDocument.filetype] == 1:
                            self.OnFormatWinMode(None)
                        elif self.prefs.doceolmode[self.txtDocument.filetype] == 2:
                            self.OnFormatMacMode(None)
                        else:
                            self.OnFormatUnixMode(None)
                        self.txtDocument.lineendingsaremixed = 0
                        emodenum = dmodenum

            if emodenum == 1:
                emode = wx.stc.STC_EOL_CRLF
            elif emodenum == 2:
                emode = wx.stc.STC_EOL_CR
            else:
                emode = wx.stc.STC_EOL_LF
            self.txtDocument.SetEOLMode(emode)

            #/Line Endings

            #Scrolling
            lines = oof.split(self.txtDocument.GetEndOfLineCharacter())

            spaces = "\t".expandtabs(self.prefs.doctabwidth[self.txtDocument.filetype])

            line = ''
            length = 0
            x = 0
            for l in lines:
                if len(l) > length:
                    line = l
                    length = len(l)
                x += 1

            line = line.replace('\t', spaces) + '000'

            scrollwidth = self.txtDocument.TextWidth(wx.stc.STC_STYLE_DEFAULT, line)

            self.txtDocument.SetScrollWidth(scrollwidth)

            self.txtDocument.SetXOffset(0)
            #/End Scrolling

            self.txtDocument.OnModified(None)

            #Load SourceBrowser:
            if self.prefs.sourcebrowserisvisible:
                self.ShowSourceBrowser()

            #Refresh SourceBrowser:
            if self.SourceBrowser is not None:
                self.SourceBrowser.Browse()

            if editrecentfiles:
                self.ddirectory = os.path.dirname(filename)
        except:
            self.ShowMessage(("Error Opening: " + filename), "Seer Error")

        #The following chunk of code is an ugly way to work around a bug in wx.STC.
        #As things stand, word wrap may not update on file load.
        #This fixes the problem, by forcing seer to reset the wx.STC instances.
        if self.prefs.docwordwrap:
            x, y = self.GetSizeTuple()
            self.SetSize(wx.Size(x+1, y+1))
            self.SetSize(wx.Size(x, y))
        #End of the chunk.

        self.reloaddocumentsmenu()

        if editrecentfiles:
            self.CreateRecentFileMenu()

        self.PPost(self.EVT_SEER_FILE_OPENED)

        wx.EndBusyCursor()

    def PBind(self, eventtype, function, *args):
        self.spyevents.append((eventtype, function, args))

    def PPost(self, eventtype):
        for evt in self.spyevents:
            if evt[0] == eventtype:
                if evt[2]:
                    apply(evt[1], evt[2])
                else:
                    evt[1]()

    def PrintTraceback(self):
        slist = traceback.format_tb(sys.exc_info()[2])
        l = len(slist)
        if l > 0:
            x = 0
            rstring = ""
            while x < l:
                rstring = rstring + slist[x]
                x = x + 1
            tracebackstring = "Traceback (most recent call last):\n" + rstring \
            + str(sys.exc_info()[0]).lstrip("exceptions.") + ": " + str(sys.exc_info()[1])
            message = "\n\n\n" + tracebackstring
            print message

    def PUnbind(self, eventtype, function):
        x = 0
        for evt in self.spyevents:
            if (evt[0] == eventtype) and (evt[1] == function):
                self.spyevents.pop(x)
            else:
                x += 1

    def reloaddocumentsmenu(self):
        mnuitems = self.documentsmenu.GetMenuItems()
        num = len(mnuitems)
        x = 0
        while x < num:
            self.documentsmenu.Remove(mnuitems[x].GetId())
            #mnuitems[x].Destroy()
            x = x + 1

        self.setupdocumentsmenu()

    def RemovePluginIcon(self, name):
        toolbarfile = self.datdirectory + "/toolbar.custom.icons.dat"
        f = file(toolbarfile, 'r')
        lines = f.read().split('\n')
        f.close()
        name = "<Plugin>:" + name
        f = file(toolbarfile, 'w')
        for line in lines:
            if line:
                currentname = sPrefsFile.ExtractPreferenceFromText(line, "Name")
                if currentname != name:
                    f.write(line + '\n')
        f.close()

    def RemoveTrailingWhitespace(self, docPos):
        #only for python files?
        if self.prefs.docremovetrailingwhitespace and self.txtDocument.filetype == 0:

            text = self.txtDocumentArray[docPos].GetText()

            #newtext, n = self.retrailingwhitespace.subn('', text)

            #patch, 23.03.2006:
            newtext = re.sub(r"\s+[\n\r]+", lambda x: x.expand("\g<0>").lstrip(" \t\f\v"), text)

            if newtext != text:
                #save current line
                curline = self.txtDocumentArray[docPos].GetCurrentLine()
                self.txtDocumentArray[docPos].SetText(newtext)
                #jump to saved current line
                self.txtDocumentArray[docPos].GotoLine(curline)
                self.SetStatusText("Removed trailing whitespaces", 2)
            else:
                self.SetStatusText("", 2)


    def runcommand(self, command, statustext = "Running Command", pagetext="Prompt", redin="", redout = "", rederr=""):
        if self.txtPrompt.pid > -1:
            self.OnNewPrompt(None)
        self.promptnotebook.SetPageText(self.promptPosition, pagetext)

        self.txtPrompt.SetReadOnly(0)
        self.txtPrompt.SetText(command + '\n')
        if not self.mainpanel.PromptIsVisible:
            self.mainpanel.PromptIsVisible = True
            self.mainpanel.OnSize(None)
        self.promptnotebook.SetPageImage(self.promptPosition, 3)
        self.txtPrompt.SetScrollWidth(1)
        self.txtPrompt.editpoint = self.txtPrompt.GetLength()
        self.txtPrompt.GotoPos(self.txtPrompt.editpoint)
        self.SetStatusText(statustext, 2)
        self.txtPrompt.process = wx.Process(self)
        self.txtPrompt.process.Redirect()
        if self.PLATFORM_IS_WIN:
            self.txtPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC | wx.EXEC_NOHIDE, self.txtPrompt.process)
        else:
            self.txtPrompt.pid = wx.Execute(command, wx.EXEC_ASYNC, self.txtPrompt.process)
        self.txtPrompt.inputstream = self.txtPrompt.process.GetInputStream()
        self.txtPrompt.errorstream = self.txtPrompt.process.GetErrorStream()
        self.txtPrompt.outputstream = self.txtPrompt.process.GetOutputStream()

        self.txtPrompt.process.redirectOut = redout
        self.txtPrompt.process.redirectErr = rederr

        self.UpdateMenuAndToolbar()
        self.txtPrompt.SetFocus()

    def RunShortcuts(self, event, stc = None, SplitView = 0):
        return sShortcuts.RunShortcuts(self, event, stc, SplitView)

    def LoadDialogSizeAndPosition(self, dialog, dialogfile, defaultdir=''):
        if self.prefs.rememberdialogsizesandpositions:
            if not defaultdir:
                defaultdir = self.datdirectory
            sizeposfile = defaultdir + '/' + dialogfile
            try:
                if os.path.exists(sizeposfile):
                    f = file(sizeposfile, 'rb')
                    text = f.read()
                    f.close()
                    x, y, px, py = map(int, text.split('\n'))
                    dialog.SetSize((x, y))
                    dialog.Move(wx.Point(px, py))
            except:
                sScrolledMessageDialog.ShowMessage(dialog, 'Error Loading Dialog Size.  The file: "%s" may be corrupt.'\
                                                    % sizeposfile, 'Error')
        dialog.Bind(wx.EVT_CLOSE, dialog.OnCloseW)


    def SaveDialogSizeAndPosition(self, dialog, dialogfile, defaultdir=''):
        if self.prefs.rememberdialogsizesandpositions:
            try:
                if not defaultdir:
                    defaultdir = self.datdirectory
                f = file(defaultdir + '/' + dialogfile, 'wb')
                x, y = dialog.GetSizeTuple()
                px, py = dialog.GetPositionTuple()
                f.write(str(x) + '\n' + str(y) + '\n' + str(px) + '\n' + str(py))
                f.close()
            except:
                sScrolledMessageDialog.ShowMessage(dialog, "Error Saving Dialog Size", 'Error')

    def SaveFile(self, docPos, IsSaveAs = False, encoding='FromText'):
        self.PPost(self.EVT_SEER_FILE_SAVING)
        #Submitted Write Access Patch.
        #Edited slightly by Dan (one if statement, string format).
        if (not os.access(self.txtDocumentArray[docPos].filename, os.W_OK)) and \
            (os.path.exists(self.txtDocumentArray[docPos].filename)):
            self.ShowMessage('Error: Write Access: "%s"' % (self.txtDocumentArray[docPos].filename), 'Save Error')
            return False
        try:
            if self.prefs.backupfileonsave and not IsSaveAs:
                try:
                    shutil.copyfile(self.txtDocumentArray[docPos].filename, self.txtDocumentArray[docPos].filename+".bak")
                except:
                    self.ShowMessage(("Error Backing up to: " + self.txtDocumentArray[docPos].filename + ".bak"), "Seer Error")

            if encoding == 'FromText':
                encoding = self.txtDocumentArray[docPos].GetEncoding()

            self.RemoveTrailingWhitespace(docPos)

            ctext = sEncoding.DecodeText(self, self.txtDocumentArray[docPos].GetText(), encoding)

            cfile = file(self.txtDocumentArray[docPos].filename, 'wb')
            cfile.write(ctext)
            cfile.close()

            #Save Stat Info:
            self.txtDocumentArray[docPos].mtime = int(os.stat(self.txtDocumentArray[docPos].filename).st_mtime)
        except:
            self.ShowMessage(("Error Writing: " + self.txtDocumentArray[docPos].filename), "Seer Error")
            return False

        self.txtDocumentArray[docPos].SetSavePoint()
        self.txtDocumentArray[docPos].OnModified(None)

        if self.prefs.checksyntaxonsave:
            if self.prefs.checksyntaxextensions:
                exts = self.prefs.checksyntaxextensions.split()
                cext = os.path.splitext(self.txtDocumentArray[docPos].filename)[1][1:]
                if cext in exts:
                    self.CheckSyntax(docPos)
            else:
                self.CheckSyntax(docPos)

        self.PPost(self.EVT_SEER_FILE_SAVED)

        return True

    def setDocumentTo(self, number, ignoreold = 0):
        if not ignoreold:
            self.lastprogargsArray[self.docPosition] = self.lastprogargs
        #copy old finder limodou 2004/04/19
        oldfinder = self.txtDocumentArray[self.docPosition].Finder
        #end limodou

        self.docPosition = number
        self.txtDocument = self.txtDocumentArray[self.docPosition]

        #copy old finder limodou 2004/04/19
        self.txtDocument.Finder.Copy(oldfinder)
        #end limodou

        self.lastprogargs = self.lastprogargsArray[self.docPosition]

        self.currentpage = self.documentnotebook.GetPage(number)

        if self.txtDocument.filename:
            self.ddirectory = os.path.split(self.txtDocument.filename)[0]

        #franz: (Bad Argument).
        self.updatePrefsMDI()

        #Syntax Highlighting
        if self.txtDocument.filetype == 0:
            self.highlightmenu.Check(self.ID_HIGHLIGHT_PYTHON, True)
        if self.txtDocument.filetype == 1:
            self.highlightmenu.Check(self.ID_HIGHLIGHT_CPP, True)
        if self.txtDocument.filetype == 2:
            self.highlightmenu.Check(self.ID_HIGHLIGHT_HTML, True)
        if self.txtDocument.filetype == 3:
            #comment limodou 2004/04/13
            self.highlightmenu.Check(self.ID_HIGHLIGHT_PLAIN_TEXT, True)
            #end limodou

        if self.txtDocument.GetModify():
            if not self.txtDocument.filename:
                self.SetTitle("Seer - Untitled " + str(self.txtDocument.untitlednumber) + '[Modified]')
            else:
                self.SetTitle("Seer - " + self.txtDocument.filename + "[Modified]")
        else:
            if not self.txtDocument.filename:
                self.SetTitle("Seer - Untitled " + str(self.txtDocument.untitlednumber))
            else:
                self.SetTitle("Seer - " + self.txtDocument.filename)

        self.txtDocument.IsActive = True
        self.txtDocument.targetPosition = number
        self.txtDocument.OnModified(None)

        self.documentnotebook.SetSelection(self.docPosition)

        self.txtDocument.SetFocus()

        self.PPost(self.EVT_SEER_DOCUMENT_CHANGED)

    def setPromptTo(self, number):
        oldfinder = self.txtPromptArray[self.promptPosition].Finder

        self.promptPosition = number
        self.txtPrompt = self.txtPromptArray[self.promptPosition]

        self.txtPrompt.Finder.Copy(oldfinder)

        self.currentprompt = self.promptnotebook.GetPage(number)

        #franz: (Bad Argument).
        self.updatePrefsPromptMDI()

        if self.txtPromptArray[self.promptPosition].pid != -1:
            if self.txtPrompt.pythonintepreter:
                self.SetStatusText("Running Python Interpreter", 2)
            else:
                self.SetStatusText(("Running " + os.path.split(self.txtDocument.filename)[1]), 2)
        else:
            self.SetStatusText("", 2)

        self.promptnotebook.SetSelection(self.promptPosition)

    def setupdocumentsmenu(self):
        self.tabnavmenu = sMenu(self)
        self.tabnavmenu.Append(self.ID_NEXT_DOCUMENT, "Next Document")
        self.tabnavmenu.Append(self.ID_PREVIOUS_DOCUMENT, "Previous Document")
        self.tabnavmenu.Append(self.ID_FIRST_DOCUMENT, "First Document")
        self.tabnavmenu.Append(self.ID_LAST_DOCUMENT, "Last Document")
        self.documentsmenu.AppendMenu(self.ID_DOCUMENT_NAVIGATION_MENU, "Navigation", self.tabnavmenu)
        self.documentsmenu.AppendSeparator()
        self.documentsmenu.Append(self.ID_SAVE_ALL, "Save All Documents")
        self.documentsmenu.AppendSeparator()
        self.documentsmenu.Append(self.ID_CLOSE_ALL, "Close &All Documents")
        self.documentsmenu.Append(self.ID_CLOSE_ALL_OTHER_DOCUMENTS, "Close All &Other Documents")
        self.documentsmenu.AppendSeparator()

        #Sort it first
        def _get_title(x):
            return x.GetFilenameTitle()
        def _x(x):
            return x

        indextitles = map(_get_title, self.txtDocumentArray)
        sortedtitles = map(_x, indextitles)

        sortedtitles.sort()

        #End Sort

        x = 0
        l = len(self.txtDocumentArray)
        if l > 10:
            y = 0
            yl = 10
            if yl > l:
                yl = l
            a = 0
            self.documentsubmenus = []
            while y < yl:
                self.documentsubmenus.append(wx.Menu())
                self.documentsmenu.AppendMenu(self.ID_DOCUMENTS_MENU_BASE+a, sortedtitles[y] + " - " + sortedtitles[yl-1], self.documentsubmenus[a])
                while x < yl:
                    i = indextitles.index(sortedtitles[x])
                    self.documentsubmenus[a].Append(self.ID_DOCUMENTS_BASE+i, sortedtitles[x])
                    self.Bind(wx.EVT_MENU, self.OnSelectDocument, id=self.ID_DOCUMENTS_BASE+i)
                    x = x + 1
                if y == l:
                    break
                y = y + 10
                yl = yl + 10
                a = a + 1
                if yl > l:
                    yl = l
        else:
            while x < l:
                i = indextitles.index(sortedtitles[x])
                self.documentsmenu.Append(self.ID_DOCUMENTS_BASE+i, sortedtitles[x])
                self.Bind(wx.EVT_MENU, self.OnSelectDocument, id=self.ID_DOCUMENTS_BASE+i)
                x = x + 1

    def setupfiletypeextensions(self):

        self.refiletypeiscpp = re.compile(self.getfileextensionstring(1), re.IGNORECASE)
        self.refiletypeishtml = re.compile(self.getfileextensionstring(2), re.IGNORECASE)
        self.refiletypeistxt = re.compile(self.getfileextensionstring(3), re.IGNORECASE)
        self.refiletypeispy = re.compile(self.getfileextensionstring(0), re.IGNORECASE)

    def SetupToolBar(self):
        return sToolBarFile.SetupToolBar(self)

    def ShowMessage(self, msg, title='Seer'):
        sScrolledMessageDialog.ShowMessage(self, msg, title)

    def ShowSourceBrowser(self):
        if self.SourceBrowser is None:
            target, i = self.mainpanel.GetTargetNotebookPage(self.prefs.sourcebrowserpanel, 'Source Browser')
            self.SourceBrowser = sSourceBrowserPanel(target, -1, self.prefs.sourcebrowserpanel, i)
            self.mainpanel.SetPanelSize(self.prefs.sourcebrowserpanel, self.prefs.sourcebrowsersize)
            target.SetPanel(self.SourceBrowser)
            self.mainpanel.ShowPanel(self.prefs.sourcebrowserpanel, i)
        else:
            self.SourceBrowser.Browse()
            self.mainpanel.ShowPanel(self.SourceBrowser.position, self.SourceBrowser.Index, True)

    def ShowPrompt(self, Visible = True):
        if Visible:
            if self.mainpanel.PromptIsVisible:
                return
            self.mainpanel.PromptIsVisible = True
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  True)
            self.mainpanel.OnSize(None)
            self.txtPrompt.SetFocus()
        else:
            if not self.mainpanel.PromptIsVisible:
                return
            self.mainpanel.PromptIsVisible = False
            if self.hasToolBar:
                self.toolbar.ToggleTool(self.ID_TOGGLE_PROMPT,  False)
            self.mainpanel.OnSize(None)
            self.txtDocument.SetFocus()

    def UpdateMenuAndToolbar(self):
        isrunning = self.txtPrompt.pid != -1
        thereisafile = len(self.txtDocument.filename) > 0

        #Toolbar
        if self.hasToolBar:
            self.toolbar.EnableTool(self.ID_RELOAD, thereisafile)

            self.toolbar.EnableTool(self.ID_END, isrunning)

        #Menus
        self.filemenu.Enable(self.ID_RELOAD, thereisafile)
        self.filemenu.Enable(self.ID_RESTORE_FROM_BACKUP, thereisafile)

        if not isrunning:
            self.programmenu.Enable(self.ID_PYTHON, True)
            self.programmenu.Enable(self.ID_END, False)
            self.programmenu.Enable(self.ID_RUN, thereisafile)
        else:
            self.programmenu.Enable(self.ID_PYTHON, False)
            self.programmenu.Enable(self.ID_END, True)
            if thereisafile:
                self.programmenu.Enable(self.ID_RUN, False)

    #franz: oldprefs not used.
    def updatePrefsMDI(self):
        #Determine What is showing
        self.mainpanel.OnSize(None)

        self.Layout()

        self.UpdateMenuAndToolbar()

        #Shortcuts
        self.STCKeycodeArray = sShortcuts.SetSTCShortcuts(self.txtDocument, self.STCShortcuts, self.STCUseDefault)

    def updatePrefsPromptMDI(self):
        #Determine What is showing
        self.currentprompt.OnSize(None)

        self.Layout()

        self.UpdateMenuAndToolbar()

        #Shortcuts
        sShortcuts.SetSTCShortcuts(self.txtPrompt, self.STCShortcuts, self.STCUseDefault)

    def updatePrefs(self, oldprefs):
        self.bSizer.Remove(self.mainpanel)

        #Styling:
        for prompt in self.txtPromptArray:
            prompt.StyleResetDefault()
            prompt.StyleClearAll()
            prompt.SetupPrefsPrompt(0)

        for document in self.txtDocumentArray:
            document.StyleResetDefault()
            document.StyleClearAll()
            document.SetupPrefsDocument(0)

        self.mainpanel.OnSize(None)

        self.setupfiletypeextensions()

        #Find/Replace:
        if  (self.prefs.findreplaceregularexpression != oldprefs.findreplaceregularexpression) or \
        (self.prefs.findreplacematchcase != oldprefs.findreplacematchcase) or \
        (self.prefs.findreplacefindbackwards != oldprefs.findreplacefindbackwards) or \
        (self.prefs.findreplacewholeword != oldprefs.findreplacewholeword) or \
        (self.prefs.findreplaceinselection != oldprefs.findreplaceinselection) or \
        (self.prefs.findreplacefromcursor != oldprefs.findreplacefromcursor) or \
        (self.prefs.findreplacepromptonreplace != oldprefs.findreplacepromptonreplace):
            self.FindOptions = []
            self.ReplaceOptions = []

#       #SourceBrowser:
#       if not (self.prefs.sourcebrowserpanel == oldprefs.sourcebrowserpanel):
#           for document in self.txtDocumentArray:
#               if document.SourceBrowser:
#                   document.SourceBrowser = None

        #sScript:
        if self.prefs.sscriptloadexamples != oldprefs.sscriptloadexamples:
            self.sscriptmenu.reloadscripts()

        #Toolbar
        if self.prefs.iconsize > 0:
            if self.hasToolBar:
                self.DestroyToolBar()
                self.SetToolBar(None)
            self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)
            self.ToolBarIdList = self.SetupToolBar()
            self.SetToolBar(self.toolbar)
            self.hasToolBar = 1
        else:
            if self.hasToolBar:
                self.DestroyToolBar()
                self.SetToolBar(None)
                self.hasToolBar = 0

        if not (oldprefs.recentfileslimit == self.prefs.recentfileslimit):
            self.DestroyRecentFileMenu()
            self.recentfiles = []

            self.LoadRecentFiles()
            self.CreateRecentFileMenu()

        #Styling:
        self.txtDocument.StyleResetDefault()
        self.txtDocument.StyleClearAll()

        self.txtPrompt.StyleResetDefault()
        self.txtPrompt.StyleClearAll()

        self.txtDocument.SetupPrefsDocument(0)
        if self.txtDocument.GetViewWhiteSpace():
            self.txtDocument.SetViewEOL(self.prefs.vieweol)
        self.txtPrompt.SetupPrefsPrompt(0)
        if self.txtPrompt.GetViewWhiteSpace():
            self.txtPrompt.SetViewEOL(self.prefs.vieweol)

        if oldprefs.docfolding[self.txtDocument.filetype]:
            if not self.prefs.docfolding[self.txtDocument.filetype]:
                self.txtDocument.FoldAll(True)

        #Add The Stuff to the Sizer

        self.bSizer.Add(self.mainpanel, 1, wx.EXPAND)

        self.txtDocument.OnModified(None)
        self.txtDocument.OnPositionChanged(None)

        #Parenthesis Matching:
        if oldprefs.docparenthesismatching != self.prefs.docparenthesismatching:
            if not self.prefs.docparenthesismatching:
                #Clear Parenthesis Highlighting
                self.txtDocument.BraceBadLight(wx.stc.STC_INVALID_POSITION)
                self.txtDocument.BraceHighlight(wx.stc.STC_INVALID_POSITION, wx.stc.STC_INVALID_POSITION)

        self.Layout()

    def ViewInPanel(self, event):
        docnumber = event.GetId() - self.ID_VIEW_IN_PANEL_BASE

        target, i = self.mainpanel.GetTargetNotebookPage(self.viewinpaneltarget, "View In Panel")
        if docnumber < 0:
            ssplit = sSplitTextPanel(target, self, self.txtDocumentArray[self.docPosition], self.viewinpaneltarget, i)
        else:
            ssplit = sSplitTextPanel(target, self, self.txtDocumentArray[docnumber], self.viewinpaneltarget, i)
        target.SetPanel(ssplit)
        self.mainpanel.ShowPanel(self.viewinpaneltarget, i)

    def ViewInPanelMenu(self, event):
        docMenu = wx.Menu()
        x = 0
        l = len(self.txtDocumentArray)
        docMenu.Append(self.ID_VIEW_IN_PANEL_BASE-1, "Current Document")
        self.Bind(wx.EVT_MENU, self.ViewInPanel, id=self.ID_VIEW_IN_PANEL_BASE-1)
        docMenu.AppendSeparator()
        if l > 10:
            y = 0
            yl = 10
            if yl > l:
                yl = l
            a = 0
            docSubMenus = []
            while y < yl:
                docSubMenus.append(wx.Menu())
                docMenu.AppendMenu(self.ID_VIEW_IN_PANEL_BASE+a, str(y+1) + " - " + str(yl), docSubMenus[a])
                while x < yl:
                    if self.txtDocumentArray[x].filename:
                        docSubMenus[a].Append(self.ID_VIEW_IN_PANEL_BASE+x, os.path.basename(self.txtDocumentArray[x].filename))
                    else:
                        docSubMenus[a].Append(self.ID_VIEW_IN_PANEL_BASE+x, "Untitled " + str(self.txtDocumentArray[x].untitlednumber))
                    self.Bind(wx.EVT_MENU, self.ViewInPanel, id=self.ID_VIEW_IN_PANEL_BASE+x)
                    x = x + 1
                if y == l:
                    break
                y = y + 10
                yl = yl + 10
                a = a + 1
                if yl > l:
                    yl = l
        else:
            while x < l:
                if self.txtDocumentArray[x].filename:
                    docMenu.Append(self.ID_VIEW_IN_PANEL_BASE+x, os.path.basename(self.txtDocumentArray[x].filename))
                else:
                    docMenu.Append(self.ID_VIEW_IN_PANEL_BASE+x, "Untitled " + str(self.txtDocumentArray[x].untitlednumber))
                self.Bind(wx.EVT_MENU, self.ViewInPanel, id=self.ID_VIEW_IN_PANEL_BASE+x)
                x = x + 1

        self.PopupMenu(docMenu, self.ScreenToClient(wx.GetMousePosition()))
        docMenu.Destroy()

    def ViewURLInBrowser(self, url):
        if url.find('http:') == -1:
            url = os.path.normpath(url)
        if self.prefs.documentationbrowser == '<os.startfile>' and self.PLATFORM_IS_WIN:
            os.startfile(url)
            return
        wx.Execute((self.prefs.documentationbrowser + ' "' + url + '"'), wx.EXEC_ASYNC)

    def WriteRecentFiles(self):
        recentfiles = self.datdirectory + "/recent_files.log"
        try:
            fin = open(recentfiles, 'w')
            x = 0
            length = len(self.recentfiles)
            while (x < self.prefs.recentfileslimit) and (x < length):
                fin.write(self.recentfiles[x] + '\n')
                x = x + 1
            fin.close()
        except IOError:
            self.ShowMessage("Error Writing: " + recentfiles, "Recent Files Error")

    #Initialize menus for Advanced mode (more items)
    def CreateMenus(self):
        self.filemenu = sMenu(self)
        self.filemenu.Append(self.ID_NEW, 'New', False, 0)
        self.filemenu.Append(self.ID_OPEN, 'Open', True, 0)
        self.filemenu.Append(self.ID_OPEN_IMPORTED_MODULE, 'Open Imported Module', True)
        self.recentmenu = wx.Menu()
        self.CreateRecentFileMenu()
        self.filemenu.AppendMenu(self.ID_OPEN_RECENT, "Open Recent", self.recentmenu)
        self.filemenu.Append(self.ID_RELOAD, 'Reload File', False, 0)
        self.filemenu.Append(self.ID_RESTORE_FROM_BACKUP, 'Restore From Backup')
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_CLOSE, 'Close', False, 0)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_CLEAR_RECENT, 'Clear Recent File List')
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_SAVE, 'Save', False, 0)
        self.filemenu.Append(self.ID_SAVE_AS, 'Save As', True, 5)
        self.filemenu.Append(self.ID_SAVE_COPY, 'Save A Copy', True, 7)
        self.filemenu.Append(self.ID_SAVE_PROMPT, 'Save Prompt Output To File', True)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_PRINT_SETUP, 'Print Setup', True)
        self.filemenu.Append(self.ID_PRINT, 'Print File', True, 0)
        self.filemenu.Append(self.ID_PRINTPROMPT, 'Print Prompt', True)
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_EXIT, 'Exit', False, 1)

        self.commentmenu = sMenu(self)
        self.commentmenu.Append(self.ID_COMMENT_REGION, 'Comment')
        self.commentmenu.Append(self.ID_UNCOMMENT_REGION, 'UnComment')

        self.whitespacemenu = sMenu(self)
        self.whitespacemenu.Append(self.ID_INDENT_REGION, 'Indent', False, 0)
        self.whitespacemenu.Append(self.ID_DEDENT_REGION, 'Dedent', False, 0)
        self.whitespacemenu.AppendSeparator()
        self.whitespacemenu.Append(self.ID_CHECK_INDENTATION, "Check Indentation Type...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_TABS, "Set Indentation To Tabs...")
        self.whitespacemenu.Append(self.ID_CLEAN_UP_SPACES, "Set Indentation To Spaces...")
        self.whitespacemenu.AppendSeparator()
        self.whitespacemenu.Append(self.ID_UNIXMODE, "Set Line Endings To Unix Mode (\"\\n\')")
        self.whitespacemenu.Append(self.ID_WINMODE, "Set Line Endings To DOS/Windows Mode (\"\\r\\n\')")
        self.whitespacemenu.Append(self.ID_MACMODE, "Set Line Endings To Mac Mode (\"\\r\')")

        self.casemenu = sMenu(self)
        self.casemenu.Append(self.ID_UPPERCASE, 'Uppercase', False, 0)
        self.casemenu.Append(self.ID_LOWERCASE, 'Lowercase', False, 0)

        self.editmenu = sMenu(self)

        self.editmenu.Append(self.ID_UNDO, 'Undo', False, 0)
        self.editmenu.Append(self.ID_REDO, 'Redo', False, 1)
        self.editmenu.AppendSeparator()

        #Order changed by seer
        ##for keyboard macro (Keyboardmacro) recording; #ugly hack franz # removed again

        self.editmenu.Append(self.ID_CUT, 'Cut')
        self.editmenu.Append(self.ID_COPY, 'Copy')
        self.editmenu.Append(self.ID_PASTE, 'Paste')
        ##end patch keyboard macro recording #end ugly hack franz # removed again

        self.editmenu.Append(self.ID_DELETE, 'Delete')

        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_SELECT_ALL, 'Select All')
        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_INSERT_SEPARATOR, 'Insert Separator', True)
        self.editmenu.Append(self.ID_INSERT_REGEX, 'Insert Regular Expression', True)
        self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_FIND_AND_COMPLETE, 'Find And Complete')
        self.editmenu.AppendSeparator()
        self.editmenu.AppendMenu(self.ID_COMMENT, "&Comments", self.commentmenu)
        self.editmenu.AppendMenu(self.ID_WHITESPACE, "&Whitespace", self.whitespacemenu)
        self.editmenu.AppendMenu(self.ID_CASE, "Case", self.casemenu)

        self.searchmenu = sMenu(self)
        self.searchmenu.Append(self.ID_FIND, 'Find', True, 0)
        self.searchmenu.Append(self.ID_FIND_NEXT, 'Find Next', False, 5)
        self.searchmenu.Append(self.ID_FIND_PREVIOUS, 'Find Previous')
        self.searchmenu.Append(self.ID_REPLACE, 'Replace', True, 0)

        self.foldmenu = sMenu(self)
        self.foldmenu.Append(self.ID_TOGGLE_FOLD, 'Toggle Fold', False, 0)
        self.foldmenu.Append(self.ID_FOLD_ALL, 'Fold All', False, 0)
        self.foldmenu.Append(self.ID_EXPAND_ALL, 'Expand All', False, 0)

        self.highlightmenu = sMenu(self)
        self.highlightmenu.AppendRadioItem(self.ID_HIGHLIGHT_PYTHON, "Python")
        self.highlightmenu.AppendRadioItem(self.ID_HIGHLIGHT_CPP, "C/C++")
        self.highlightmenu.AppendRadioItem(self.ID_HIGHLIGHT_HTML, "HTML")
        self.highlightmenu.AppendRadioItem(self.ID_HIGHLIGHT_PLAIN_TEXT, "Plain Text")
        self.highlightmenu.Check(self.ID_HIGHLIGHT_PYTHON, True)

        self.viewinpanelmenu = sMenu(self)
        self.viewinpanelmenu.Append(self.ID_VIEW_IN_LEFT_PANEL, 'View In Left Panel')
        self.viewinpanelmenu.Append(self.ID_VIEW_IN_RIGHT_PANEL, 'View In Right Panel')
        self.viewinpanelmenu.Append(self.ID_VIEW_IN_TOP_PANEL, 'View In Top Panel')

        self.gotomenu = sMenu(self)
        self.gotomenu.Append(self.ID_GOTO_BLOCK_START, 'Go To Block Start', False, -1, 'Block Start')
        self.gotomenu.Append(self.ID_GOTO_BLOCK_END, 'Go To Block End', False, -1, 'Block End')
        self.gotomenu.Append(self.ID_GOTO_CLASS_START, 'Go To Class Start', False, -1, 'Class Start')
        self.gotomenu.Append(self.ID_GOTO_CLASS_END, 'Go To Class End', False, -1, 'Class End')
        self.gotomenu.Append(self.ID_GOTO_DEF_START, 'Go To Def Start', False, -1, 'Def Start')
        self.gotomenu.Append(self.ID_GOTO_DEF_END, 'Go To Def End', False, -1, 'Def End')

        self.viewmenu = sMenu(self)
        self.viewmenu.Append(self.ID_GOTO, 'Go To', True, 0)
        self.viewmenu.AppendMenu(self.ID_GOTO_MENU, "Go To", self.gotomenu)
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(self.ID_ZOOM_IN, 'Zoom In', False, 5)
        self.viewmenu.Append(self.ID_ZOOM_OUT, 'Zoom Out', False, 5)
        self.viewmenu.AppendSeparator()
        self.viewmenu.AppendMenu(self.ID_FOLDING, "&Folding", self.foldmenu)
        self.viewmenu.AppendSeparator()
        self.viewmenu.AppendMenu(self.ID_VIEW_IN_PANEL, "&View In Panel", self.viewinpanelmenu)
        self.viewmenu.AppendSeparator()
        self.viewmenu.AppendMenu(self.ID_HIGHLIGHT, "&Syntax Highlighting", self.highlightmenu)
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(self.ID_TOGGLE_SOURCEBROWSER, 'Toggle Source Browser')
        self.viewmenu.Append(self.ID_SOURCEBROWSER_GOTO, 'Source Browser Go To', True)
        self.viewmenu.AppendSeparator()
        #fix bug someone refered in forum limodou 2004/04/20
        self.viewmenu.Append(self.ID_TOGGLE_VIEWWHITESPACE, 'Toggle View Whitespace', False, 12)
        #end limodou
        self.viewmenu.Append(self.ID_TOGGLE_PROMPT, 'Toggle Prompt')

        self.programmenu = sMenu(self)
        self.programmenu.Append(self.ID_CHECK_SYNTAX, 'Check Syntax')
        self.programmenu.AppendSeparator()
        self.programmenu.Append(self.ID_RUN, 'Run')
        self.programmenu.Append(self.ID_SET_ARGS, 'Set Arguments', True)
        self.programmenu.Append(self.ID_PYTHON, 'Python', False, -1, 'Open a Python Interpreter')
        self.programmenu.Append(self.ID_END, 'End')
        self.programmenu.Append(self.ID_CLOSE_PROMPT, 'Close Prompt')
        # Feb 17 - adding PyDoc menu items
        self.programmenu.AppendSeparator()
        self.programmenu.Append(self.ID_PYDOC_CURR, self.getmenulabel('Pydoc Current File'))
        self.programmenu.Append(self.ID_PYDOC_ALL, self.getmenulabel('Pydoc All Open Files'))
        self.programmenu.Append(self.ID_VIEW_PYDOC, self.getmenulabel('Browse PyDoc...'))
        # End Pydoc changes

        self.bookmarksmenu = sBookmarksMenu(self)
        self.sscriptmenu = sScriptMenu(self)

        self.txtDocument.OnModified(None)

        #sScript Shortcuts
        self.sScriptShortcutsAction = self.sscriptmenu.OnScript

        self.pluginsconfiguremenu = sPluginConfigureMenu(self)
        self.pluginsindexmenu = sPluginIndexMenu(self)
        self.pluginsprefsmenu = sPluginPreferencesMenu(self)

        self.documentsmenu = sMenu(self)
        self.setupdocumentsmenu()

        self.optionsmenu = sMenu(self)
        self.optionsmenu.Append(self.ID_PREFS, 'Preferences', True, 0)
        self.optionsmenu.Append(self.ID_SHORTCUTS, 'Customize Shortcuts', True, 0)
        self.optionsmenu.Append(self.ID_POPUP, 'Customize Pop Up Menu', True)
        self.optionsmenu.Append(self.ID_CUSTOMIZE_TOOLBAR, 'Customize ToolBar', True)
        self.optionsmenu.AppendSeparator()
        self.optionsmenu.Append(self.ID_EDIT_BOOKMARKS, 'Edit Bookmarks', True, 0)
        self.optionsmenu.Append(self.ID_EDIT_SCRIPT_MENU, 'Edit Script Menu', True)
        self.optionsmenu.AppendSeparator()
        self.optionsmenu.AppendMenu(self.ID_CONFIGURE_PLUGINS, "&Configure Plugins", self.pluginsconfiguremenu)
        self.optionsmenu.AppendMenu(self.ID_PLUGIN_PREFS, "Plugin Preferences", self.pluginsprefsmenu)
        self.optionsmenu.AppendMenu(self.ID_LOAD_PLUGIN, "&Load Plugin(s) From Index", self.pluginsindexmenu)

        self.pluginshelpmenu = sPluginHelpMenu(self)
        self.pluginsaboutmenu = sPluginAboutMenu(self)

        self.helpmenu = sMenu(self)
        self.helpmenu.Append(self.ID_ABOUT, "&About Seer...")
        self.helpmenu.AppendMenu(self.ID_PLUGIN_ABOUT, "About Plugin", self.pluginsaboutmenu)
        self.helpmenu.AppendSeparator()
        self.helpmenu.Append(self.ID_HELP, 'Help', True, 0, 'Seer &Help...')
        self.helpmenu.AppendMenu(self.ID_PLUGIN_HELP, "Plugin Help", self.pluginshelpmenu)
        self.helpmenu.AppendSeparator()
        self.helpmenu.Append(self.ID_PYTHON_DOCS, 'View Python Docs', True)
        self.helpmenu.Append(self.ID_WXWIDGETS_DOCS, 'View WxWidgets Docs', True)
        self.helpmenu.Append(self.ID_REHOWTO_DOCS, 'View Regular Expression Howto', True)

        self.menuBar = wx.MenuBar()
        #ugly hack workaround
        #in linux, if there is a menu accelerator, the hotkeys are not working anymore.
        menuBarNamesWin32 = ["&File", "&Edit", "&Search", "&View", "&Program", "&Bookmarks",
                          "D&rScript", "&Documents", "&Options", "&Help"]

        menuBarNamesGtk = ["File", "Edit", "Search", "View", "Program", "Bookmarks",
                          "sScript", "Documents", "Options", "Help"]
        if self.PLATFORM_IS_WIN:
            menuBarNames = menuBarNamesWin32
        else:
            menuBarNames = menuBarNamesGtk

        self.menuBar.Append(self.filemenu, menuBarNames[0])
        self.menuBar.Append(self.editmenu, menuBarNames[1])
        self.menuBar.Append(self.searchmenu, menuBarNames[2])
        self.menuBar.Append(self.viewmenu, menuBarNames[3])
        self.menuBar.Append(self.programmenu, menuBarNames[4])
        self.menuBar.Append(self.bookmarksmenu, menuBarNames[5])
        self.menuBar.Append(self.sscriptmenu, menuBarNames[6])
        self.menuBar.Append(self.documentsmenu, menuBarNames[7])
        self.menuBar.Append(self.optionsmenu, menuBarNames[8])
        self.menuBar.Append(self.helpmenu, menuBarNames[9])

        self.SetMenuBar(self.menuBar)
        self.SetToolbar()

    def SetToolbar(self):
        if self.hasToolBar:
            self.DestroyToolBar()
            self.SetToolBar(None)
        try:
            #AB
            self.ToolBarList = sToolBarFile.getToolBarList(self.datdirectory)
        except:
            self.ShowMessage("Error Loading ToolBar List", "Seer Error")

        if self.prefs.iconsize > 0:
            self.hasToolBar = True
            self.toolbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)

            self.ToolBarIdList = self.SetupToolBar()

            self.SetToolBar(self.toolbar)

    # lm - adding helper functions

    def promptSaveAll(self):
        """ check if there are any open unsaved files, and prompt the user to save each """
        x = 0
        while x < len(self.txtDocumentArray):
            if self.txtDocumentArray[x].GetModify():
                if self.Ask('Would you like to save "%s"?' % self.txtDocumentArray[x].GetFilename(), "Seer"):
                    self.setDocumentTo(x)
                    self.OnSave(None)
            x += 1

    def promptSaveCurrent(self):
        """ ask the user if they would like to save the current file """
        if self.txtDocument.GetModify():
            if self.Ask('Would you like to save "%s"?' % self.txtDocument.GetFilename(), "Seer"):
                self.OnSave(None)

    def promptDir(self, msg):
        """ open a directory browser and return the directory chosen """
        d = wx.DirDialog(self, msg, style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON|wx.MAXIMIZE_BOX|wx.THICK_FRAME)
        dir = ''
        if d.ShowModal() == wx.ID_OK:
            dir = d.GetPath()
        d.Destroy()
        return dir

class sApp(wx.App):

    def OnInit(self):

        #lc = wx.Locale(wx.LANGUAGE_DEFAULT)
        #_ = wx.GetTranslation
        #lc.AddCatalogLookupPathPrefix('locale')
        #lc.AddCatalog('seer')

        self.frame = sFrame(None, 101, "Seer - Untitled 1")

        self.frame.Show(True)

        self.SetTopWindow(self.frame)

        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

        return True

    def OnActivate(self, event):
        if event.GetActive():
            self.frame.OnActivate()
        event.Skip()

def main():
    app = sApp(0)
    # load files from command line parameters
    if len(sys.argv) > 1:
        app.frame.OpenFile(sys.argv[1], False)
        if len(sys.argv) > 2:
            for f in sys.argv[2:]:
                try:
                    app.frame.OpenFile(f, True)
                except:
                    print "Error opening file %r" % f
    app.MainLoop()


if __name__ == '__main__':
    main()

