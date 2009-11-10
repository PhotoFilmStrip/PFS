#Boa:Frame:FrmMain
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os

import wx
from wx.lib.wordwrap import wordwrap

from core.Picture import Picture
from core.PhotoFilmStrip import PhotoFilmStrip, UserInteractionHandler

from lib.Settings import Settings
from lib.UpdateChecker import UpdateChecker
from lib.common.ObserverPattern import Observer

from gui.ctrls.ImageSectionEditor import ImageSectionEditor, EVT_RECT_CHANGED
from gui.ctrls.PhotoFilmStripList import PhotoFilmStripList, EVT_CHANGED

from gui.util.ImageCache import ImageCache
from gui.util.ImageProxy import ImageProxy

from gui.DlgRender import DlgRender
from gui.DlgUpdateInfo import DlgUpdateInfo
from gui.PnlEditPicture import PnlEditPicture
from gui.PnlWelcome import PnlWelcome
from gui.ActionManager import ActionManager
from gui.HelpViewer import HelpViewer

from res.license import licenseText


[wxID_FRMMAIN, wxID_FRMMAINBITMAPLEFT, wxID_FRMMAINBITMAPRIGHT, 
 wxID_FRMMAINCMDMOVELEFT, wxID_FRMMAINCMDMOVERIGHT, wxID_FRMMAINCMDREMOVE, 
 wxID_FRMMAINLISTVIEW, wxID_FRMMAINPANELTOP, wxID_FRMMAINPNLEDITPICTURE, 
] = [wx.NewId() for _init_ctrls in range(9)]


