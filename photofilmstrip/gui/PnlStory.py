# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import os

import wx
import wx.lib.scrolledpanel

from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.VisualJob import VisualJob

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.Media import Media, MediaOrientation
from photofilmstrip.core.OutputProfile import OutputProfile, FPS25
from photofilmstrip.core.StoryFile import StoryFile
from photofilmstrip.core.StoryEngine import StoryEngine

from photofilmstrip.gui.ctrls.PnlNotification import PnlNotification
from photofilmstrip.gui.DlgRender import DlgRender, FormatData
from photofilmstrip.gui.PnlEditorPage import PnlEditorPage
from photofilmstrip.gui.helper import CreateMenuItem
from photofilmstrip.PnlStoryGuide import PnlStoryGuide

[ID_MEDIA_ADD,
 ID_MEDIA_MOVE_UP,
 ID_MEDIA_MOVE_DOWN,
 ID_MEDIA_MOVE_OUT,
 ID_MEDIA_MOVE_IN,
 ID_MEDIA_REMOVE,
 ID_RENDER,
 ID_PREVIEW,
] = [wx.NewId() for __ in range(8)]


class PnlStory(PnlEditorPage, Observer):

    def __init__(self, parent, story):
        PnlEditorPage.__init__(self, parent)
        Observer.__init__(self)
        self.__story = story

        self.splitWin = wx.SplitterWindow(self)

        self.pnlMedias = PnlMediaContainer(self.splitWin)
        self.pnlMedias.SetupScrolling(scroll_x=False)
        self.pnlMedias.Bind(wx.EVT_CHAR_HOOK, self._OnKeyDown)

        self.treeCtrlr = TreeController(story, self.pnlMedias, self)

        self.pnlNotification = PnlNotification(self)

        self.pnlGuide = PnlStoryGuide(self.splitWin)
        self.pnlGuide.Bind(wx.html.EVT_HTML_LINK_CLICKED, self._OnLinkClicked)

        szMain = wx.BoxSizer(wx.VERTICAL)
        szMain.Add(self.splitWin, 1, wx.EXPAND, 0)
        szMain.Add(self.pnlNotification, 0, wx.EXPAND)

        self.pnlNotification.Show(False)

        self.SetSizer(szMain)
        self.splitWin.SplitVertically(self.pnlMedias, self.pnlGuide, -600)

    def ObservableUpdate(self, obj, arg):
        self.SetChanged(True)

    def _OnLinkClicked(self, event):
        self.splitWin.Unsplit()

    def _OnKeyDown(self, event):
        key = event.GetKeyCode()
        if event.AltDown():
            if key == wx.WXK_UP:
                self._OnMoveUp(event)
                return
            elif key == wx.WXK_DOWN:
                self._OnMoveDown(event)
                return
            elif key == wx.WXK_LEFT:
                self._OnMoveOut(event)
                return
            elif key == wx.WXK_RIGHT:
                self._OnMoveIn(event)
                return
        if key == wx.WXK_DELETE:
            self._OnRemove(event)
            return
        event.Skip()

    def _OnAddMedia(self, event):  # pylint: disable=unused-argument
        dlg = wx.FileDialog(self, _("Add media"),
                            Settings().GetProjectPath(), "",
                            _("Media files") + " (*.*)|*.*",
                            wx.FD_OPEN | wx.FD_PREVIEW | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            itmParent, offset = self.treeCtrlr.GetInsertInfo()
            for idx, path in enumerate(dlg.GetPaths()):
                media = Media(path)
                media.AddObserver(self)

                itmNew = self.treeCtrlr.AddMedia(itmParent, media, offset + idx)
                self.pnlMedias.SelectItem(itmNew)

        dlg.Destroy()

    def _OnMoveUp(self, event):  # pylint: disable=unused-argument
        selItm = self.treeCtrlr.GetSelectedItem()
        if not selItm:
            return

        newItm = self.treeCtrlr.MoveUp(selItm)
        if newItm:
            self.pnlMedias.SelectItem(newItm)

    def _OnMoveDown(self, event):  # pylint: disable=unused-argument
        selItm = self.treeCtrlr.GetSelectedItem()
        if not selItm:
            return

        newItm = self.treeCtrlr.MoveDown(selItm)
        if newItm:
            self.pnlMedias.SelectItem(newItm)

    def _OnMoveOut(self, event):  # pylint: disable=unused-argument
        selItm = self.treeCtrlr.GetSelectedItem()
        if not selItm:
            return

        newItm = self.treeCtrlr.MoveOut(selItm)
        if newItm:
            self.pnlMedias.SelectItem(newItm)

    def _OnMoveIn(self, event):  # pylint: disable=unused-argument
        selItm = self.treeCtrlr.GetSelectedItem()
        if not selItm:
            return

        try:
            newItm = self.treeCtrlr.MoveIn(selItm)
        except ValueError as err:
            self.pnlNotification.AddNotification(str(err), 5000)
            return

        if newItm:
            self.pnlMedias.SelectItem(newItm)

    def _OnRemove(self, event):  # pylint: disable=unused-argument
        selItm = self.treeCtrlr.GetSelectedItem()
        if not selItm:
            return

        self.treeCtrlr.RemoveMedia(selItm)

    def _OnPreview(self, event):  # pylint: disable=unused-argument
        profile = OutputProfile("HD 720p", (1280, 720), FPS25, 5000)
        self._OnStart(None, profile)

    def _OnRender(self, event):  # pylint: disable=unused-argument
        dlg = DlgRender(self, RendererProvider(), Aspect.ASPECT_16_9)
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return

            profile = dlg.GetProfile()
            gstElements = dlg.GetFormatData().GetData()
        finally:
            dlg.Destroy()

        dlg = wx.FileDialog(self, _("Video file"),
                            Settings().GetProjectPath(), "",
                            _("Video files") + " (*.*)|*.*",
                            wx.FD_SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self._OnStart(dlg.GetPath(), profile, gstElements)
            else:
                return
        finally:
            dlg.Destroy()

    def _OnStart(self, outpath, profile=None, gstElements=None):
        self._UpdateProject()
        vj = StoryEngine(self.__story.GetMedias(), outpath, profile, gstElements)

        if outpath is None:
            # do a preview
            label = "Preview"
            groupId = "general"
        else:
            label = _("Generate video %s") % outpath
            groupId = "render"

        wxvJob = VisualJob(label, vj.Execute, maxProgress=100,
                           groupId=groupId)
        if outpath:
            wxvJob.GetOutputFile = lambda: outpath
        JobManager().EnqueueContext(wxvJob)

    def GetProject(self):
        return self.__story

    def IsReady(self):
        self._UpdateProject()
        isOk = True
        for media in self.__story.GetMedias():
            if not media.IsOk():
                isOk = False
                break

            if media.IsAudio() and not media.GetChildren():
                self.pnlNotification.AddNotification(
                    _("An audio stream needs to contain at least one video stream!"))
                isOk = False
                break

            for subMedia in media.GetChildren():
                if not subMedia.IsOk():
                    isOk = False
                    break

            if not isOk:
                break

        result = bool(self.__story.GetMedias()) and isOk
        if result:
            self.pnlNotification.ClearNotifications()
        return result

    def GetStatusText(self, index):
        return ""

    def GetSaveFilePath(self):
        fp = self.__story.GetFilename()
        dirname = os.path.dirname(fp)
        if not dirname:
            return None

        return fp

    def _GetEditorName(self):
        return "Story"

    def _Save(self, filepath):
        self._UpdateProject()
        pf = StoryFile(self.__story, filepath)
        pf.Save()
        return True

    def _UpdateProject(self):
        medias = []
        for media in self.treeCtrlr.GetRootItems():
            medias.append(media)
        self.__story.SetMedias(medias)

    def GetFileExtension(self):
        return ".pfstory"

    def AddMenuEditActions(self, menu):
        menuSize = wx.ArtProvider.GetSizeHint(wx.ART_MENU)
        CreateMenuItem(menu, ID_MEDIA_ADD,
                       _("Add media") + "\tCtrl+I",
                       wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_16'),
                       wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_MEDIA_MOVE_UP,
                       _("Move up"),
                       wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_MENU, menuSize))
        CreateMenuItem(menu, ID_MEDIA_MOVE_DOWN,
                       _("Move down"),
                       wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_MENU, menuSize))
        CreateMenuItem(menu, ID_MEDIA_REMOVE,
                       _("Remove") + "\tCtrl+Del",
                       wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU, menuSize))

    def AddToolBarActions(self, toolBar):
        toolSize = wx.ArtProvider.GetSizeHint(wx.ART_TOOLBAR)
        toolBar.AddTool(ID_MEDIA_ADD, "",
                        wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_24'),
                        wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_D_24'),
                        wx.ITEM_NORMAL,
                        _("Add media"), _("Add clip"))
        toolBar.AddSeparator()
        toolBar.AddTool(ID_MEDIA_MOVE_UP, "",
                        wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, toolSize),
                        shortHelp=_("Move up"))
        toolBar.AddTool(ID_MEDIA_MOVE_DOWN, "",
                        wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_TOOLBAR, toolSize),
                        shortHelp=_("Move down"))
        toolBar.AddTool(ID_MEDIA_MOVE_OUT, "",
                        wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, toolSize),
                        shortHelp=_("Move out"))
        toolBar.AddTool(ID_MEDIA_MOVE_IN, "",
                        wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, toolSize),
                        shortHelp=_("Move in"))
        toolBar.AddSeparator()
        toolBar.AddTool(ID_MEDIA_REMOVE, "",
                        wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, toolSize),
                        shortHelp=_("Remove"))
        toolBar.AddSeparator()
        toolBar.AddTool(ID_PREVIEW, "",
                        wx.ArtProvider.GetBitmap('PFS_PLAY_24'),
                        shortHelp=_("Preview"))
        toolBar.AddTool(ID_RENDER, "",
                        wx.ArtProvider.GetBitmap('PFS_RENDER_24'),
                        wx.ArtProvider.GetBitmap('PFS_RENDER_D_24'),
                        wx.ITEM_NORMAL,
                        _("Render filmstrip"),
                        _("Render filmstrip"))

    def ConnectEvents(self, evtHandler):
        evtHandler.Bind(wx.EVT_MENU, self._OnAddMedia, id=ID_MEDIA_ADD)
        evtHandler.Bind(wx.EVT_MENU, self._OnMoveUp, id=ID_MEDIA_MOVE_UP)
        evtHandler.Bind(wx.EVT_MENU, self._OnMoveDown, id=ID_MEDIA_MOVE_DOWN)
        evtHandler.Bind(wx.EVT_MENU, self._OnMoveOut, id=ID_MEDIA_MOVE_OUT)
        evtHandler.Bind(wx.EVT_MENU, self._OnMoveIn, id=ID_MEDIA_MOVE_IN)
        evtHandler.Bind(wx.EVT_MENU, self._OnRemove, id=ID_MEDIA_REMOVE)
        evtHandler.Bind(wx.EVT_MENU, self._OnPreview, id=ID_PREVIEW)
        evtHandler.Bind(wx.EVT_MENU, self._OnRender, id=ID_RENDER)

        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_RENDER)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PREVIEW)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckSelection, id=ID_MEDIA_MOVE_UP)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckSelection, id=ID_MEDIA_MOVE_DOWN)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckSelection, id=ID_MEDIA_MOVE_OUT)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckSelection, id=ID_MEDIA_MOVE_IN)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckSelection, id=ID_MEDIA_REMOVE)

    def DisconnEvents(self, evtHandler):
        for wId in [ID_MEDIA_ADD, ID_MEDIA_MOVE_UP, ID_MEDIA_MOVE_DOWN,
                    ID_MEDIA_MOVE_OUT, ID_MEDIA_MOVE_IN, ID_MEDIA_REMOVE,
                    ID_PREVIEW, ID_RENDER]:
            evtHandler.Disconnect(wId)

    def Init(self):
        pass

    def OnCheckProjectReady(self, event):
        event.Enable(self.IsReady())

    def OnCheckSelection(self, event):
        selItm = self.treeCtrlr.GetSelectedItem()
        event.Enable(selItm is not None and selItm.IsOk())


