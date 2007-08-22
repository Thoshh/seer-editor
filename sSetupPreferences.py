#!/usr/bin/env python

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

#This is a module for a gui for importing / exporting preferences.

import wx
import sZip
import sFileDialog

class sSetupPreferencesDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'Setup Preferences', style=wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)

        self.parent = parent

        self.sframe = parent.sframe

        self.ID_EXPORT_ALL = 501
        self.ID_IMPORT_ALL = 502

        self.ID_EXPORT_PREFS = 503
        self.ID_IMPORT_PREFS = 504

        self.ID_EXPORT_PLUGINS = 505
        self.ID_IMPORT_PLUGINS = 506

        self.btnExportAll = wx.Button(self, self.ID_EXPORT_ALL, 'Export Preferences, Plugins To Zip')
        self.btnImportAll = wx.Button(self, self.ID_IMPORT_ALL, 'Import Preferences, Plugins From Zip')
        self.btnExportPrefs = wx.Button(self, self.ID_EXPORT_PREFS, 'Export Preferences To Zip')
        self.btnImportPrefs = wx.Button(self, self.ID_IMPORT_PREFS, 'Import Preferences From Zip')
        self.btnExportPlugins = wx.Button(self, self.ID_EXPORT_PLUGINS, 'Export Plugins To Zip')
        self.btnImportPlugins = wx.Button(self, self.ID_IMPORT_PLUGINS, 'Import Plugins From Zip')

        self.btnExit = wx.Button(self, wx.ID_CANCEL, 'Exit')

        self.theSizer = wx.BoxSizer(wx.VERTICAL)

        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)
        self.theSizer.Add(self.btnExportAll, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.btnImportAll, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)
        self.theSizer.Add(self.btnExportPrefs, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.btnImportPrefs, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)
        self.theSizer.Add(self.btnExportPlugins, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.btnImportPlugins, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)
        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)
        self.theSizer.Add(self.btnExit, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(wx.StaticText(self, -1, '   '), 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizerAndFit(self.theSizer)

        self.Bind(wx.EVT_BUTTON, self.OnExportAll, id=self.ID_EXPORT_ALL)
        self.Bind(wx.EVT_BUTTON, self.OnImportAll, id=self.ID_IMPORT_ALL)
        self.Bind(wx.EVT_BUTTON, self.OnExportPrefs, id=self.ID_EXPORT_PREFS)
        self.Bind(wx.EVT_BUTTON, self.OnImportPrefs, id=self.ID_IMPORT_PREFS)
        self.Bind(wx.EVT_BUTTON, self.OnExportPlugins, id=self.ID_EXPORT_PLUGINS)
        self.Bind(wx.EVT_BUTTON, self.OnImportPlugins, id=self.ID_IMPORT_PLUGINS)

    def OnExportAll(self, event):
        dlg = sFileDialog.FileDialog(self.sframe, "Export Preferences and Plugins To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace("\\", "/")
            sZip.ExportPreferencesTo(self.sframe.pluginsdirectory, self.sframe.preferencesdirectory,
                                      self.sframe.datdirectory, filename)

        dlg.Destroy()

    def OnExportPlugins(self, event):
        dlg = sFileDialog.FileDialog(self.sframe, "Export Plugins To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace("\\", "/")
            sZip.ExportDirectoryTo(self.sframe.pluginsdirectory, filename, 'plugins')

        dlg.Destroy()

    def OnExportPrefs(self, event):
        dlg = sFileDialog.FileDialog(self.sframe, "Export Preferences To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace("\\", "/")
            sZip.ExportPreferencesTo(self.sframe.pluginsdirectory, self.sframe.preferencesdirectory,
                                      self.sframe.datdirectory, filename, plugins=False)

        dlg.Destroy()

    def OnImportAll(self, event):
        if self.sframe.Ask('This will permanently overwrite all of your preferences and plugins file.\n\nProceed?', 'Warning'):
            dlg = sFileDialog.FileDialog(self.sframe, "Import Preferences and Plugins From", 'Zip File (*.zip)|*.zip')

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace("\\", "/")
                sZip.ImportPreferencesFrom(self.sframe.preferencesdirectory, filename)
                self.sframe.ShowMessage('Successfully imported preferences and plugins.', 'Import Success')

            dlg.Destroy()

    def OnImportPlugins(self, event):
        if self.sframe.Ask('This will permanently overwrite all of your plugins.\n\nProceed?', 'Warning'):
            dlg = sFileDialog.FileDialog(self.sframe, "Import Plugins From", 'Zip File (*.zip)|*.zip')

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace("\\", "/")
                sZip.ImportPluginsFrom(self.sframe.preferencesdirectory, filename)
                self.sframe.ShowMessage('Successfully imported plugins.', 'Import Success')

            dlg.Destroy()

    def OnImportPrefs(self, event):
        if self.sframe.Ask('This will permanently overwrite all of your preferences.\n\nProceed?', 'Warning'):
            dlg = sFileDialog.FileDialog(self.sframe, "Import Preferences From", 'Zip File (*.zip)|*.zip')

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace("\\", "/")
                sZip.ImportJustPreferencesFrom(self.sframe.preferencesdirectory, filename)
                self.sframe.ShowMessage('Successfully imported preferences.', 'Import Success')

            dlg.Destroy()