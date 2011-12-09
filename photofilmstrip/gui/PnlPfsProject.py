#Boa:FramePanel:PnlPfsProject
# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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
import logging

import wx

from photofilmstrip.core.Picture import Picture

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.common.ObserverPattern import Observer

from photofilmstrip.gui.ImageSectionEditor import (
        ImageSectionEditor, ImageProxy, EVT_RECT_CHANGED)
from photofilmstrip.gui.PhotoFilmStripList import (
        PhotoFilmStripList, EVT_CHANGED)

from photofilmstrip.gui.util.ImageCache import ImageCache

from photofilmstrip.gui.PnlEditPicture import PnlEditPicture
from photofilmstrip.gui.PnlAddPics import PnlAddPics
from photofilmstrip.gui.DlgPositionInput import DlgPositionInput
from photofilmstrip.action.ActionAutoPath import ActionAutoPath


[wxID_PNLPFSPROJECT, wxID_PNLPFSPROJECTBITMAPLEFT, 
 wxID_PNLPFSPROJECTBITMAPRIGHT, wxID_PNLPFSPROJECTCMDMOVELEFT, 
 wxID_PNLPFSPROJECTCMDMOVERIGHT, wxID_PNLPFSPROJECTCMDREMOVE, 
 wxID_PNLPFSPROJECTLVPICS, wxID_PNLPFSPROJECTPANELTOP, 
 wxID_PNLPFSPROJECTPNLADDPICS, wxID_PNLPFSPROJECTPNLEDITPICTURE, 
 wxID_PNLPFSPROJECTTOOLBARIMGSECT, 
] = [wx.NewId() for _init_ctrls in range(11)]


[wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT, 
 wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT, 
 wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST, 
 wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH, 
] = [wx.NewId() for _init_coll_toolBarImgSect_Tools in range(4)]