class TreeController:

    def __init__(self, project, treeIf, observer):
        '''
        :type project: photofilmstrip.core.Media.Media
        :type treeIf: TreeIF
        '''
        self.treeIf = treeIf
        self.hiddenRoot = Media("")
        self.hiddenRoot.AddObserver(observer)
        self.treeIf.SetItemData(None, self.hiddenRoot)

        for offset, media in enumerate(project.GetMedias()):
            media.AddObserver(observer)
            self.hiddenRoot.AddChild(media, offset)
            itmId = self.treeIf.InsertItem(None, offset, media)
            if offset == 0:
                self.treeIf.SelectItem(itmId)

            for subOffset, subMedia in enumerate(media.GetChildren()):
                subMedia.AddObserver(observer)
                self.treeIf.InsertItem(itmId, subOffset, subMedia)

    def GetSelectedItem(self):
        selection = self.treeIf.GetSelection()
        if selection:
            return selection
        else:
            return None

    def GetInsertInfo(self):
        itmParent = None
        selItm = self.GetSelectedItem()
        offset = 0
        if selItm:
            media = self.treeIf.GetItemData(selItm)
            itmParent = self.treeIf.GetItemParent(selItm)
            offset = media.GetIndex() + 1
        return itmParent, offset

    def AddMedia(self, itmParent, media, idx=0):
        if itmParent is None:
            itmParent = self.treeIf.GetRoot()
        parent = self.treeIf.GetItemData(itmParent)

        parent.AddChild(media, idx)

        itmNew = self.treeIf.InsertItem(itmParent, idx, media)

        for subIdx, subMedia in enumerate(media.GetChildren()):
            self.treeIf.InsertItem(itmNew, subIdx, subMedia)
        return itmNew

    def RemoveMedia(self, wxItm):
        assert wxItm.IsOk() and wxItm != self.treeIf.GetRoot()

        selMedia = self.treeIf.GetItemData(wxItm)
        parent = selMedia.GetParent()
        parent.RemoveChild(selMedia)
        self.treeIf.RemoveItem(wxItm)
        return True

    def MoveUp(self, wxItm):
        assert wxItm.IsOk() and wxItm != self.treeIf.GetRoot()

        selMedia = self.treeIf.GetItemData(wxItm)
        itmParent = self.treeIf.GetItemParent(wxItm)
        idx = selMedia.GetIndex()

        newItm = None
        if idx > 0:
            idx -= 1
            self.RemoveMedia(wxItm)
            newItm = self.AddMedia(itmParent, selMedia, idx)
        return newItm

    def MoveDown(self, wxItm):
        assert wxItm.IsOk() and wxItm != self.treeIf.GetRoot()

        selMedia = self.treeIf.GetItemData(wxItm)
        parent = selMedia.GetParent()
        if parent is self.hiddenRoot:
            itmParent = None
        else:
            itmParent = self.treeIf.GetItemParent(wxItm)
        idx = selMedia.GetIndex()

        newItm = None
        if idx < len(parent.GetChildren()) - 1:
            idx += 1
            self.RemoveMedia(wxItm)
            newItm = self.AddMedia(itmParent, selMedia, idx)
        return newItm

    def MoveOut(self, wxItm):
        assert wxItm.IsOk() and wxItm != self.treeIf.GetRoot()

        selMedia = self.treeIf.GetItemData(wxItm)
        parent = selMedia.GetParent()
        if parent is self.hiddenRoot:
            return None

        idx = parent.GetIndex()

        self.RemoveMedia(wxItm)
        newItm = self.AddMedia(None, selMedia, idx + 1)
        return newItm

    def MoveIn(self, wxItm):
        assert wxItm.IsOk() and wxItm != self.treeIf.GetRoot()

        selMedia = self.treeIf.GetItemData(wxItm)
        parent = selMedia.GetParent()
        idx = selMedia.GetIndex()
        if idx == 0 or selMedia.GetChildren() or parent is not self.treeIf.GetItemData(self.treeIf.GetRoot()):
            raise ValueError(_("It's not allowed to create more than two levels!"))

        newParentItm = self.treeIf.GetPrevSibling(wxItm)
        newParent = self.treeIf.GetItemData(newParentItm)

        if newParent.IsVideo() and selMedia.IsVideo():
            raise ValueError(_("It's not allowed to put a video stream inside a video stream!"))
        elif newParent.IsAudio() and selMedia.IsAudio():
            raise ValueError(_("It's not allowed to put an audio stream inside an audio stream!"))
        else:
            self.RemoveMedia(wxItm)

            newItm = self.AddMedia(newParentItm, selMedia,
                                   len(newParent.GetChildren()))
            return newItm

    def GetRootItems(self):
        result = []
        for treeItm in self.treeIf.GetItems():
            result.append(treeItm.data)
        return result


