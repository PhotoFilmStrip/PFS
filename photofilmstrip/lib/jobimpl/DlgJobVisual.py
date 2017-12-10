# Boa:Dialog:DlgJobVisual
# encoding: UTF-8

import time

import wx

from .WxVisualJobHandler import WxVisualJobHandler, EVT_JOB_UPDATE

[wxID_DLGJOBVISUAL, wxID_DLGJOBVISUALCMDABORT, wxID_DLGJOBVISUALGAUGE,
 wxID_DLGJOBVISUALSTELAPSEDDIV, wxID_DLGJOBVISUALSTELAPSEDLABEL,
 wxID_DLGJOBVISUALSTELAPSEDVALUE, wxID_DLGJOBVISUALSTINFO,
 wxID_DLGJOBVISUALSTREMAININGDIV, wxID_DLGJOBVISUALSTREMAININGLABEL,
 wxID_DLGJOBVISUALSTREMAININGVALUE,
] = [wx.NewId() for _init_ctrls in range(10)]


class DlgJobVisual(wx.Dialog, WxVisualJobHandler):

    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stInfo, 0, border=8, flag=wx.ALL)
        parent.Add(self.gauge, 0, border=8, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.szTiming, 0, border=8, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.cmdAbort, 0, border=8,
              flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

    def _init_coll_szTiming_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stElapsedLabel, 0, border=0, flag=wx.ALIGN_RIGHT)
        parent.Add(self.stElapsedDiv, 0, border=4,
              flag=wx.RIGHT | wx.LEFT)
        parent.Add(self.stElapsedValue, 0, border=8, flag=wx.LEFT)
        parent.Add(self.stRemainingLabel, 0, border=0,
              flag=wx.ALIGN_RIGHT)
        parent.Add(self.stRemainingDiv, 0, border=4,
              flag=wx.RIGHT | wx.LEFT)
        parent.Add(self.stRemainingValue, 0, border=8, flag=wx.LEFT)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szTiming = wx.FlexGridSizer(cols=3, hgap=0, rows=2, vgap=8)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szTiming_Items(self.szTiming)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGJOBVISUAL, name=u'DlgJobVisual',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_DIALOG_STYLE, title='')
        self.SetClientSize(wx.Size(400, 250))
        self.SetSizeHints(350, -1, -1, -1)

        self.stInfo = wx.StaticText(id=wxID_DLGJOBVISUALSTINFO, label=u'Info',
              name=u'stInfo', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.gauge = wx.Gauge(id=wxID_DLGJOBVISUALGAUGE, name=u'gauge',
              parent=self, pos=wx.Point(-1, -1), range=100,
              size=wx.Size(-1, -1), style=wx.GA_HORIZONTAL)

        self.stElapsedLabel = wx.StaticText(id=wxID_DLGJOBVISUALSTELAPSEDLABEL,
              label=_(u'Elapsed time'), name=u'stElapsedLabel', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=wx.ALIGN_RIGHT)

        self.stElapsedDiv = wx.StaticText(id=wxID_DLGJOBVISUALSTELAPSEDDIV,
              label=u':', name=u'stElapsedDiv', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stElapsedValue = wx.StaticText(id=wxID_DLGJOBVISUALSTELAPSEDVALUE,
              label=u'0:00:00', name=u'stElapsedValue', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stRemainingLabel = wx.StaticText(id=wxID_DLGJOBVISUALSTREMAININGLABEL,
              label=_(u'Remaining time'), name=u'stRemainingLabel', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stRemainingDiv = wx.StaticText(id=wxID_DLGJOBVISUALSTREMAININGDIV,
              label=u':', name=u'stRemainingDiv', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stRemainingValue = wx.StaticText(id=wxID_DLGJOBVISUALSTREMAININGVALUE,
              label=u'0:00:00', name=u'stRemainingValue', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdAbort = wx.Button(id=wxID_DLGJOBVISUALCMDABORT,
              label=_(u'&Cancel'), name=u'cmdAbort', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cmdAbort.Show(False)
        self.cmdAbort.Bind(wx.EVT_BUTTON, self.__OnCancel,
              id=wxID_DLGJOBVISUALCMDABORT)

        self._init_sizers()

    def __init__(self, parent, job):
        self._init_ctrls(parent)
        WxVisualJobHandler.__init__(self)
        self.SetTitle(job.GetName())

        if self.cmdAbort.IsShown():
            self.__state = "Continue"
        else:
            self.__state = "Uncancelable"

        self.__job = job
        self.__delay = 3
        self.__maximum = 100
        self.__display_estimated = 0
        self.__last_timeupdate = 0
        self.__ctdelay = 0
        self.__timeStart = time.time()

        self.Bind(wx.EVT_CLOSE, self.__OnClose)
        self.Bind(EVT_JOB_UPDATE, self.__OnJobUpdate)

    def __OnCancel(self, event):
        if self.__state == "Finished":
            event.Skip()
        else:
            self.__state = "Canceled"
#            self.DisableAbort()
#            self.DisableSkip()

            self.__timeStop = time.time()

    def __OnClose(self, event):
        if self.__state == "Uncancelable":
            event.Veto()
        elif self.__state == "Finished":
            event.Skip()
        else:
            self.__state = "Canceled"
#            self.DisableAbort()
#            self.DisableSkip()
            self.__timeStop = time.time()

    def __Pulse(self, newmsg):
        self.gauge.Pulse()
        self.__UpdateMessage(newmsg)

        if 1:  # self.__elapsed or self.__remaining or self.__estimated:
            elapsed = time.time() - self.__timeStart

            self.__SetTimeLabel(elapsed, self.stElapsedValue)
#            self.__SetTimeLabel(-1, self.stEstimated)
            self.__SetTimeLabel(-1, self.stRemainingValue)

    def __Update(self, value, msg):
        if value <= self.__maximum:
            self.gauge.SetValue(value)
        self.__UpdateMessage(msg)

#        if (self.__elapsed or self.__remaining or self.__estimated) and (value != 0):
        if value != 0:
            elapsed = time.time() - self.__timeStart
            if self.__last_timeupdate < elapsed or value == self.__maximum:
                self.__last_timeupdate = elapsed
                estimated = (elapsed * self.__maximum) / float(value)
                if estimated > self.__display_estimated and self.__ctdelay >= 0:
                    self.__ctdelay += 1
                elif estimated < self.__display_estimated and self.__ctdelay <= 0:
                    self.__ctdelay -= 1
                else:
                    self.__ctdelay = 0

                if self.__ctdelay >= self.__delay \
                or self.__ctdelay <= (self.__delay * -1) \
                or value == self.__maximum \
                or elapsed > self.__display_estimated \
                or (elapsed > 0 and elapsed < 4):
                    self.__display_estimated = estimated
                    self.__ctdelay = 0

            display_remaining = self.__display_estimated - elapsed
            if display_remaining < 0:
                display_remaining = 0;

            self.__SetTimeLabel(elapsed, self.stElapsedValue)
#            self.__SetTimeLabel(m_display_estimated, self.stEstimated)
            self.__SetTimeLabel(display_remaining, self.stRemainingValue)

    def __UpdateMessage(self, newmsg):
        if newmsg and newmsg != self.stInfo.GetLabel():
            self.stInfo.SetLabel(newmsg)

    def __SetTimeLabel(self, val, staticText):
        if val != -1:
            hours = val / 3600
            minutes = (val % 3600) / 60
            seconds = val % 60
            s = "%d:%02d:%02d" % (hours, minutes, seconds)
        else:
            s = _("Unknown")

        if s != staticText.GetLabel():
            staticText.SetLabel(s)

    def __OnJobUpdate(self, event):
        if event.IsBegin():
            self.__timeStart = time.time()
#            self.__dlg = wx.ProgressDialog(self.__job.GetName(),
#                                           self.__job.GetInfo(),
#                                           maximum=self.__job.GetMaxProgress(),
#                                           parent=self,
#                                           style = wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)# | wx.PD_AUTO_HIDE)
            self.SetInitialSize(self.GetEffectiveMinSize())
            self.CenterOnParent()
            self.ShowModal()
        if event.IsDone():
            self.__state = "Finished"
            self.Close()
        if event.IsUpdate():
            if "name" in event.GetFields():
                self.SetTitle(self.__job.GetName())
#            if "info" in event.GetFields():
#                self.stInfo.SetLabel(self.__job.GetInfo())
#            if "progress" in event.GetFields():
#                self.gauge.SetValue(self.__job.GetProgress())
            if "maxProgress" in event.GetFields():
                maximum = self.__job.GetMaxProgress()
                if maximum > 0:
                    self.__maximum = maximum
                    self.gauge.SetRange(maximum)

            self.__Update(self.__job.GetProgress(),
                          self.__job.GetInfo())

