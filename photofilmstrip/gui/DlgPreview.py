# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import os
import subprocess
import tempfile
import wx

from photofilmstrip.core.RenderEngine import RenderEngineSlideshow
from photofilmstrip.core.OutputProfile import GetOutputProfiles
from photofilmstrip.core.renderer.SingleFileRenderer import SingleFileRenderer
from photofilmstrip.core.Renderers import RENDERERS
from photofilmstrip.core.RenderJob import RenderJob
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.Settings import Settings


class DlgPreview(wx.Dialog):
    """
    Preview dialog that shows briefly while generating, then opens external player.
    This dialog is shown minimally and closes the job queue when done.
    """

    def __init__(self, parent, project, aspect, selectedPics=None):
        # Create a minimal visible dialog that can receive Alt+Q
        # Size it small but visible at the bottom
        screen_size = wx.GetDisplaySize()
        dialog_width = 200
        dialog_height = 30
        
        wx.Dialog.__init__(
            self, 
            parent=parent,
            id=wx.ID_ANY,
            title=_("Preview - Press Alt+Q to stop"),
            pos=wx.Point(screen_size.width - dialog_width - 10, screen_size.height - dialog_height - 10),
            size=wx.Size(dialog_width, dialog_height),
            style=wx.FRAME_TOOL_WINDOW | wx.STAY_ON_TOP | wx.CAPTION
        )
        
        self.parent = parent
        self.project = project
        self.aspect = aspect
        self.selectedPics = selectedPics or project.GetPictures()
        self.tempDir = tempfile.mkdtemp(prefix="pfs_preview_")
        self.tempFile = None
        self.renderJob = None
        self.checkTimer = None
        self.externalPlayerProcess = None
        
        # Create a simple panel with a label
        panel = wx.Panel(self, wx.ID_ANY)
        self.statusLabel = wx.StaticText(panel, wx.ID_ANY, _("Generating preview... Press Alt+Q to stop"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.statusLabel, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(sizer)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(panel, 1, wx.EXPAND)
        
        # Bind Alt+Q to close the preview
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        # Start preview generation
        self.StartPreviewGeneration()
        
        # Hide the dialog - we don't want to see it
        # But keep it alive to monitor the job and handle Alt+Q
        self.Hide()

    def StartPreviewGeneration(self):
        """Start generating the preview in background."""
        try:
            pics = self.selectedPics
            if not pics:
                self.Close()
                return

            # Get a video renderer (skip SingleFileRenderer)
            videoRenderers = [r for r in RENDERERS if r != SingleFileRenderer]
            if not videoRenderers:
                self.Close()
                return

            # Prefer MkvX264AC3 or Mp4X264AAC for better quality (no pink box)
            from photofilmstrip.core.renderer.GStreamerRenderer import MkvX264AC3, Mp4X264AAC, OggTheoraVorbis
            preferred_renderers = [MkvX264AC3, Mp4X264AAC, OggTheoraVorbis]
            for pref in preferred_renderers:
                if pref in videoRenderers:
                    rendererClass = pref
                    wx.LogDebug("Using preferred renderer: %s" % pref.__name__)
                    break
            else:
                # Fallback to first available
                rendererClass = videoRenderers[0]
                wx.LogDebug("Using fallback renderer: %s" % rendererClass.__name__)

            # Use default renderer properties (don't load from settings to avoid issues)
            renderer = rendererClass()

            # Get a simple, working profile
            from photofilmstrip.core.OutputProfile import GetMPEGProfiles, GetOutputProfiles, OutputProfile
            
            # For MkvX264AC3 and Mp4X264AAC, we need non-MPEG profiles
            from photofilmstrip.core.renderer.GStreamerRenderer import MkvX264AC3, Mp4X264AAC
            use_non_mpeg = rendererClass in (MkvX264AC3, Mp4X264AAC)
            
            if use_non_mpeg:
                # Get non-MPEG profiles (regular output profiles)
                profiles = GetOutputProfiles(self.aspect)
                # Filter out MPEG profiles
                profiles = [p for p in profiles if not p.IsMPEGProfile()]
            else:
                # For other renderers, try MPEG profiles first
                profiles = GetMPEGProfiles()
                if not profiles:
                    profiles = GetOutputProfiles(self.aspect)
            
            if not profiles:
                # Create a simple OutputProfile if none available
                from photofilmstrip.core.FrameRate import FrameRate
                profile = OutputProfile(
                    "Preview",
                    (800, 600),  # Standard resolution
                    FrameRate(25, "25.00 fps"),
                    5000  # Bitrate
                )
                wx.LogDebug("Using default profile: 800x600, 25fps")
            else:
                profile = profiles[0]
                wx.LogDebug("Using profile: %s (MPEG=%s)" % (profile.GetName(), profile.IsMPEGProfile()))

            # Use actual durations from pictures (no limit)
            totalLength = None

            # Initialize renderer with output file
            outputBase = os.path.join(self.tempDir, "preview")
            renderer.Init(profile, self.aspect, outputBase)

            # Don't set audio files for preview (simplifies things)
            # audioFiles = self.project.GetAudioFiles()
            # if audioFiles:
            #     renderer.SetAudioFiles(audioFiles)

            # Create render engine with draft mode
            # Disable loop in the engine since we want the player to handle it
            engine = RenderEngineSlideshow(
                profile, pics, 
                draftMode=True,
                totalLength=totalLength,
                loop=False  # Player handles looping, not the engine
            )

            # Get tasks from engine
            tasks = engine.GetTasks()

            # Create render job
            self.renderJob = RenderJob("Preview", renderer, tasks)

            # Enqueue the job - this will show in job queue
            JobManager().EnqueueContext(self.renderJob)

            # Start a timer to check for completion
            self.checkTimer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.OnCheckJob, self.checkTimer)
            self.checkTimer.Start(500)  # Check every 500ms

        except Exception as e:
            import traceback
            wx.LogError("Error starting preview: %s\n%s" % (str(e), traceback.format_exc()))
            self.Close()

    def OnCheckJob(self, event):
        """Check if the render job is done."""
        if self.renderJob and self.renderJob.IsDone():
            self.checkTimer.Stop()
            self.OnJobCompleted()

    def OnJobCompleted(self):
        """Called when the render job completes."""
        try:
            # Find the generated file
            if os.path.exists(self.tempDir):
                files = os.listdir(self.tempDir)
                
                # Look for common video file extensions
                videoExtensions = ['.mkv', '.mp4', '.avi', '.mov', '.webm', '.mpeg', '.mpg']
                previewFile = None
                for ext in videoExtensions:
                    testFile = os.path.join(self.tempDir, "preview" + ext)
                    if os.path.exists(testFile):
                        previewFile = testFile
                        break
                
                # Also check if there's exactly one file
                if not previewFile and len(files) == 1:
                    previewFile = os.path.join(self.tempDir, files[0])
                
                if previewFile:
                    self.tempFile = previewFile
                    self.OpenPreview(previewFile)
                else:
                    wx.LogError("No preview file found in %s. Files: %s" % (self.tempDir, files))
            else:
                wx.LogError("Temp dir doesn't exist: %s" % self.tempDir)
            
            # Give JobManager a moment to remove the job from visuals
            import time
            time.sleep(0.5)
            
            # Try to close the job queue frame
            self._CloseJobQueueFrame()
            
            # Close this dialog and cleanup
            self.Close()
        except Exception as e:
            import traceback
            wx.LogError("Error in OnJobCompleted: %s\n%s" % (str(e), traceback.format_exc()))
            self.Close()
    
    def _CloseJobQueueFrame(self):
        """Try to close the job queue frame."""
        try:
            # Get the main frame
            main_frame = self.parent
            while main_frame and not isinstance(main_frame, wx.Frame):
                main_frame = main_frame.GetParent()
            
            if main_frame and hasattr(main_frame, 'frmJobManager'):
                # Close the job queue frame
                if main_frame.frmJobManager:
                    main_frame.frmJobManager.Close()
        except Exception as e:
            wx.LogError("Error closing job queue frame: %s" % str(e))

    def OnKeyDown(self, event):
        """Handle Alt+Q to close preview."""
        key_code = event.GetKeyCode()
        alt_down = event.AltDown()
        
        # Log all key presses for debugging
        if key_code < 128:  # Printable ASCII
            key_char = chr(key_code)
            wx.LogDebug("Key pressed in DlgPreview: %s (code=%d, alt=%s)" % (key_char, key_code, alt_down))
        
        if key_code == ord('Q') and alt_down:
            # Alt+Q pressed - kill the external player
            wx.LogDebug("Alt+Q detected! Killing player...")
            self._KillExternalPlayer()
            self.Close()
        event.Skip()
    
    def _KillExternalPlayer(self):
        """Kill the external player process if running."""
        if self.externalPlayerProcess:
            wx.LogDebug("Attempting to kill external player with PID %d" % self.externalPlayerProcess.pid)
            try:
                if wx.Platform == "__WXGTK__":
                    # On Linux, try to kill the process group first
                    import signal
                    import os
                    try:
                        # Send SIGTERM to the process group
                        os.killpg(os.getpgid(self.externalPlayerProcess.pid), signal.SIGTERM)
                        wx.LogDebug("Sent SIGTERM to process group")
                    except (ProcessLookupError, PermissionError, OSError) as e:
                        wx.LogDebug("Failed to send SIGTERM to group: %s" % str(e))
                        # Process group doesn't exist or we can't access it
                        # Try killing just the process
                        self.externalPlayerProcess.terminate()
                        wx.LogDebug("Sent SIGTERM to process")
                    
                    # Give it a moment, then force kill if needed
                    import time
                    time.sleep(0.5)
                    if self.externalPlayerProcess.poll() is None:
                        # Still running, try SIGKILL
                        wx.LogDebug("Process still running, sending SIGKILL")
                        try:
                            os.killpg(os.getpgid(self.externalPlayerProcess.pid), signal.SIGKILL)
                        except (ProcessLookupError, PermissionError, OSError) as e:
                            wx.LogDebug("Failed to send SIGKILL to group: %s" % str(e))
                            self.externalPlayerProcess.kill()
                            wx.LogDebug("Sent SIGKILL to process")
                else:
                    # On other platforms, try terminate then kill
                    self.externalPlayerProcess.terminate()
                    wx.LogDebug("Sent terminate to process")
                    import time
                    time.sleep(0.5)
                    if self.externalPlayerProcess.poll() is None:
                        self.externalPlayerProcess.kill()
                        wx.LogDebug("Sent kill to process")
                
                # Check if process is gone
                if self.externalPlayerProcess.poll() is not None:
                    wx.LogDebug("External player killed successfully")
                else:
                    wx.LogDebug("WARNING: External player may still be running")
            except Exception as e:
                wx.LogDebug("Error killing external player: %s" % str(e))
            finally:
                self.externalPlayerProcess = None
        else:
            wx.LogDebug("No external player process to kill")

    def OpenPreview(self, previewFile):
        """Open the preview file in an external player with looping."""
        import shutil
        
        # For Linux, check common player locations - prioritize mplayer
        player_paths = {
            "mplayer": [
                shutil.which("mplayer"),
                "/usr/bin/mplayer",
                "/usr/local/bin/mplayer",
                "/bin/mplayer"
            ],
            "mpv": [
                shutil.which("mpv"),
                "/usr/bin/mpv",
                "/usr/local/bin/mpv",
                "/bin/mpv"
            ],
            "vlc": [
                shutil.which("vlc"),
                "/usr/bin/vlc",
                "/usr/local/bin/vlc",
                "/bin/vlc"
            ]
        }
        
        # Try mplayer first with loop option
        for path in player_paths["mplayer"]:
            if path and os.path.exists(path):
                cmd = [path, "-loop", "0", previewFile]
                try:
                    self.externalPlayerProcess = subprocess.Popen(
                        cmd,
                        preexec_fn=os.setsid if wx.Platform == "__WXGTK__" else None,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    wx.LogDebug("Opened with mplayer -loop 0")
                    wx.CallAfter(self.statusLabel.SetLabel, _("Playing preview (looping)... Press Alt+Q to stop"))
                    return
                except Exception as e:
                    wx.LogDebug("mplayer failed: %s" % str(e))
        
        # Try mpv
        for path in player_paths["mpv"]:
            if path and os.path.exists(path):
                for loop_flag in ["--loop-file=inf", "--loop=inf", "--loop-playlist=inf", "--loop"]:
                    cmd = [path, loop_flag, previewFile]
                    try:
                        self.externalPlayerProcess = subprocess.Popen(
                            cmd,
                            preexec_fn=os.setsid if wx.Platform == "__WXGTK__" else None,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        wx.LogDebug("Opened with mpv: %s" % loop_flag)
                        wx.CallAfter(self.statusLabel.SetLabel, _("Playing preview (looping)... Press Alt+Q to stop"))
                        return
                    except Exception as e:
                        wx.LogDebug("mpv failed: %s" % str(e))
        
        # Try vlc
        for path in player_paths["vlc"]:
            if path and os.path.exists(path):
                cmd = [path, "--loop", previewFile]
                try:
                    self.externalPlayerProcess = subprocess.Popen(
                        cmd,
                        preexec_fn=os.setsid if wx.Platform == "__WXGTK__" else None,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    wx.LogDebug("Opened with vlc --loop")
                    wx.CallAfter(self.statusLabel.SetLabel, _("Playing preview (looping)... Press Alt+Q to stop"))
                    return
                except Exception as e:
                    wx.LogDebug("vlc failed: %s" % str(e))
        
        # Fallback to xdg-open or default
        wx.LogDebug("No looping player found, using default")
        try:
            if wx.Platform == "__WXGTK__":
                self.externalPlayerProcess = subprocess.Popen(
                    ["xdg-open", previewFile],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                wx.LogDebug("Opened with xdg-open (no loop support)")
            elif wx.Platform == "__WXMAC__":
                self.externalPlayerProcess = subprocess.Popen(
                    ["open", previewFile],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                wx.LogDebug("Opened with open (no loop support)")
            else:
                os.startfile(previewFile)
                wx.LogDebug("Opened with startfile (no loop support)")
                self.externalPlayerProcess = None
            
            # Update status label
            wx.CallAfter(self.statusLabel.SetLabel, _("Playing preview... Press Alt+Q to stop"))
        except Exception as e:
            wx.LogError("Failed to open preview: %s" % str(e))
    


    def OnCmdCloseButton(self, event):
        """Handle close button."""
        # Try to close external player if it's still running
        self._KillExternalPlayer()
        
        # Clean up
        if self.renderJob:
            self.renderJob.Abort()
        
        # Clean up temporary directory
        if self.tempDir and os.path.exists(self.tempDir):
            try:
                import shutil
                shutil.rmtree(self.tempDir, ignore_errors=True)
            except Exception as e:
                wx.LogError("Error cleaning up: %s" % str(e))
        
        if event is not None:
            self.EndModal(wx.ID_OK)
        if self.checkTimer:
            self.checkTimer.Stop()
        self.Destroy()

    def __del__(self):
        # Don't call OnCmdCloseButton here as the wx object may already be deleted
        # Cleanup is handled by OnCmdCloseButton when the dialog is closed properly
        pass