class TreeIF:

    def GetRoot(self):
        raise NotImplementedError()

    def InsertItem(self, treeItmParent, idx, data):
        raise NotImplementedError()

    def RemoveItem(self, treeItm):
        raise NotImplementedError()

    def GetPrevSibling(self, treeItm):
        raise NotImplementedError()

    def SetItemData(self, treeItm, data):
        raise NotImplementedError()

    def GetItemData(self, treeItm):
        raise NotImplementedError()

    def GetItemParent(self, treeItm):
        raise NotImplementedError()

    def SelectItem(self, treeItm):
        raise NotImplementedError()

    def GetItems(self):
        raise NotImplementedError()

    def GetSelection(self):
        raise NotImplementedError()


class TreeItm:

    def __init__(self, data=None):
        self.data = data
        self.parent = None
        self.children = []
        self.pnl = None

    def GetChildren(self):
        return self.children

    def Insert(self, idx, treeItm):
        self.children.insert(idx, treeItm)
        treeItm.parent = self

    def Delete(self):
        self.parent.children.remove(self)

    def Index(self):
        if self.parent:
            return self.parent.children.index(self)

    def Iter(self):
        for child in self.children:
            yield child

    def IterRek(self):
        for child in self.children:
            yield child
            for subChild in child.IterRek():
                yield subChild

    def Row(self):
        row = 0
        root = self
        while root.parent:
            root = root.parent

        for child in root.IterRek():
            row += 1
            if child is self:
                break
        return row

    def IsOk(self):
        return self.parent is not None


