# encoding: UTF-8

import time

import wx

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.core.ProjectFile import ProjectFile

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.WxVisualJobHandler import EVT_JOB_RESULT, WxInteractionEvent

from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.DlgJobVisual import DlgJobVisual


class WxProjectFile(ProjectFile):

    def __init__(self, wxParent, project=None, filename=None):
        ProjectFile.__init__(self, project, filename)
        self.__wxParent = wxParent
        self.__wxvJob = None
        self.__resultEvent = None

    def __WaitUntilJobDone(self):
        while self.__resultEvent is None:
            if wx.Thread_IsMain():
                wx.Yield()
            time.sleep(0.05)
        self.__wxvJob = None
        try:
            return self.__resultEvent.GetResult()
        finally:
            self.__resultEvent = None

    def __OnJobDone(self, event):
        self.__resultEvent = event

    def __Load(self, importPath, job=None):
        return ProjectFile.Load(self, importPath)

    def __Save(self, includePics, job=None):
        return ProjectFile.Save(self, includePics)

    def _SelectAlternatePath(self, imgPath):
        sapEvent = SelectAlternatePathEvent(imgPath)
        self.__wxvJob._Interact(sapEvent)

    def _StepProgress(self, msg):
        self.__wxvJob.StepProgress(msg)

    def Load(self, importPath=None):
        wxvJob = VisualJob(_("Loading project %s") % self._filename,
                           self.__Load, args=(importPath,))
        wxvJob.SetAltPath = self.SetAltPath
        dlg = DlgJobVisual(self.__wxParent, wxvJob)
        dlg.Bind(EVT_JOB_RESULT, self.__OnJobDone)

        wxvJob.AddVisualJobHandler(dlg)

        self.__wxvJob = wxvJob
        JobManager().EnqueueContext(wxvJob)
        try:
            return self.__WaitUntilJobDone()
        finally:
            dlg.Destroy()

    def Save(self, includePics=False):
        wxvJob = VisualJob(_("Saving project %s") % self._filename,
                           self.__Save, args=(includePics,),
                           maxProgress=len(self._project.GetPictures()))

        dlg = DlgJobVisual(self.__wxParent, wxvJob)
        dlg.Bind(EVT_JOB_RESULT, self.__OnJobDone)

        wxvJob.AddVisualJobHandler(dlg)

        self.__wxvJob = wxvJob
        JobManager().EnqueueContext(wxvJob)
        try:
            return self.__WaitUntilJobDone()
        finally:
            dlg.Destroy()


class SelectAlternatePathEvent(WxInteractionEvent):

    def __init__(self, imgPath):
        WxInteractionEvent.__init__(self)
        self.__imgPath = imgPath

    def OnProcess(self, wxParent):
        dlg = wx.MessageDialog(wxParent,
                               _(u"Some images does not exist in the folder '%s' anymore. If the files has moved you can select the new path. Do you want to select a new path?") % self.__imgPath,
                               _(u"Question"),
                               wx.YES_NO | wx.ICON_QUESTION)
        try:
            if dlg.ShowModal() == wx.ID_NO:
                self.GetJob().SetAltPath(self.__imgPath, self.__imgPath)
                return
        finally:
            dlg.Destroy()

        dlg = wx.DirDialog(wxParent, defaultPath=Settings().GetImagePath())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.GetJob().SetAltPath(self.__imgPath, path)
                return
            else:
                self.Skip()
        finally:
            dlg.Destroy()