class PnlPfsProject(wx.Panel, Observer):
    
    _custom_classes = {"wx.Panel": ["ImageSectionEditor",
                                    "PnlEditPicture",
                                    "PnlAddPics"],
                       "wx.ListView": ["PhotoFilmStripList"]}
    
    def _init_coll_sizerPictures_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.lvPics, 1, border=0, flag=wx.EXPAND)
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
        parent.AddWindow(self.pnlAddPics, 1, border=0,
              flag=wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.pnlEditPicture, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerPictures, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerPnlTop_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.bitmapLeft, 1, border=2, flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.toolBarImgSect, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.bitmapRight, 1, border=2, flag=wx.ALL | wx.EXPAND)

    def _init_coll_toolBarImgSect_Tools(self, parent):
        # generated method, don't edit

        parent.DoAddTool(bitmap=wx.ArtProvider.GetBitmap('PFS_MOTION_RANDOM',
              wx.ART_TOOLBAR, wx.DefaultSize), bmpDisabled=wx.NullBitmap,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH, kind=wx.ITEM_NORMAL,
              label=u'', longHelp=u'', shortHelp=_(u'Random motion'))
        parent.AddSeparator()
        parent.DoAddTool(bitmap=wx.ArtProvider.GetBitmap('PFS_MOTION_RIGHT',
              wx.ART_TOOLBAR, wx.DefaultSize), bmpDisabled=wx.NullBitmap,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT, kind=wx.ITEM_NORMAL,
              label='', longHelp='', shortHelp=_(u'Set motion end to start'))
        parent.DoAddTool(bitmap=wx.ArtProvider.GetBitmap('PFS_MOTION_LEFT',
              wx.ART_TOOLBAR, wx.DefaultSize), bmpDisabled=wx.NullBitmap,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT, kind=wx.ITEM_NORMAL,
              label=u'', longHelp=u'', shortHelp=_(u'Set motion start to end'))
        parent.AddSeparator()
        parent.DoAddTool(bitmap=wx.ArtProvider.GetBitmap('PFS_MOTION_INPUT',
              wx.ART_TOOLBAR, wx.DefaultSize), bmpDisabled=wx.NullBitmap,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST, kind=wx.ITEM_NORMAL,
              label='', longHelp='',
              shortHelp=_(u'Adjust motion manual'))
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolAutoPath,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTTOPATH)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolLeftToRight,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTFTTORIGHT)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolRightToLeft,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTGHTTOLEFT)
        self.Bind(wx.EVT_TOOL, self.OnToolBarImgSectToolAdjust,
              id=wxID_PNLPFSPROJECTTOOLBARIMGSECTADJUST)

        parent.Realize()

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
        wx.Panel.__init__(self, id=wxID_PNLPFSPROJECT, name=u'PnlPfsProject',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(400, 250))

        self.panelTop = wx.Panel(id=wxID_PNLPFSPROJECTPANELTOP,
              name=u'panelTop', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.bitmapLeft = ImageSectionEditor(id=wxID_PNLPFSPROJECTBITMAPLEFT,
              name=u'bitmapLeft', parent=self.panelTop, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.toolBarImgSect = wx.ToolBar(id=wxID_PNLPFSPROJECTTOOLBARIMGSECT,
              name=u'toolBarImgSect', parent=self.panelTop, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.TB_VERTICAL | wx.NO_BORDER)

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
              style=wx.LC_ICON | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.lvPics.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnLvPicsListItemSelected, id=wxID_PNLPFSPROJECTLVPICS)
        self.lvPics.Bind(wx.EVT_RIGHT_DOWN, self.OnLvPicsRightDown)

        self.cmdMoveLeft = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_BACK',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLPFSPROJECTCMDMOVELEFT,
              name=u'cmdMoveLeft', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdMoveLeft.Bind(wx.EVT_BUTTON, self.OnCmdMoveLeftButton,
              id=wxID_PNLPFSPROJECTCMDMOVELEFT)

        self.cmdMoveRight = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_FORWARD',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_PNLPFSPROJECTCMDMOVERIGHT, name=u'cmdMoveRight',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdMoveRight.Bind(wx.EVT_BUTTON, self.OnCmdMoveRightButton,
              id=wxID_PNLPFSPROJECTCMDMOVERIGHT)

        self.cmdRemove = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_DELETE',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLPFSPROJECTCMDREMOVE,
              name=u'cmdRemove', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdRemove.Bind(wx.EVT_BUTTON, self.OnCmdRemoveButton,
              id=wxID_PNLPFSPROJECTCMDREMOVE)

        self._init_coll_toolBarImgSect_Tools(self.toolBarImgSect)

        self._init_sizers()

    def __init__(self, parent, photoFilmStrip):
        self._init_ctrls(parent)
        Observer.__init__(self)
        
        self.lvPics.SetDropTarget(ImageDropTarget(self))
        
        self.imgProxy = ImageProxy()
        self.imgProxy.AddObserver(self.bitmapLeft)
        self.imgProxy.AddObserver(self.bitmapRight)
        
        self.bitmapLeft.SetImgProxy(self.imgProxy)
        self.bitmapLeft.SetAspect(photoFilmStrip.GetAspect())
        self.bitmapRight.SetImgProxy(self.imgProxy)
        self.bitmapRight.SetAspect(photoFilmStrip.GetAspect())

        self.pnlAddPics.GetButton().Bind(wx.EVT_BUTTON, self.OnImportPics)
        self.pnlAddPics.stInfo.SetDropTarget(ImageDropTarget(self))

        self.cmdMoveLeft.Enable(False)
        self.cmdMoveRight.Enable(False)
        self.cmdRemove.Enable(False)
        self.panelTop.Show(False)
        
        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapLeft.GetId())
        self.Bind(EVT_RECT_CHANGED, self.OnRectChanged, id=self.bitmapRight.GetId())
        
        self.Bind(EVT_CHANGED, self.OnPhotoFilmStripListChanged, id=self.lvPics.GetId())

        self.__photoFilmStrip = photoFilmStrip
        self.__hasChanged = False
        self.__usedAltPath = False
        
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.SetChanged(False)
        
    def GetSelectedImageState(self):
        item = self.lvPics.GetSelected()
        if item == 0:
            if self.lvPics.GetItemCount() == 1:
                kind = 'none'
            else:
                kind = 'first'
        elif item == self.lvPics.GetItemCount() - 1:
            kind = 'last'
        else:
            kind = 'any'
        
        return kind

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
            
            selItm = self.lvPics.GetSelected()
            self.InsertPictures(pics, 
                                selItm + 1 if selItm != wx.NOT_FOUND else None, 
                                autopath=True)
            
            Settings().SetImagePath(os.path.dirname(path))
            
            selIdx = self.lvPics.GetSelected()
            pic = self.lvPics.GetPicture(selIdx)
            self.pnlEditPicture.SetPicture(pic, 
                                           selIdx == self.lvPics.GetItemCount() - 1)
        dlg.Destroy()

    def OnLvPicsListItemSelected(self, event):
        item = event.GetIndex()

        self.cmdMoveLeft.Enable(item > 0)
        self.cmdMoveRight.Enable(item < self.lvPics.GetItemCount() - 1)
        self.cmdRemove.Enable(True)
        
        pic = self.lvPics.GetPicture(item)
        self.imgProxy.SetPicture(pic)

        self.bitmapLeft.SetSection(wx.Rect(*pic.GetStartRect()))
        self.bitmapRight.SetSection(wx.Rect(*pic.GetTargetRect()))

        self.pnlEditPicture.SetPicture(pic, 
                                       item == self.lvPics.GetItemCount() - 1)
        
        event.Skip()

    def OnLvPicsRightDown(self, event):
        pos = event.GetPosition()
        item = self.lvPics.HitTest(pos)
        if item != -1:
            self.lvPics.Select(item)
            
            pic = self.lvPics.GetPicture(item)
            
            menu = wx.Menu()
            ident = wx.NewId()
            item = wx.MenuItem(menu, ident, _(u"Browse"))
            item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, wx.DefaultSize))
            menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnBrowseImage, id=ident)
            self.lvPics.PopupMenu(menu)

            event.Skip()

    def OnBrowseImage(self, event):
        dlg = wx.FileDialog(self, _(u"Import image"), 
                            Settings().GetImagePath(), "", 
                            _(u"Imagefiles") + " (*.*)|*.*", 
                            wx.OPEN | wx.FD_PREVIEW)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            item = self.lvPics.GetSelected()
            orgPic = self.lvPics.GetPicture(item)
            
            pic = Picture(path)
            pic.SetComment(orgPic.GetComment())
            pic.SetDuration(orgPic.GetDuration())
            pic.SetEffect(orgPic.GetEffect())
            pic.SetRotation(orgPic.GetRotation())
            pic.SetStartRect(orgPic.GetStartRect())
            pic.SetTargetRect(orgPic.GetTargetRect())

            ImageCache().RegisterPicture(pic)
                        
            self.lvPics.SetPicture(item, pic)
            pic.AddObserver(self)
            pic.Notify('bitmap')
            
            Settings().SetImagePath(os.path.dirname(path))
            
            self.SetChanged(True)
        dlg.Destroy()

    def OnRectChanged(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem)
        if pic is None:
            return
        if event.GetEventObject() is self.bitmapLeft:
            pic.SetStartRect(tuple(self.bitmapLeft.GetSection()))
        else:
            pic.SetTargetRect(tuple(self.bitmapRight.GetSection()))

    def OnCmdMoveLeftButton(self, event):
        selItem = self.lvPics.GetSelected()
        self.lvPics.SwapPictures(selItem, selItem - 1)
        self.lvPics.Select(selItem - 1)
        
        self.SetChanged(True)

    def OnCmdMoveRightButton(self, event):
        selItem = self.lvPics.GetSelected()
        self.lvPics.SwapPictures(selItem, selItem + 1)
        self.lvPics.Select(selItem + 1)

        self.SetChanged(True)

    def OnCmdRemoveButton(self, event):
        selItem = self.lvPics.GetSelected()
        self.lvPics.DeleteItem(selItem)
        
        if selItem > self.lvPics.GetItemCount() - 1:
            selItem = self.lvPics.GetItemCount() - 1
        self.lvPics.Select(selItem)
        
        if self.lvPics.GetItemCount() == 0:
            self.imgProxy.SetPicture(None)
            self.pnlEditPicture.SetPicture(None)
            self.pnlEditPicture.Enable(False)
            self.cmdMoveLeft.Enable(False)
            self.cmdMoveRight.Enable(False)
            
            self.pnlAddPics.Show(True)
            self.panelTop.Show(False)
        
        evt = UpdateStatusbarEvent(self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
        self.cmdRemove.Enable(self.lvPics.GetItemCount() > 0)
        
        self.Layout()

    def OnPhotoFilmStripListChanged(self, event):
        self.__photoFilmStrip.SetPictures(self.lvPics.GetPictures())
        self.SetChanged(True)

    def OnToolBarImgSectToolAutoPath(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem)
        if pic is None:
            return
        actAp = ActionAutoPath(pic, self.__photoFilmStrip.GetAspect())
        actAp.Execute()

    def OnToolBarImgSectToolLeftToRight(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem)
        if pic is None:
            return
        pic.SetTargetRect(pic.GetStartRect())

    def OnToolBarImgSectToolRightToLeft(self, event):
        selItem = self.lvPics.GetSelected()
        pic = self.lvPics.GetPicture(selItem)
        if pic is None:
            return
        pic.SetStartRect(pic.GetTargetRect())

    def OnToolBarImgSectToolAdjust(self, event):
        selItem = self.lvPics.GetSelected()
        selPic = self.lvPics.GetPicture(selItem)
        
        dlg = DlgPositionInput(self, selPic, self.__photoFilmStrip.GetAspect())
        dlg.ShowModal()
        dlg.Destroy()

    def Close(self):
        self.imgProxy.RemoveObserver(self.bitmapLeft)
        self.imgProxy.RemoveObserver(self.bitmapRight)
        self.imgProxy.Destroy()

    def GetPhotoFilmStrip(self):
        return self.__photoFilmStrip

    def InsertPictures(self, pics, position=None, autopath=False):
        logging.debug("InsertPictures(pos=%s)", position)
        if position is None:
            position = self.lvPics.GetItemCount()
        
        for idx, pic in enumerate(pics):
            if autopath:
                actAp = ActionAutoPath(pic, self.__photoFilmStrip.GetAspect())
                actAp.Execute()

            self.lvPics.InsertPicture(position, pic)
            position += 1 

            pic.AddObserver(self)

        if self.lvPics.GetSelected() == -1:
            self.lvPics.Select(0)
            
        evt = UpdateStatusbarEvent(self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
        
        self.SetChanged(True)

        self.pnlAddPics.Show(self.lvPics.GetItemCount() == 0)
        self.panelTop.Show(self.lvPics.GetItemCount() != 0)
        self.Layout()
        
        self.lvPics.SetFocus()

    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, Picture):
            if arg == 'bitmap':
                self.imgProxy.SetPicture(obj)
                self.lvPics.Refresh()
            
            if arg == 'duration':
                evt = UpdateStatusbarEvent(self.GetId())
                self.GetEventHandler().ProcessEvent(evt)

            if arg == 'start':
                self.bitmapLeft.SetSection(wx.Rect(*obj.GetStartRect()))

            if arg == 'target':
                self.bitmapRight.SetSection(wx.Rect(*obj.GetTargetRect()))
             
            self.SetChanged(True)

    def UpdateProperties(self):
        self.bitmapLeft.SetAspect(self.__photoFilmStrip.GetAspect())
        self.bitmapRight.SetAspect(self.__photoFilmStrip.GetAspect())
        self.SetChanged(True)

        evt = UpdateStatusbarEvent(self.GetId())
        self.GetEventHandler().ProcessEvent(evt)
    
    def IsReady(self):
        return self.lvPics.GetItemCount() > 0
        
    def IsPictureSelected(self):
        return self.lvPics.GetSelected() >= 0
    
    def SetChanged(self, changed=True):
        self.__hasChanged = changed
    def HasChanged(self):
        return self.__hasChanged
    
    
        
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


_EVT_UPDATE_STATUSBAR_TYPE  = wx.NewEventType()
EVT_UPDATE_STATUSBAR        = wx.PyEventBinder(_EVT_UPDATE_STATUSBAR_TYPE, 1)


class UpdateStatusbarEvent(wx.PyCommandEvent):
    def __init__(self, wxId):
        wx.PyCommandEvent.__init__(self, _EVT_UPDATE_STATUSBAR_TYPE, wxId)