class PnlMediaContainer(wx.lib.scrolledpanel.ScrolledPanel, TreeIF):

    def __init__(self, parent):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY,
            name="pnlMediaContainer", style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.root = TreeItm()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self._selected = None
        self._selItm = None

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectItem)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)

    def OnSelectItem(self, event):
        pnl = event.GetEventObject()
        if pnl != self._selected:
            if self._selected is not None:
                self._selected.Select(False)
            self._selected = pnl
        self._selected.Select(True)
        self._selItm = self._selected.data

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        items = self.GetSizer().GetChildren()
        idx = 0
        for szItem in items:
            if szItem.GetWindow() is self._selected:
                break
            idx += 1
        else:
            idx = -1

        if key == wx.WXK_DOWN:
            if self._selected is not None and len(items) > idx + 1:
                self._selected.Select(False)
                self._selected = items[idx + 1].GetWindow()
                self._selected.Select(True)
                self._selItm = self._selected.data
        elif key == wx.WXK_UP:
            if self._selected is not None and idx > 0:
                self._selected.Select(False)
                self._selected = items[idx - 1].GetWindow()
                self._selected.Select(True)
                self._selItm = self._selected.data
        else:
            event.Skip()

    def GetRoot(self):
        return self.root

    def GetItems(self):
        return self.root.children

    def GetPrevSibling(self, treeItm):
        idx = treeItm.parent.children.index(treeItm)
        if idx > 0:
            return treeItm.parent.children[idx - 1]
        else:
            return None

    def SetItemData(self, treeItm, data):
        if treeItm is None:
            treeItm = self.root
        treeItm.data = data

    def GetItemData(self, treeItm):
        return treeItm.data

    def GetItemParent(self, treeItm):
        return treeItm.parent

    def InsertItem(self, treeItmParent, idx, data):
        if treeItmParent is None:
            treeItmParent = self.root

        treeItm = TreeItm()
        treeItm.data = data
        treeItmParent.Insert(idx, treeItm)

        pnl = PnlMediaItem(self, data)
        pnl.SetData(treeItm)

        treeItm.pnl = pnl

        szIdx = treeItm.Row()

        self.sizer.Insert(szIdx - 1, pnl, wx.SizerFlags().Expand())
        self.Layout()
        return treeItm

    def SelectItem(self, treeItm):
        self._selItm = treeItm
        sel = None
        if treeItm is not None:
            sel = treeItm.pnl
        if sel:
            if self._selected:
                self._selected.Select(False)
            self._selected = sel
            self._selected.Select(True)

    def RemoveItem(self, treeItm):
        szIdx = treeItm.Row() - 1

        for trItem in [treeItm] + list(treeItm.IterRek()):
            if trItem.pnl is self._selected:
                self._selected = None
            self.sizer.Detach(szIdx)
            trItem.pnl.Destroy()

        treeItm.Delete()

        if self._selected is None:
            try:
                sizerItem = self.sizer.GetChildren()[max(szIdx - 1, 0)]
            except IndexError:
                sizerItem = None
            if sizerItem is None:
                self.SelectItem(None)
            else:
                pnlMediaItem = sizerItem.GetWindow()
                self.SelectItem(pnlMediaItem.data)

        self.Layout()

    def GetSelection(self):
        return self._selItm


