# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#

import os
import logging

import wx

from photofilmstrip.action.ActionAutoPath import ActionAutoPath
from photofilmstrip.action.ActionCenterPath import ActionCenterPath
from photofilmstrip.action.ActionRender import ActionRender

from photofilmstrip.core.Picture import Picture
from photofilmstrip.core.Project import Project

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.util import CheckFile

from photofilmstrip.gui.helper import CreateMenuItem
from photofilmstrip.gui.ImageSectionEditor import (
        ImageSectionEditor, EVT_RECT_CHANGED)
from photofilmstrip.gui.PhotoFilmStripList import (
        PhotoFilmStripList, EVT_CHANGED)

from photofilmstrip.gui.util.ImageCache import ImageCache

from photofilmstrip.gui.PnlEditorPage import PnlEditorPage
from photofilmstrip.gui.PnlEditPicture import PnlEditPicture
from photofilmstrip.gui.PnlAddPics import PnlAddPics
from photofilmstrip.gui.DlgConfigureAudio import DlgConfigureAudio
from photofilmstrip.gui.DlgPositionInput import DlgPositionInput
from photofilmstrip.gui.DlgRender import DlgRender
from photofilmstrip.gui.WxProjectFile import WxProjectFile
from photofilmstrip.core.exceptions import RenderException

[wxID_PNLPFSPROJECT, wxID_PNLPFSPROJECTBITMAPLEFT,
 wxID_PNLPFSPROJECTBITMAPRIGHT, wxID_PNLPFSPROJECTCMDMOVELEFT,
 wxID_PNLPFSPROJECTCMDMOVERIGHT, wxID_PNLPFSPROJECTCMDREMOVE,
 wxID_PNLPFSPROJECTLVPICS, wxID_PNLPFSPROJECTPANELTOP,
 wxID_PNLPFSPROJECTPNLADDPICS, wxID_PNLPFSPROJECTPNLEDITPICTURE,
 wxID_PNLPFSPROJECTTOOLBARIMGSECT,
] = [wx.NewId() for _init_ctrls in range(11)]

[wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST,
 wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT,
 wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT,
 wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK, wxID_PNLPFSPROJECTTOOLBARIMGSECTSWAP,
 wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH,
] = [wx.NewId() for _init_coll_toolBarImgSect_Tools in range(6)]

[ID_PIC_MOVE_LEFT,
 ID_PIC_MOVE_RIGHT,
 ID_PIC_REMOVE,
 ID_PIC_ROTATE_CW,
 ID_PIC_ROTATE_CCW,
 ID_PIC_MOTION_RANDOM,
 ID_PIC_MOTION_CENTER,
 ID_PIC_IMPORT,
 ID_MUSIC,
 ID_RENDER_FILMSTRIP,
 ID_EXPORT, ID_IMPORT,
] = [wx.NewId() for __ in range(12)]


