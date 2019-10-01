# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#

import os

import wx

from photofilmstrip.lib.Settings import Settings


class PnlEditorPage(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, name=wx.PanelNameStr):
        wx.Panel.__init__(self, parent, id, name=name)
        self.__hasChanged = False

    def __Save(self, filepath):
        try:
            return self._Save(filepath)
        except Exception as err:
            dlg = wx.MessageDialog(self.GetParent(),
                                   _(u"Could not save the file '%(file)s': %(errMsg)s") % \
                                            {'file': filepath,
                                             'errMsg': str(err)},
                                   _(u"Question"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def SetChanged(self, changed=True):
        self.__hasChanged = changed

    def HasChanged(self):
        return self.__hasChanged

    def CheckAndAskSaving(self):
        if self.HasChanged():
            filepath = self.GetSaveFilePath()
            if filepath is None:
                filepath = _(u"New file")

            dlg = wx.MessageDialog(self.GetParent(),
                                   _(u"'%s' has been modified. Save changes?") % filepath,
                                   _(u"Question"),
                                   wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION)
            response = dlg.ShowModal()
            dlg.Destroy()

            if response == wx.ID_CANCEL:
                return False
            elif response == wx.ID_YES and not self.OnSave():
                return False
        return True

    def OnSave(self):
        curFilePath = self.GetSaveFilePath()
        if curFilePath is None:
            return self.OnSaveAs()
        elif self.__Save(curFilePath):
            self.SetChanged(False)
            return True
        else:
            return False

    def OnSaveAs(self):
        curFilePath = self.GetSaveFilePath()
        if curFilePath is None:
            curFilePath = "{0}{1}".format(self._GetEditorName(), self.GetFileExtension())
        dlg = wx.FileDialog(self.GetParent(), _(u"Save %s") % self._GetEditorName(),
                            self._GetDefaultSaveFolder(),
                            curFilePath,
                            self._GetEditorName() + u'-' + _(u"File") + " (*{0})|*{0}".format(self.GetFileExtension()),
                            wx.FD_SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filepath = dlg.GetPath()
                if os.path.splitext(filepath)[1].lower() != self.GetFileExtension():
                    filepath += self.GetFileExtension()

                if os.path.isfile(filepath):
                    dlg2 = wx.MessageDialog(self.GetParent(),
                                            _(u"Overwrite existing file '%s'?") % filepath,
                                            _(u"Question"),
                                            wx.YES_NO | wx.ICON_QUESTION)
                    try:
                        if dlg2.ShowModal() == wx.ID_NO:
                            return False
                    finally:
                        dlg2.Destroy()

                if self.__Save(filepath):
                    self.SetChanged(False)
                    return True
                else:
                    return False
        finally:
            dlg.Destroy()

    def _GetDefaultSaveFolder(self):
        return Settings().GetProjectPath()

    def _GetEditorName(self):
        raise NotImplementedError()

    def _Save(self, filepath):
        raise NotImplementedError()

    def GetProject(self):
        raise NotImplementedError()

    def GetFileExtension(self):
        raise NotImplementedError()

    def GetStatusText(self, index):
        raise NotImplementedError()

    def GetSaveFilePath(self):
        raise NotImplementedError()

    def AddMenuFileActions(self, menu):
        pass

    def AddMenuEditActions(self, menu):
        pass

    def AddToolBarActions(self, toolBar):
        pass

    def ConnectEvents(self, evtHandler):
        pass

    def DisconnEvents(self, evtHandler):
        pass

    def OnStatusBarClick(self, index):
        pass