class PnlMediaItem(wx.Panel):

    def __init__(self, parent, media):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, name='PnlMediaItem')
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        bmp = wx.ArtProvider.GetBitmap("PFS_ALERT_24", wx.ART_OTHER, wx.Size(24, 24))
        if media.IsOk():
            if media.IsAudio():
                bmp = wx.ArtProvider.GetBitmap("PFS_MUSIC_24", wx.ART_OTHER, wx.Size(24, 24))
            elif media.IsVideo():
                bmp = wx.ArtProvider.GetBitmap("PFS_RENDER_24", wx.ART_OTHER, wx.Size(24, 24))

        self.bmp = wx.StaticBitmap(self, wx.ID_ANY,
              bitmap=bmp)

        self.stName = wx.StaticText(self, id=wx.ID_ANY,
              label=media.GetFilename(), name="stName")

        self.stInfo = wx.StaticText(self, id=wx.ID_ANY,
              label="'00:00:00", name="stInfo")

        self.pnlOptOrientation = None
        if media.IsVideo():
            self.pnlOptOrientation = PnlOptSelect(self, _("Orientation"))
            self.pnlOptOrientation.SetItemCaptionGenerator(
                lambda x: x.GetLabel())
            self.pnlOptOrientation.SetItems(list(MediaOrientation))

            for ctrl in self.pnlOptOrientation.GetChildren():
                ctrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)

            self.pnlOptOrientation.Bind(EVT_VALUE_CHANGE, self.__OnOrientationChange)
            value = media.GetProperty("orientation")
            if value:
                self.pnlOptOrientation.SetValue(value)

        self.staticLine = wx.StaticLine(self, id=wx.ID_ANY,
              name="staticLine")

        szCol0Content = wx.BoxSizer(wx.VERTICAL)
        szCol0Content.Add(self.stName, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)
        szCol0Content.AddSpacer(4)
        szCol0Content.Add(self.stInfo, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)

        szCol0 = wx.BoxSizer(wx.HORIZONTAL)
        if media.GetParent().GetFilename() != "":
            szCol0.AddSpacer(24)
        szCol0.Add(self.bmp, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        szCol0.AddSpacer(4)
        szCol0.Add(szCol0Content)

        szCol1 = wx.BoxSizer(wx.VERTICAL)
        if self.pnlOptOrientation:
            szCol1.Add(self.pnlOptOrientation)

        szRow = wx.BoxSizer(wx.HORIZONTAL)
        szRow.Add(szCol0, 3, border=0, flag=0)
        szRow.AddSpacer(4)
        szRow.Add(szCol1, 1, border=0, flag=0)

        szMain = wx.BoxSizer(wx.VERTICAL)
        szMain.Add(szRow, 0, border=4, flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
        szMain.Add(self.staticLine, 0, border=0, flag=wx.EXPAND)
        self.SetSizerAndFit(szMain)

        self.media = media
        self.data = None

        for ctrl in [self, self.stName, self.stInfo, self.pnlOptOrientation]:
            if ctrl:
                ctrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)

        font = self.stName.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stName.SetFont(font)

    def __OnLeftDown(self, event):  # pylint: disable=unused-argument
        evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)
        if isinstance(event.GetEventObject(), wx.Control):
            event.Skip()

    def __OnOrientationChange(self, event):
        self.media.SetProperty("orientation", event.GetValue().value)

    def SetData(self, data):
        self.data = data

    def Select(self, value):
        if value:
            if self.IsShownOnScreen():
                self.SetFocus()
            bgCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            bgCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        self.SetBackgroundColour(bgCol)
        self.stName.SetForegroundColour(txtCol)
        self.stInfo.SetForegroundColour(txtCol)
        if self.pnlOptOrientation:
            self.pnlOptOrientation.SetActive(value)

        self.Refresh()