class PnlPfsProject(PnlEditorPage, Observer):

    _custom_classes = {"wx.Panel": ["PnlEditorPage",
                                    "ImageSectionEditor",
                                    "PnlEditPicture",
                                    "PnlAddPics"],
                       "wx.ListView": ["PhotoFilmStripList"]}

    def _init_coll_sizerPictures_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.lvPics, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.sizerPictureCtrls, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerPictureCtrls_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.cmdMoveLeft, 0, border=2, flag=wx.ALL)
        parent.AddStretchSpacer(1)
        parent.Add(self.cmdMoveRight, 0, border=2, flag=wx.ALL)
        parent.AddStretchSpacer(1)
        parent.Add(self.cmdRemove, 0, border=2, flag=wx.ALL)

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.panelTop, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.pnlAddPics, 1, border=0,
              flag=wx.ALIGN_CENTER_HORIZONTAL)
        parent.Add(self.pnlEditPicture, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.sizerPictures, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerPnlTop_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bitmapLeft, 1, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.toolBarImgSect, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.bitmapRight, 1, border=0, flag=wx.ALL | wx.EXPAND)

    def _init_coll_toolBarImgSect_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH, "",
                       wx.ArtProvider.GetBitmap('PFS_MOTION_RANDOM_24'),
                       _(u'Random motion'))
        parent.AddSeparator()
        parent.AddTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT,
                       _(u'Set motion start to end'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_START_TO_END_24'),
                       _(u'Set motion start to end'))
        parent.AddTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT,
                       _(u'Set motion end to start'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_END_TO_START_24'),
                       _(u'Set motion end to start'))
        parent.AddTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTSWAP,
                       _(u'Swap motion'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_SWAP_24'),
                       _(u'Swap motion'))
        parent.AddSeparator()
        parent.AddTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST,
                       _(u'Adjust motion manual'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_MANUAL_24'),
                       _(u'Adjust motion manual'))
        parent.AddSeparator()
        parent.AddCheckTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK,
                            _(u'Preserve image dimension'),
                            wx.ArtProvider.GetBitmap('PFS_LOCK_24'),
                            shortHelp=_(u'Preserve image dimension'))
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolAutoPath,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolLeftToRight,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolRightToLeft,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolAdjust,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectSwap,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTSWAP)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectUnlockTool,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK)

        parent.Realize()

    def _init_sizers(self):
        # generated method, don't edit
        sizerPnlTop = wx.BoxSizer(orient=wx.HORIZONTAL)

        sizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerPictures = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerPictureCtrls = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_sizerPnlTop_Items(sizerPnlTop)
        self._init_coll_sizerMain_Items(sizerMain)
        self._init_coll_sizerPictures_Items(self.sizerPictures)
        self._init_coll_sizerPictureCtrls_Items(self.sizerPictureCtrls)

        self.SetSizer(sizerMain)
        self.panelTop.SetSizer(sizerPnlTop)

    def _InitCtrls(self):
        self.panelTop = wx.Panel(id=wxID_PNLPFSPROJECTPANELTOP,
              name=u'panelTop', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.bitmapLeft = ImageSectionEditor(id=wxID_PNLPFSPROJECTBITMAPLEFT,
              name=u'bitmapLeft', parent=self.panelTop, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.toolBarImgSect = wx.ToolBar(id=wxID_PNLPFSPROJECTTOOLBARIMGSECT,
              name=u'toolBarImgSect', parent=self.panelTop,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TB_VERTICAL | wx.NO_BORDER | wx.TB_NODIVIDER)

        self.bitmapRight = ImageSectionEditor(id=wxID_PNLPFSPROJECTBITMAPRIGHT,
              name=u'bitmapRight', parent=self.panelTop, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.pnlAddPics = PnlAddPics(id=wxID_PNLPFSPROJECTPNLADDPICS,
              name=u'pnlAddPics', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.pnlEditPicture = PnlEditPicture(id=wxID_PNLPFSPROJECTPNLEDITPICTURE,
              name=u'pnlEditPicture', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.lvPics = PhotoFilmStripList(id=wxID_PNLPFSPROJECTLVPICS,
              name=u'lvPics', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1),
              style=wx.HSCROLL)  # | wx.ALWAYS_SHOW_SB)
        self.lvPics.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnLvPicsSelectionChanged, id=wxID_PNLPFSPROJECTLVPICS)

        self.cmdMoveLeft = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_LEFT_32'),
              id=wxID_PNLPFSPROJECTCMDMOVELEFT,
              name=u'cmdMoveLeft', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdMoveLeft.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_LEFT_D_32'))
        self.cmdMoveLeft.Bind(wx.EVT_BUTTON, self.OnCmdMoveLeftButton,
              id=wxID_PNLPFSPROJECTCMDMOVELEFT)

        self.cmdMoveRight = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_RIGHT_32'),
              id=wxID_PNLPFSPROJECTCMDMOVERIGHT, name=u'cmdMoveRight',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdMoveRight.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_RIGHT_D_32'))
        self.cmdMoveRight.Bind(wx.EVT_BUTTON, self.OnCmdMoveRightButton,
              id=wxID_PNLPFSPROJECTCMDMOVERIGHT)

        self.cmdRemove = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMAGE_REMOVE_32'),
              id=wxID_PNLPFSPROJECTCMDREMOVE,
              name=u'cmdRemove', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdRemove.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_IMAGE_REMOVE_D_32'))
        self.cmdRemove.Bind(wx.EVT_BUTTON, self.OnCmdRemoveButton,
              id=wxID_PNLPFSPROJECTCMDREMOVE)

        self._init_coll_toolBarImgSect_Tools(self.toolBarImgSect)

        self._init_sizers()

    def __init__(self, parent, project):
        PnlEditorPage.__init__(self, parent, id=wxID_PNLPFSPROJECT,
                               name=u'PnlPfsProject')
        self.SetClientSize(wx.Size(400, 250))

        self._InitCtrls()
        Observer.__init__(self)

        self.lvPics.SetDropTarget(ImageDropTarget(self))

        self.imgProxyLeft = None
        self.imgProxyRight = None
        self.__project = project
        self.__usedAltPath = False

        self._InitImageProxy()

        self.bitmapLeft.SetAspect(project.GetAspect())
        self.bitmapRight.SetAspect(project.GetAspect())

        self.pnlAddPics.GetButton().Bind(wx.EVT_BUTTON, self.OnImportPics)
        self.pnlAddPics.stInfo.SetDropTarget(ImageDropTarget(self))

        self.cmdMoveLeft.Enable(False)
        self.cmdMoveRight.Enable(False)
        self.cmdRemove.Enable(False)
        self.panelTop.Show(False)

        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapLeft.GetId())
        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapRight.GetId())

        self.Bind(EVT_CHANGED, self.OnPhotoFilmStripListChanged, id=self.lvPics.GetId())

        project.AddObserver(self)
        self.pnlEditPicture.SetupModeByProject(project)

        self.SetInitialSize(self.GetEffectiveMinSize())
        self.SetChanged(False)

    def _InitImageProxy(self):
        raise NotImplementedError()

    def GetFileExtension(self):
        return ".pfs"

    def GetSaveFilePath(self):
        return self.__project.GetFilename()

    def _Save(self, filepath):
        prjFile = WxProjectFile(self, self.__project, filepath)
        prjFile.Save(False)
        return True

    def AddMenuFileActions(self, menu):
#        CreateMenuItem(menu, self.ID_IMPORT, _(u"&Import Project"))
#        CreateMenuItem(menu, self.ID_EXPORT, _(u"&Export Project"))
#        menu.AppendSeparator()
        pass

    def AddMenuEditActions(self, menu):
        CreateMenuItem(menu, ID_PIC_IMPORT,
                       _(u'&Import Pictures') + '\tCtrl+I',
                       wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PIC_MOVE_LEFT,
                       _(u'Move picture &left'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_LEFT_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_LEFT_D_16'))
        CreateMenuItem(menu, ID_PIC_MOVE_RIGHT,
                       _(u'Move picture &right'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_RIGHT_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_MOVING_RIGHT_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PIC_REMOVE,
                       _(u'R&emove Picture') + '\tCtrl+Del',
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_REMOVE_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_REMOVE_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PIC_ROTATE_CW,
                       _(u'Rotate &clockwise') + '\tCtrl+r',
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_RIGHT_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_RIGHT_D_16'))
        CreateMenuItem(menu, ID_PIC_ROTATE_CCW,
                       _(u'Rotate counter clock&wise') + '\tCtrl+l',
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_LEFT_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_LEFT_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PIC_MOTION_RANDOM,
                       _(u'Random &motion') + '\tCtrl+d',
                       wx.ArtProvider.GetBitmap('PFS_MOTION_RANDOM_16'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_RANDOM_D_16'))
        CreateMenuItem(menu, ID_PIC_MOTION_CENTER,
                       _(u'Centralize m&otion') + '\tCtrl+f',
                       wx.ArtProvider.GetBitmap('PFS_MOTION_CENTER_16'),
                       wx.ArtProvider.GetBitmap('PFS_MOTION_CENTER_D_16'))

    def ConnectEvents(self, evtHandler):
        evtHandler.Bind(wx.EVT_MENU, self.OnProjectExport, id=ID_EXPORT)
        evtHandler.Bind(wx.EVT_MENU, self.OnProjectImport, id=ID_IMPORT)

        evtHandler.Bind(wx.EVT_MENU, self.OnCmdMoveLeftButton, id=ID_PIC_MOVE_LEFT)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdMoveRightButton, id=ID_PIC_MOVE_RIGHT)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdRemoveButton, id=ID_PIC_REMOVE)

        evtHandler.Bind(wx.EVT_MENU, self.OnCmdRotateLeftButton, id=ID_PIC_ROTATE_CCW)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdRotateRightButton, id=ID_PIC_ROTATE_CW)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdMotionRandom, id=ID_PIC_MOTION_RANDOM)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdMotionCenter, id=ID_PIC_MOTION_CENTER)

        evtHandler.Bind(wx.EVT_MENU, self.OnImportPics, id=ID_PIC_IMPORT)
        evtHandler.Bind(wx.EVT_MENU, self.OnConfigureMusic, id=ID_MUSIC)
        evtHandler.Bind(wx.EVT_MENU, self.OnRenderFilmstrip, id=ID_RENDER_FILMSTRIP)

        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_REMOVE)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_ROTATE_CCW)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_ROTATE_CW)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_MOVE_LEFT)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_MOVE_RIGHT)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_MOTION_RANDOM)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ID_PIC_MOTION_CENTER)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_RENDER_FILMSTRIP)

    def DisconnEvents(self, evtHandler):
        for wId in [ID_PIC_MOVE_LEFT, ID_PIC_MOVE_RIGHT, ID_PIC_REMOVE,
                    ID_PIC_ROTATE_CCW, ID_PIC_ROTATE_CW, ID_PIC_MOTION_RANDOM,
                    ID_PIC_MOTION_CENTER, ID_PIC_IMPORT, ID_MUSIC, ID_RENDER_FILMSTRIP]:
            evtHandler.Disconnect(wId)

    def GetSelectedImageState(self):
        items = self.lvPics.GetSelected()
        if len(items) == 0:
            kind = 'none'
        elif items[0] == 0:
            if self.lvPics.GetItemCount() == 1:
                kind = 'none'  # to disable move buttons
            else:
                kind = 'first'
        elif items[0] == self.lvPics.GetItemCount() - 1:
            kind = 'last'
        else:
            kind = 'any'