class FrmMain(wx.Frame, Observer, UserInteractionHandler):
    
    _custom_classes = {"wx.Panel": ["ImageSectionEditor",
                                    "PnlEditPicture"],
                       "wx.ListView": ["PhotoFilmStripList"]}
    
    def _init_coll_sizerPictures_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.listView, 1, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerPictureCtrls, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerPictureCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdMoveLeft, 0, border=2, flag=wx.ALL)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdMoveRight, 0, border=2, flag=wx.ALL)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdRemove, 0, border=2, flag=wx.ALL)

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panelTop, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.pnlEditPicture, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerPictures, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerPnlTop_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.bitmapLeft, 1, border=2, flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.bitmapRight, 1, border=2, flag=wx.ALL | wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerPnlTop = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerPictures = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerPictureCtrls = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_sizerPnlTop_Items(self.sizerPnlTop)
        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_sizerPictures_Items(self.sizerPictures)
        self._init_coll_sizerPictureCtrls_Items(self.sizerPictureCtrls)

        self.SetSizer(self.sizerMain)
        self.panelTop.SetSizer(self.sizerPnlTop)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRMMAIN, name=u'FrmMain', parent=prnt,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL, title='PhotoFilmStrip')
        self.SetClientSize(wx.Size(400, 250))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.panelTop = wx.Panel(id=wxID_FRMMAINPANELTOP, name=u'panelTop',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.bitmapLeft = ImageSectionEditor(id=wxID_FRMMAINBITMAPLEFT,
              name=u'bitmapLeft', parent=self.panelTop, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.bitmapRight = ImageSectionEditor(id=wxID_FRMMAINBITMAPRIGHT,
              name=u'bitmapRight', parent=self.panelTop, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.pnlEditPicture = PnlEditPicture(id=wxID_FRMMAINPNLEDITPICTURE,
              name=u'pnlEditPicture', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.listView = PhotoFilmStripList(id=wxID_FRMMAINLISTVIEW, 
              name=u'listView', parent=self, pos=wx.Point(-1, -1), 
              size=wx.Size(-1, -1),
              style=wx.LC_ICON | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.listView.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListViewListItemSelected, id=wxID_FRMMAINLISTVIEW)
        self.listView.Bind(wx.EVT_RIGHT_DOWN, self.OnListViewRightDown)

        self.cmdMoveLeft = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_BACK',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_FRMMAINCMDMOVELEFT,
              name=u'cmdMoveLeft', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdMoveLeft.Bind(wx.EVT_BUTTON, self.OnCmdMoveLeftButton,
              id=wxID_FRMMAINCMDMOVELEFT)

        self.cmdMoveRight = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_FORWARD',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_FRMMAINCMDMOVERIGHT,
              name=u'cmdMoveRight', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdMoveRight.Bind(wx.EVT_BUTTON, self.OnCmdMoveRightButton,
              id=wxID_FRMMAINCMDMOVERIGHT)

        self.cmdRemove = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_DELETE',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_FRMMAINCMDREMOVE,
              name=u'cmdRemove', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdRemove.Bind(wx.EVT_BUTTON, self.OnCmdRemoveButton,
              id=wxID_FRMMAINCMDREMOVE)

        self._init_sizers()

    def __init__(self):
        self._init_ctrls(None)
        Observer.__init__(self)
        self.SetTitle(Settings.APP_NAME)
        
        iconBundle = wx.IconBundle()
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_32", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_48", wx.ART_OTHER))
        self.SetIcons(iconBundle)
        
        self.listView.SetDropTarget(ImageDropTarget(self))
        
        self.imgProxy = ImageProxy()
        self.imgProxy.AddObserver(self.bitmapLeft)
        self.imgProxy.AddObserver(self.bitmapRight)
        
        self.bitmapLeft.SetDropTarget(ProjectDropTarget(self))
        self.bitmapLeft.SetImgProxy(self.imgProxy)

        self.bitmapRight.SetDropTarget(ProjectDropTarget(self))
        self.bitmapRight.SetImgProxy(self.imgProxy)
        
#        self.pnlWelcome = PnlWelcome(self.bitmapLeft)
#        self.pnlWelcome.GetButton().Bind(wx.EVT_BUTTON, self.OnImportPics)
#        self.pnlWelcome.stInfo.SetDropTarget(ImageDropTarget(self))
        
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        sizer.AddStretchSpacer(1)
#        sizer.Add(self.pnlWelcome, 0, wx.ALIGN_CENTER)
#        sizer.AddStretchSpacer(1)
#        self.bitmapLeft.SetSizer(sizer)
        
        self.statusBar = wx.StatusBar(self)
        self.statusBar.SetFieldsCount(3)
        self.SetStatusBar(self.statusBar)
        
        self.actionManager = ActionManager()
        
        menuBar = self.actionManager.GetMenuBar()
        self.SetMenuBar(menuBar)
        toolBar = self.actionManager.GetToolBar(self)
        self.SetToolBar(toolBar)

        self.Bind(wx.EVT_MENU, self.OnProjectNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnProjectLoad, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU_RANGE, self.OnProjectLoadFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        self.Bind(wx.EVT_MENU, self.OnProjectSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnProjectSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnProjectExport, id=ActionManager.ID_PROJECT_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnProjectImport, id=ActionManager.ID_PROJECT_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnCmdMoveLeftButton, id=ActionManager.ID_PIC_MOVE_LEFT)
        self.Bind(wx.EVT_MENU, self.OnCmdMoveRightButton, id=ActionManager.ID_PIC_MOVE_RIGHT)
        self.Bind(wx.EVT_MENU, self.OnCmdRemoveButton, id=ActionManager.ID_PIC_REMOVE)

        self.Bind(wx.EVT_MENU, self.pnlEditPicture.OnCmdRotateLeftButton, id=ActionManager.ID_PIC_ROTATE_CCW)
        self.Bind(wx.EVT_MENU, self.pnlEditPicture.OnCmdRotateRightButton, id=ActionManager.ID_PIC_ROTATE_CW)

        self.Bind(wx.EVT_MENU, self.OnImportPics, id=ActionManager.ID_PIC_IMPORT)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpIndex, id=wx.ID_HELP)

        self.Bind(wx.EVT_MENU, self.OnRenderFilmstrip, id=ActionManager.ID_RENDER_FILMSTRIP)
        
        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapLeft.GetId())
        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapRight.GetId())
        
        self.Bind(EVT_CHANGED, self.OnPhotoFilmStripListChanged, id=self.listView.GetId())

        self.SetBackgroundColour(toolBar.GetBackgroundColour())
        self.SetInitialSize(self.GetEffectiveMinSize())
        
        self.actionManager.OnPictureSelected(False)
        self.actionManager.OnProjectChanged(False)
        self.actionManager.OnProjectReady(False)

        self.__currentProject = None
        self.__usedAltPath = False
        
        at = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP_CONTENTS)])
        self.SetAcceleratorTable(at)
        self.Bind(wx.EVT_MENU, self.OnHelpContent, id=wx.ID_HELP_CONTENTS)
        
        self.NewProject(False)
        
        self.__updateChecker = UpdateChecker()
        wx.CallLater(500, self.__NotifyUpdate)
        
    def __NotifyUpdate(self):
        if not self.__updateChecker.IsDone():
            wx.CallLater(500, self.__NotifyUpdate)
        if not self.__updateChecker.IsOk():
            return
        if not self.__updateChecker.IsNewer(Settings.APP_VERSION):
            return
        
        dlg = DlgUpdateInfo(self, 
                            "%s %s" % (Settings.APP_NAME, self.__updateChecker.GetVersion()),
                            wx.ArtProvider_GetBitmap("PFS_ICON_48", wx.ART_OTHER),
                            Settings.APP_URL,
                            self.__updateChecker.GetChanges())
        dlg.ShowModal()
        dlg.Destroy()

    def __GetMoveImageState(self):
        item = self.listView.GetSelected()
        if item == 0:
            if self.listView.GetItemCount() == 1:
                kind = 'none'
            else:
                kind = 'first'
        elif item == self.listView.GetItemCount() - 1:
            kind = 'last'
        else:
            kind = 'any'
        
        return kind

    def OnClose(self, event):
        if self.CheckAndAskSaving():
            self.imgProxy.Destroy()
            self.Destroy()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = Settings.APP_NAME
        info.Version = Settings.APP_VERSION
        info.Copyright = u"(C) 2009 %s" % Settings.DEVELOPERS[0]
        info.Description = wordwrap(Settings.APP_DESCRIPTION, 350, wx.ClientDC(self))
        info.WebSite = (Settings.APP_URL, "%s %s" % (Settings.APP_NAME, _(u"online")))
        info.Developers = Settings.DEVELOPERS

        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        wx.AboutBox(info)
        
    def OnProjectNew(self, event):
        self.NewProject()
        
    def OnProjectLoad(self, event):
        if not self.CheckAndAskSaving():
            return

        dlg = wx.FileDialog(self, _(u"Select %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            Settings.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath())
            
    def OnProjectLoadFileHistory(self, event):
        if not self.CheckAndAskSaving():
            return

        fileNum = event.GetId() - wx.ID_FILE1
        path = self.actionManager.GetHistoryFile(fileNum)
        self.LoadProject(path)
        
    def OnProjectSave(self, event):
        if self.__currentProject:
            return self.SaveProject(self.__currentProject, False)
        else:
            return self.OnProjectSaveAs(event)

    def OnProjectSaveAs(self, event):
        dlg = wx.FileDialog(self, _(u"Save %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), 
                            self.__currentProject if self.__currentProject else "photofilmstrip", 
                            Settings.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".pfs":
                filepath += ".pfs"
                
            if os.path.isfile(filepath):
                dlg2 = wx.MessageDialog(self,
                                        _(u"Overwrite existing file '%s'?") % filepath, 
                                        _(u"Question"),
                                        wx.YES_NO | wx.ICON_QUESTION)
                if dlg2.ShowModal() == wx.ID_NO:
                    return False
                
            return self.SaveProject(filepath, False)
        return False
    
    def OnProjectExport(self, event):
        dlg = wx.FileDialog(self, _(u"Export %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), 
                            self.__currentProject if self.__currentProject else "photofilmstrip", 
                            u"%s %s-%s %s" % (_(u"Portable"), Settings.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".ppfs":
                filepath += ".ppfs"
            self.SaveProject(filepath, True)

    def OnProjectImport(self, event):
        if not self.CheckAndAskSaving():
            return

        dlg = wx.FileDialog(self, _(u"Import %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            u"%s %s-%s %s" % (_(u"Portable"), Settings.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath(), True)

    def OnRenderFilmstrip(self, event):
        photoFilmStrip = PhotoFilmStrip(self.__currentProject)
        photoFilmStrip.SetPictures(self.listView.GetPictures())
        dlg = DlgRender(self, photoFilmStrip)
        dlg.ShowModal()
        dlg.Destroy()

    def OnImportPics(self, event):
        dlg = wx.FileDialog(self, _(u"Import images"), 
                            Settings().GetImagePath(), "", 
                            _(u"Imagefiles") + " (*.*)|*.*", 
                            wx.OPEN | wx.FD_MULTIPLE | wx.FD_PREVIEW)
        if dlg.ShowModal() == wx.ID_OK:
            pics = []
            for path in dlg.GetPaths():
                pic = Picture(path)
                pics.append(pic)
            
            self.InsertPictures(pics, autopath=True)
            
            Settings().SetImagePath(os.path.dirname(path))
        dlg.Destroy()

    def OnListViewListItemSelected(self, event):
        item = event.GetIndex()

        self.cmdMoveLeft.Enable(item > 0)
        self.cmdMoveRight.Enable(item < self.listView.GetItemCount() - 1)
        self.cmdRemove.Enable(True)
        
        pic = self.listView.GetPicture(item)
        self.imgProxy.SetPicture(pic)

        self.bitmapLeft.SetSection(wx.Rect(*pic.GetStartRect()))
        self.bitmapRight.SetSection(wx.Rect(*pic.GetTargetRect()))

        self.pnlEditPicture.SetPicture(pic)
        
        self.actionManager.OnPictureSelected(True, self.__GetMoveImageState())

        event.Skip()

    def OnListViewRightDown(self, event):
        pos = event.GetPosition()
        item = self.listView.HitTest(pos)
        if item != -1:
            self.listView.Select(item)
            
            pic = self.listView.GetPicture(item)
            
            menu = wx.Menu()
            ident = wx.NewId()
            item = wx.MenuItem(menu, ident, _(u"Browse"))
            item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, wx.DefaultSize))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnBrowseImage, id=ident)
            self.listView.PopupMenu(menu)

            event.Skip()

    def OnBrowseImage(self, event):
        dlg = wx.FileDialog(self, _(u"Import image"), 
                            Settings().GetImagePath(), "", 
                            _(u"Imagefiles") + " (*.*)|*.*", 
                            wx.OPEN | wx.FD_PREVIEW)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            item = self.listView.GetSelected()
            orgPic = self.listView.GetPicture(item)
            
            pic = Picture(path)
            pic.SetComment(orgPic.GetComment())
            pic.SetDuration(orgPic.GetDuration())
            pic.SetEffect(orgPic.GetEffect())
            pic.SetRotation(orgPic.GetRotation())
            pic.SetStartRect(orgPic.GetStartRect())
            pic.SetTargetRect(orgPic.GetTargetRect())

            ImageCache().RegisterPicture(pic)
                        
            self.listView.SetPicture(item, pic)
            pic.AddObserver(self)
            pic.Notify('bitmap')
            
            Settings().SetImagePath(os.path.dirname(path))
            
            self.actionManager.OnProjectChanged(True)
        dlg.Destroy()

    def OnRectChanged(self, event):
        selItem = self.listView.GetSelected()
        pic = self.listView.GetPicture(selItem)
        if pic is None:
            return
        if event.GetEventObject() is self.bitmapLeft:
            pic.SetStartRect(tuple(self.bitmapLeft.GetSection()))
        else:
            pic.SetTargetRect(tuple(self.bitmapRight.GetSection()))

    def OnCmdMoveLeftButton(self, event):
        selItem = self.listView.GetSelected()
        self.listView.SwapPictures(selItem, selItem - 1)
        self.listView.Select(selItem - 1)
        
        self.actionManager.OnProjectChanged(True)

    def OnCmdMoveRightButton(self, event):
        selItem = self.listView.GetSelected()
        self.listView.SwapPictures(selItem, selItem + 1)
        self.listView.Select(selItem + 1)

        self.actionManager.OnProjectChanged(True)

    def OnCmdRemoveButton(self, event):
        selItem = self.listView.GetSelected()
        self.listView.DeleteItem(selItem)
        
        if selItem > self.listView.GetItemCount() - 1:
            selItem = self.listView.GetItemCount() - 1
        self.listView.Select(selItem)
        
        if self.listView.GetItemCount() == 0:
            self.imgProxy.SetPicture(None)
            self.pnlEditPicture.SetPicture(None)
            self.pnlEditPicture.Enable(False)
            self.cmdMoveLeft.Enable(False)
            self.cmdMoveRight.Enable(False)
#            self.pnlWelcome.Show(True)
        
        self.UpdateStatusText()
        self.cmdRemove.Enable(self.listView.GetItemCount() > 0)
        self.actionManager.OnPictureSelected(self.listView.GetItemCount() > 0,
                                             self.__GetMoveImageState())
        self.actionManager.OnProjectReady(self.listView.GetItemCount() > 0)
        self.actionManager.OnProjectChanged(True)

    def OnHelpIndex(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_INDEX)
        event.Skip()
    def OnHelpContent(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_CREATE_PFS)
        event.Skip()
        
    def OnPhotoFilmStripListChanged(self, event):
        self.actionManager.OnProjectChanged(True)

    def CheckAndAskSaving(self):
        if self.actionManager.CanSave():
            name = self.__currentProject
            if not name:
                name = _(u"Unnamed PhotoFilmStrip")
                
            dlg = wx.MessageDialog(self,
                                   _(u"'%s' has been modified. Save changes?") % name, 
                                   _(u"Question"),
                                   wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            dlg.Destroy()
            
            if response == wx.ID_CANCEL:
                return False
            elif response == wx.ID_YES and not self.OnProjectSave(None):
                return False
        return True

    def UpdateStatusText(self):
        pics = self.listView.GetPictures()

        imgCount = len(pics)
        self.statusBar.SetStatusText("%s: %d" % (_(u"Images"), imgCount), 1)
        
        totalTime = 0
        for pic in pics:
            totalTime += pic.GetDuration()
        minutes = totalTime / 60
        seconds = totalTime % 60
        self.statusBar.SetStatusText("%s: %02d:%02d" % (_(u"Duration"), 
                                                        minutes, 
                                                        seconds), 2)

    def NewProject(self, askSaving=True):
        if askSaving and not self.CheckAndAskSaving():
            return

        self.listView.DeleteAllItems()
        self.imgProxy.SetPicture(None)
        
        ImageCache().ClearCache()

        self.cmdMoveLeft.Enable(False)
        self.cmdMoveRight.Enable(False)
        self.cmdRemove.Enable(False)
        self.pnlEditPicture.Enable(False)

        self.actionManager.OnPictureSelected(False)
        self.actionManager.OnProjectChanged(False)
        self.actionManager.OnProjectReady(False)

        self.SetTitle(Settings.APP_NAME)
        self.__currentProject = None
        self.UpdateStatusText()
        
    def GetAltPath(self, imgPath):
        """
        overridden method from UserInteractionHandler
        """
        dlg = wx.MessageDialog(self,
                               _(u"Some images does not exist in the folder '%s' anymore. If the files has moved you can select the new path. Do you want to select a new path?") % imgPath, 
                               _(u"Question"),
                               wx.YES_NO | wx.ICON_QUESTION)
        resp = dlg.ShowModal()
        dlg.Destroy()
        if resp == wx.ID_NO:
            return imgPath
        
        dlg = wx.DirDialog(self, defaultPath=Settings().GetImagePath())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.__usedAltPath = True
                return path
        finally:
            dlg.Destroy()

        return imgPath

    def LoadProject(self, filepath, skipHistory=False):
        self.NewProject(False)
        
        self.__usedAltPath = False
        photoFilmStrip = PhotoFilmStrip()
        photoFilmStrip.SetUserInteractionHandler(self)
        if not photoFilmStrip.Load(filepath):
            dlg = wx.MessageDialog(self,
                                   _(u"Invalid %(app)s-Project: %(file)s") % {"app": Settings.APP_NAME,
                                                                              "file": filepath}, 
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        pics = photoFilmStrip.GetPictures()
        
        self.InsertPictures(pics)

        self.__currentProject = filepath
        self.SetTitle(Settings.APP_NAME + ' - ' + filepath)

        if not skipHistory:
            self.actionManager.AddFileToHistory(filepath)
        
        self.actionManager.OnProjectChanged(self.__usedAltPath)
        self.actionManager.OnProjectReady(True)
        
        Settings().SetProjectPath(os.path.dirname(filepath))
    
    def SaveProject(self, filepath, includePics):
        pics = self.listView.GetPictures()
        photoFilmStrip = PhotoFilmStrip()
        photoFilmStrip.SetPictures(pics)
        try:
            photoFilmStrip.Save(filepath, includePics)
        except StandardError, err:
            dlg = wx.MessageDialog(self,
                                   _(u"Could not save the file '%(file)s': %(errMsg)s") % \
                                            {'file': filepath,
                                             'errMsg': unicode(err)}, 
                                   _(u"Question"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if not includePics:
            self.actionManager.AddFileToHistory(filepath)
        
        self.__currentProject = filepath
        self.SetTitle(Settings.APP_NAME + ' - ' + filepath)
        self.actionManager.OnProjectChanged(False)
        return True
    
    def InsertPictures(self, pics, position=None, autopath=False):
        if position is None:
            position = self.listView.GetItemCount()
        
        dlg = wx.ProgressDialog(_(u"Please wait"),
                                _(u"Loading pictures..."),
                                maximum = len(pics),
                                parent=self,
                                style = wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)

        for idx, pic in enumerate(pics):
            if autopath:
                pic.AutoPath(ImageSectionEditor.RATIO)

            ImageCache().RegisterPicture(pic)

            self.listView.InsertPicture(position, pic)
            position += 1 

            pic.AddObserver(self)

            dlg.Update(idx + 1)
        
        if self.listView.GetSelected() == -1:
            self.listView.Select(0)
            
        dlg.Destroy()
        
        self.UpdateStatusText()
        self.actionManager.OnProjectReady(self.listView.GetItemCount() > 0)
        self.actionManager.OnProjectChanged(True)
#        self.pnlWelcome.Show(self.listView.GetItemCount() == 0)

    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, Picture):
            if arg == 'bitmap':
                ImageCache().UpdatePicture(obj)
                self.imgProxy.SetPicture(obj)
                self.listView.UpdatePictures()
            
            if arg == 'duration':
                self.UpdateStatusText()
             
            self.actionManager.OnProjectChanged(True)

        
class ImageDropTarget(wx.FileDropTarget):
    def __init__(self, frmMain):
        wx.FileDropTarget.__init__(self)
        self.frmMain = frmMain

    def OnDropFiles(self, x, y, filenames):
        itm = self.frmMain.listView.HitTest((x, y))
        
        pics = [] 
        for path in filenames:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                pic = Picture(path)
                pics.append(pic)

        if pics:
            self.frmMain.InsertPictures(pics, itm + 1 if itm != wx.NOT_FOUND else None, True)
            return True
        return False
    

class ProjectDropTarget(wx.FileDropTarget):
    def __init__(self, frmMain):
        wx.FileDropTarget.__init__(self)
        self.frmMain = frmMain

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) == 1:
            path = filenames[0]
            ext = os.path.splitext(path)[1].lower()
            if ext == '.pfs':

                if not self.frmMain.CheckAndAskSaving():
                    return False

                self.frmMain.LoadProject(path)
                return True

        return False