class PnlOptSelect(wx.Panel):

    def __init__(self, parent, caption, items=None, captionGenerator=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        if items is None:
            items = []
        if captionGenerator is None:
            captionGenerator = lambda x: x

        self._active = False
        self._captionGenerator = captionGenerator
        self._items = items

        self.stName = wx.StaticText(self, id=wx.ID_ANY,
              label=caption + ":", name='stName')

        self.stValue = wx.StaticText(self, id=wx.ID_ANY,
              label="", name='stName')

        self.cbOptions = wx.Choice(self, wx.ID_ANY)
        self.cbOptions.Bind(wx.EVT_CHOICE, self._OnChoice)
        self.cbOptions.Show(False)

        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(self.stName, flag=wx.ALIGN_CENTER_VERTICAL)
        sz.AddSpacer(4)
        sz.Add(self.stValue, flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.cbOptions, flag=wx.EXPAND)
        self.SetSizeHints(wx.Size(-1, self.cbOptions.GetSize()[1]))
        self.SetSizer(sz)

        self.SetItems(items)

    def SetActive(self, value):
        if value:
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        self.stName.SetForegroundColour(txtCol)

        self._active = value
        self.stValue.Show(not value)
        self.stValue.SetLabel(self.cbOptions.GetStringSelection())
        self.cbOptions.Show(value)
        self.GetParent().Layout()
        self.Layout()

    def SetValue(self, value):
        strValue = self._captionGenerator(value)
        self.cbOptions.SetStringSelection(strValue)
        self.stValue.SetLabel(strValue)

    def SetItemCaptionGenerator(self, captionGenerator):
        self._captionGenerator = captionGenerator

    def _OnChoice(self, event):
        selItem = None
        selection = self.cbOptions.GetSelection()
        if selection != wx.NOT_FOUND:
            selItem = self.cbOptions.GetClientData(selection)
        evt = ValueChangeEvent(self.GetId(), selItem)
        self.ProcessEvent(evt)

    def SetItems(self, items):
        for item in items:
            self.cbOptions.Append(self._captionGenerator(item), item)
        if self.cbOptions.GetCount() > 0:
            self.cbOptions.Select(0)
            self.stValue.SetLabel(self._captionGenerator(items[0]))
        self._items = items


EVT_VALUE_CHANGE_TYPE = wx.NewEventType()
EVT_VALUE_CHANGE = wx.PyEventBinder(EVT_VALUE_CHANGE_TYPE, 1)


class ValueChangeEvent(wx.PyCommandEvent):

    def __init__(self, wxId, value):
        wx.PyCommandEvent.__init__(self, EVT_VALUE_CHANGE_TYPE, wxId)
        self._value = value

    def GetValue(self):
        return self._value


class RendererProvider:

    def GetDefault(self):
        return "x264/AC3 (MKV)"

    def GetItems(self):
        result = []
        result.append(
            FormatData("x264/AC3 (MKV)", [],
                       ("matroskamux", "x264enc", "avenc_ac3")))
        result.append(
            FormatData("x264/AAC (MP4)", [],
                       ("mp4mux", "x264enc", "voaacenc")))
        return result