#        if len(items) > 1:
#            kind = 'multi'

        return kind

    def OnProjectExport(self, event):
        prj = self.__project
        curFilePath = prj.GetFilename()
        dlg = wx.FileDialog(self, _(u"Export slideshow"),
                            Settings().GetProjectPath(),
                            curFilePath,
                            u"%s %s" % (_(u"Portable slideshow"), "(*.ppfs)|*.ppfs"),
                            wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".ppfs":
                filepath += ".ppfs"

            prjFile = WxProjectFile(self, self.__project, filepath)
            prjFile.Save(True)

    def OnProjectImport(self, event):
        dlg = wx.FileDialog(self, _(u"Import Slideshow"),
                            Settings().GetProjectPath(), "",
                            u"%s %s" % (_(u"Portable slideshow"), "(*.ppfs)|*.ppfs"),
                            wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()

            prjFile = WxProjectFile(self, filename=filepath)
            prjFile.Load()

    def OnImportPics(self, event):
        dlg = wx.FileDialog(self, _(u"Import images"),
                            Settings().GetImagePath(), "",
                            _(u"Image files") + " (*.*)|*.*",
                            wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_PREVIEW)
        if dlg.ShowModal() == wx.ID_OK:
            pics = []
            for path in dlg.GetPaths():
                if not self._CheckImportedPic(path):
                    continue

                pic = Picture(path)
                pics.append(pic)
                ImageCache().RegisterPicture(pic)

            selItms = self.lvPics.GetSelected()
            self.InsertPictures(pics,
                                selItms[0] + 1 if selItms else None,
                                autopath=True)

            Settings().SetImagePath(os.path.dirname(path))

            selPics = self.lvPics.GetSelectedPictures()
            self.pnlEditPicture.SetPictures(selPics)
        dlg.Destroy()

    def _CheckImportedPic(self, path):  # pylint: disable=unused-argument
        return True

    def OnConfigureMusic(self, event):
        dlg = DlgConfigureAudio(self, self.GetProject())
        dlg.ShowModal()
        dlg.Destroy()

    def OnRenderFilmstrip(self, event):
        self.PrepareRendering()

        project = self.__project
        dlg = DlgRender(self, project.GetAspect())
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return

            profile = dlg.GetProfile()
            draftMode = dlg.GetDraftMode()
            rendererClass = dlg.GetRendererClass()
        finally:
            dlg.Destroy()

        ar = ActionRender(project,
                          profile,
                          rendererClass,
                          draftMode)
        try:
            ar.Execute()
            renderJob = ar.GetRenderJob()
            JobManager().EnqueueContext(renderJob)
        except RenderException as exc:
            dlg = wx.MessageDialog(self,
                                   exc.GetMessage(),
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def OnCheckImageSelected(self, event):
        value = self.IsPictureSelected()
        kind = self.GetSelectedImageState()
        if event.GetId() == ID_PIC_MOVE_LEFT:
            # FIXME: does not work with multiselect
            value = kind not in ['first', 'none'] and value
        elif event.GetId() == ID_PIC_MOVE_RIGHT:
            # FIXME: does not work with multiselect
            value = kind not in ['last', 'none'] and value
        event.Enable(value)

    def OnCheckProjectReady(self, event):
        event.Enable(self.IsReady())

    def OnLvPicsSelectionChanged(self, event):
        selItems = self.lvPics.GetSelected()

        self.cmdMoveLeft.Enable(selItems.count(0) == 0)
        self.cmdMoveRight.Enable(selItems.count(self.lvPics.GetItemCount() - 1) == 0)
        self.cmdRemove.Enable(len(selItems) > 0)

        selPics = self.lvPics.GetSelectedPictures()
        self.pnlEditPicture.SetPictures(selPics)

        self.panelTop.Enable(len(selPics) == 1)
        self.bitmapRight.Enable(len(selPics) == 1)
        self.bitmapLeft.Enable(len(selPics) == 1)

        self._OnPicsSelectionChanged(selItems, selPics)

        if event:
            event.Skip()

    def _OnPicsSelectionChanged(self, selItems, selPics):
        raise NotImplementedError()

    def OnRectChanged(self, event):
        selItem = self.lvPics.GetSelected()
        pic = None
        if selItem:
            pic = self.lvPics.GetPicture(selItem[0])
        if pic is None:
            return

        if self.__project.GetTimelapse():
            self.__OnRectChangedTimelapse(event, pic, selItem[0])
        else:
            self.__OnRectChangedDefault(event, pic)

        if event.CheckImageDimensionLock():
            self._CheckAndSetLock(pic)

    def __OnRectChangedDefault(self, event, pic):
        if event.GetEventObject() is self.bitmapLeft:
            pic.SetStartRect(tuple(self.bitmapLeft.GetSection()))
        else:
            pic.SetTargetRect(tuple(self.bitmapRight.GetSection()))

    def __OnRectChangedTimelapse(self, event, pic, selIdx):
        if event.GetEventObject() is self.bitmapLeft:
            pic.SetStartRect(tuple(self.bitmapLeft.GetSection()))
            prevPic = self.lvPics.GetPicture(selIdx - 1)
            if prevPic:
                prevPic.SetTargetRect(tuple(self.bitmapLeft.GetSection()))
        else:
            pic.SetTargetRect(tuple(self.bitmapRight.GetSection()))
            nextPic = self.lvPics.GetPicture(selIdx + 1)
            if nextPic:
                nextPic.SetStartRect(tuple(self.bitmapRight.GetSection()))

    def OnCmdMoveLeftButton(self, event):
        selItems = self.lvPics.GetSelected()
        selItems.sort()
        for selItem in selItems:
            self.lvPics.SwapPictures(selItem, selItem - 1)

        self.SetChanged(True)

    def OnCmdMoveRightButton(self, event):
        selItems = self.lvPics.GetSelected()
        selItems.sort(reverse=True)
        for selItem in selItems:
            self.lvPics.SwapPictures(selItem, selItem + 1)

        self.SetChanged(True)

    def OnCmdRemoveButton(self, event):
        selItems = self.lvPics.GetSelected()
        # remove pics starting at the end
        selItems.sort(reverse=True)
        for selItem in selItems:
            self.lvPics.DeleteItem(selItem)

        if self.lvPics.GetItemCount() == 0:
            self.imgProxyLeft.SetPicture(None)
            self.imgProxyRight.SetPicture(None)
            self.pnlEditPicture.SetPictures(None)
            self.pnlEditPicture.Enable(False)
            self.cmdMoveLeft.Enable(False)
            self.cmdMoveRight.Enable(False)

            self.pnlAddPics.Show(True)
            self.panelTop.Show(False)

        self.cmdRemove.Enable(self.lvPics.GetItemCount() > 0)

        self.Layout()

    def OnCmdRotateLeftButton(self, event):
        self.pnlEditPicture.OnCmdRotateLeftButton(event)

    def OnCmdRotateRightButton(self, event):
        self.pnlEditPicture.OnCmdRotateRightButton(event)

    def OnCmdMotionRandom(self, event):
        self.OnMotionRandom()

    def OnCmdMotionCenter(self, event):
        self.OnMotionCenter()

    def OnPhotoFilmStripListChanged(self, event):
        self.__project.SetPictures(self.lvPics.GetPictures())
        self.SetChanged(True)

    def OnToolBarImgSectToolAutoPath(self, event):
        self.OnMotionRandom()

    def OnToolBarImgSectToolLeftToRight(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem[0])
        if pic is None:
            return
        pic.SetTargetRect(pic.GetStartRect())

    def OnToolBarImgSectToolRightToLeft(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem[0])
        if pic is None:
            return
        pic.SetStartRect(pic.GetTargetRect())

    def OnToolBarImgSectSwap(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem[0])
        if pic is None:
            return
        target = pic.GetTargetRect()
        pic.SetTargetRect(pic.GetStartRect())
        pic.SetStartRect(target)

    def OnToolBarImgSectToolAdjust(self, event):
        selItem = self.lvPics.GetSelected()
        selPic = self.lvPics.GetPicture(selItem[0])

        dlg = DlgPositionInput(self, selPic, self.__project.GetAspect())
        dlg.ShowModal()
        dlg.Destroy()

    def OnMotionRandom(self):
        for pic in self.lvPics.GetSelectedPictures():
            actAp = ActionAutoPath(pic, self.__project.GetAspect())
            actAp.Execute()

    def OnMotionCenter(self):
        for pic in self.lvPics.GetSelectedPictures():
            actCp = ActionCenterPath(pic, self.__project.GetAspect())
            actCp.Execute()

    def Close(self):
        self.imgProxyLeft.RemoveObserver(self.bitmapLeft)
        self.imgProxyRight.RemoveObserver(self.bitmapRight)
        self.imgProxyLeft.Destroy()
        self.imgProxyRight.Destroy()

    def GetProject(self):
        return self.__project

    def PrepareRendering(self):
        for audioFile in self.__project.GetAudioFiles():
            if not CheckFile(audioFile):
                dlg = wx.MessageDialog(self,
                                       _(u"Audio file '%s' does not exist! Continue anyway?") % audioFile,
                                       _(u"Warning"),
                                       wx.YES_NO | wx.ICON_WARNING)
                dlgResult = dlg.ShowModal()
                dlg.Destroy()
                if dlgResult == wx.ID_NO:
                    return
                else:
                    break

    def InsertPictures(self, pics, position=None, autopath=False):
        logging.debug("InsertPictures(pos=%s)", position)
        if position is None:
            position = self.lvPics.GetItemCount()

        self.lvPics.Freeze()
        for pic in pics:
            if autopath:
                actAp = ActionAutoPath(pic, self.__project.GetAspect())
                actAp.Execute()

            self.lvPics.InsertPicture(position, pic)
            position += 1

            pic.AddObserver(self)
        self.lvPics.Thaw()
        if len(self.lvPics.GetSelected()) == 0:
            self.lvPics.Select(0)

        self.SetChanged(True)

        self.pnlAddPics.Show(self.lvPics.GetItemCount() == 0)
        self.panelTop.Show(self.lvPics.GetItemCount() != 0)
        self.Layout()

        self.lvPics.SetFocus()

    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, Picture):
            if arg == 'bitmap':
                if self.bitmapLeft._imgProxy._picture is obj:
                    self.imgProxyLeft.SetPicture(obj)
                elif self.bitmapRight._imgProxy._picture is obj:
                    self.imgProxyRight.SetPicture(obj)
                self.lvPics.Refresh()

            if arg == 'duration':
                self.__project.Notify("duration")

            if arg == 'start' and self.bitmapLeft._imgProxy._picture is obj:
                self.bitmapLeft.SetSection(wx.Rect(*obj.GetStartRect()))

            if arg == 'target' and self.bitmapLeft._imgProxy._picture is obj:
                self.bitmapRight.SetSection(wx.Rect(*obj.GetTargetRect()))

            self.SetChanged(True)

        elif isinstance(obj, Project):
            if arg == 'duration':
                self.pnlEditPicture.SetupModeByProject(self.__project)
                self.SetChanged(True)

    def IsReady(self):
        return self.lvPics.GetItemCount() > 0

    def IsPictureSelected(self):
        return len(self.lvPics.GetSelected()) > 0

    def _CheckAndSetLock(self, pic):
        unlocked = False
        for rect in (pic.GetStartRect(), pic.GetTargetRect()):
            if rect[0] < 0 or rect[1] < 0 \
            or rect[2] > pic.GetWidth() or rect[3] > pic.GetHeight() \
            or rect[0] + rect[2] > pic.GetWidth() \
            or rect[1] + rect[3] > pic.GetHeight():
                unlocked = True
                break
        self.toolBarImgSect.ToggleTool(wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK,
                                       unlocked)
        if unlocked:
            resName = 'PFS_UNLOCK_24'
        else:
            resName = 'PFS_LOCK_24'
        self.toolBarImgSect.SetToolNormalBitmap(
            wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK,
            wx.ArtProvider.GetBitmap(resName, wx.ART_TOOLBAR, wx.DefaultSize))
        self.bitmapLeft.SetLock(not unlocked)
        self.bitmapRight.SetLock(not unlocked)

    def OnToolBarImgSectUnlockTool(self, event):
        if event.IsChecked():
            resName = 'PFS_UNLOCK_24'
        else:
            resName = 'PFS_LOCK_24'
        self.toolBarImgSect.SetToolNormalBitmap(
            wxID_PNLPFSPROJECTTOOLBARIMGSECTUNLOCK,
            wx.ArtProvider.GetBitmap(resName, wx.ART_TOOLBAR, wx.DefaultSize))

        self.bitmapLeft.SetLock(not event.IsChecked())
        self.bitmapRight.SetLock(not event.IsChecked())


class ImageDropTarget(wx.FileDropTarget):

    def __init__(self, pnlPfs):
        wx.FileDropTarget.__init__(self)
        self.pnlPfs = pnlPfs

    def OnDropFiles(self, x, y, filenames):
        itm = self.pnlPfs.lvPics.HitTest((x, y))
        logging.debug("OnDropFiles(%d, %d, %s): %s", x, y, filenames, itm)

        pics = []
        for path in filenames:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                pic = Picture(path)
                pics.append(pic)

        if pics:
            self.pnlPfs.InsertPictures(pics, itm + 1 if itm != wx.NOT_FOUND else None, True)
            return True
        return False
