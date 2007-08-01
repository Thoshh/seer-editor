#!/usr/bin/env python
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

        self.ID_EXPORT_SEERSCRIPTS = 507
        self.ID_IMPORT_SEERSCRIPTS = 518h

        self.btnExportAll = wx.Button(self, self.ID_EXPORT_ALL, 'Export Preferences, Plugins, sScripts To Zip')
        self.btnImportAll = wx.Button(self, self.ID_IMPORT_ALL, 'Import Preferences, Plugins, sScripts From Zip')
        self.btnExportPrefs = wx.Button(self, self.ID_EXPORT_PREFS, 'Export Preferences To Zip')
        self.btnImportPrefs = wx.Button(self, self.ID_IMPORT_PREFS, 'Import Preferences From Zip')
        self.btnExportPlugins = wx.Button(self, self.ID_EXPORT_PLUGINS, 'Export Plugins To Zip')
        self.btnImportPlugins = wx.Button(self, self.ID_IMPORT_PLUGINS, 'Import Plugins From Zip')
        self.btnExportsScripts = wx.Button(self, self.ID_EXPORT_SEERSCRIPTS, 'Export sScripts To Zip')
        self.btnImportsScripts = wx.Button(self, self.ID_IMPORT_SEERSCRIPTS, 'Import sScripts From Zip')

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
        self.theSizer.Add(self.btnExportsScripts, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.theSizer.Add(self.btnImportsScripts, 0, wx.SHAPED | wx.ALIGN_CENTER)
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
        self.Bind(wx.EVT_BUTTON, self.OnExportsScripts, id=self.ID_EXPORT_SEERSCRIPTS)
        self.Bind(wx.EVT_BUTTON, self.OnImportsScripts, id=self.ID_IMPORT_SEERSCRIPTS)

    def OnExportAll(self, event):
        dlg = sFileDialog.FileDialog(self.sframe, "Export Preferences, Plugins, and sScripts To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace("\\", "/")
            sZip.ExportPreferencesTo(self.sframe.pluginsdirectory, self.sframe.preferencesdirectory,
                                      self.sframe.datdirectory, filename)

        dlg.Destroy()

    def OnExportsScripts(self, event):
        dlg = sFileDialog.FileDialog(self.sframe, "Export sScripts To", 'Zip File (*.zip)|*.zip', IsASaveDialog=True)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath().replace("\\", "/")
            sZip.ExportsScriptsTo(self.sframe.preferencesdirectory, filename)

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
                                      self.sframe.datdirectory, filename, plugins=False, sscripts=False)

        dlg.Destroy()

    def OnImportAll(self, event):
        if self.sframe.Ask('This will permanently overwrite all of your preferences, plugins, and sscript file.\n\nProceed?', 'Warning'):
            dlg = sFileDialog.FileDialog(self.sframe, "Import Preferences, Plugins, and sScripts From", 'Zip File (*.zip)|*.zip')

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace("\\", "/")
                sZip.ImportPreferencesFrom(self.sframe.preferencesdirectory, filename)
                self.sframe.ShowMessage('Successfully imported preferences, plugins, and sscripts.', 'Import Success')

            dlg.Destroy()

    def OnImportsScripts(self, event):
        if self.sframe.Ask('This will permanently overwrite all of your sscript file.\n\nProceed?', 'Warning'):
            dlg = sFileDialog.FileDialog(self.sframe, "Import sScripts From", 'Zip File (*.zip)|*.zip')

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath().replace("\\", "/")
                sZip.ImportsScriptsFrom(self.sframe.preferencesdirectory, filename)
                self.sframe.ShowMessage('Successfully imported sscripts.', 'Import Success')

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