# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import logging
import os
import re
import threading
import time

from gi.repository import Gst, GES
from gi.repository import GstPbutils

from photofilmstrip.core.geom import Rect
from photofilmstrip.core.Media import MediaOrientation
from photofilmstrip.core.GtkMainLoop import GtkMainLoop


class StoryEngine(object):

    TRANSITION_DURATION = None  # Gst.SECOND * 1

    def _Log(self, lvl, msg, *args):
        logging.log(lvl, msg, *args)

    def __init__(self, medias, outFile, profile, gstElements):
        self.medias = medias
        self.outFile = outFile
        self.profile = profile
        self.gstElements = gstElements
        self.isPreview = self.outFile is None

        self.job = None

        self.pipeline = None
        self.project = None
        self.timeline = None
        self.layer_video = None
        self.layer_vertical_effect = None
        self.layer_audio = None

        self.posPoller = None
        self.readyEvent = None

        self.assets_added_ctr = 0
        self.outResolution = Rect(*profile.GetResolution())
        self.assets = {}

    def Execute(self, job):
        self.job = job

        self.readyEvent = threading.Event()

        # disable vaapi plugin
        reg = Gst.Registry.get()
        vaapi_ele = Gst.Registry.lookup_feature(reg, "vaapidecodebin")
        if vaapi_ele:
            vaapi_rank = vaapi_ele.get_rank()
            vaapi_ele.set_rank(255)

        GtkMainLoop.EnsureRunning()

        self.job.SetInfo(_("Prepare rendering..."))

        self._CreateGesElements()
        self._LoadAssets()
        self._MakeTimeline()
        if self.isPreview:
            self.pipeline.set_mode(GES.PipelineFlags.FULL_PREVIEW)
        else:
            self._SetupRendering()
            self._SaveGesProject(os.path.splitext(self.outFile)[0] + ".xges")

            self.pipeline.set_mode(GES.PipelineFlags.RENDER)

        self.job.SetInfo(_("Rendering in progress..."))

        self.posPoller = PositionPoller(
            self.job, self.pipeline, self.timeline.get_duration())
        self.posPoller.start()

        self.pipeline.set_state(Gst.State.PLAYING)

        self.readyEvent.wait()

        if vaapi_ele:
            vaapi_ele.set_rank(vaapi_rank)
        self.posPoller.Stop()

    def _CreateGesElements(self):
        self.timeline = GES.Timeline.new()
        self.timeline.add_track(GES.VideoTrack.new())
        self.timeline.add_track(GES.AudioTrack.new())
        self.timeline.set_auto_transition(0)

        self._GesUpdateRestrictionCaps()

        self.pipeline = GES.Pipeline()
        self.pipeline.set_timeline(self.timeline)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        # Workaound: connecting to all messages results in "Python int too large to convert to C long" ???
        bus.connect("message::error", self._GstOnMessage)
        bus.connect("message::eos", self._GstOnMessage)
        bus.connect("message::state-changed", self._GstOnMessage)
        bus.connect("message::warning", self._GstOnMessage)

        self.layer_video = GES.Layer()
        self.layer_vertical_effect = GES.Layer()
        self.layer_vertical_effect.set_priority(1)
        self.layer_audio = GES.Layer()
        self.layer_audio.set_priority(2)
        self.timeline.add_layer(self.layer_video)
        self.timeline.add_layer(self.layer_vertical_effect)
        self.timeline.add_layer(self.layer_audio)

        self.project = self.timeline.get_asset()
        self.project.connect("asset-added", self._GesOnAssetAdded)
        self.project.connect("error-loading-asset", self._GesOnErrorLoadingAsset)

    def _SetupRendering(self):
        profile = self._GesMakeEncodingProfile()
        self.project.add_encoding_profile(profile)
        for sprof in profile.get_profiles():
            if isinstance(sprof, GstPbutils.EncodingVideoProfile):
                sprof.set_restriction(self.videocaps)

            if isinstance(sprof, GstPbutils.EncodingAudioProfile):
                sprof.set_restriction(self.audiocaps)

        outfile = Gst.filename_to_uri(self.outFile)
        self.pipeline.set_render_settings(outfile, profile)
        self.pipeline.set_state(Gst.State.NULL)

    def _GesUpdateRestrictionCaps(self):
        # Get the height/width without rendering settings applied
        width, height = self.outResolution
        videorate = Gst.Fraction(self.profile.GetFrameRate().AsFloat())
        videocaps = Gst.Caps.new_empty_simple("video/x-raw")

        videocaps.set_value("width", width)
        videocaps.set_value("height", height)
        videocaps.set_value("framerate", videorate)
        videocaps.set_value("pixel-aspect-ratio", Gst.Fraction(1, 1))
        self.videocaps = videocaps

        audiocaps = Gst.Caps.new_empty_simple("audio/x-raw")
        audiocaps.set_value("rate", 44100)
        audiocaps.set_value("channels", 2)
        self.audiocaps = audiocaps

        for track in self.timeline.get_tracks():
            if isinstance(track, GES.VideoTrack):
                track.set_restriction_caps(videocaps)

            elif isinstance(track, GES.AudioTrack):
                track.set_restriction_caps(audiocaps)

    def _GesGetSrcCaps(self, profile, full=False):
        factories = Gst.ElementFactory.find(profile)
        if not factories:
            self._Log(
                logging.ERROR,
                "Could not find any element with name %s",
                profile)
            return

        for pad_template in factories.get_static_pad_templates():
            if pad_template.direction == Gst.PadDirection.SRC:
                caps = Gst.caps_from_string(pad_template.get_caps().to_string())
                return caps
#                 else:
#                     return caps.split(",")[0]
        return None

    def _GesMakeEncodingProfile(self):
        caps = self._GesGetSrcCaps(self.gstElements[0])
        profile = GstPbutils.EncodingContainerProfile.new(
            "photofilmstrip", None, caps, None)
        profile.set_preset_name(self.gstElements[0])

        caps = self._GesGetSrcCaps(self.gstElements[1])
        stream = GstPbutils.EncodingVideoProfile.new(
            caps, None, Gst.Caps("video/x-raw"), 0)
        stream.set_enabled(1)
        stream.set_preset_name(self.gstElements[1])
        profile.add_profile(stream)

        caps = self._GesGetSrcCaps(self.gstElements[2])
        stream = GstPbutils.EncodingAudioProfile.new(
            caps, None, Gst.Caps("audio/x-raw,rate=44100,channels=2"), 0)
        stream.set_enabled(1)
        stream.set_preset_name(self.gstElements[2])
        profile.add_profile(stream)

        return profile

    def _SaveGesProject(self, outfile):
        outfile = Gst.filename_to_uri(outfile)
        self.project.save(self.timeline, outfile, None, True)

    def _GesOnAssetAdded(self, project, asset):  # pylint: disable=unused-argument
        self._Log(logging.DEBUG, "Asset added: %s %s %s",
                  asset, asset.get_id(), asset.get_extractable_type())
        self.assets_added_ctr += 1

    def _GetClipInfo(self, discovererInfo):
        clipInfo = ClipInfo()
        videoInfos = discovererInfo.get_video_streams()
        audioInfos = discovererInfo.get_audio_streams()
        clipInfo.hasAudio = len(audioInfos) > 0
        orientation = None
        for streamInfo in videoInfos:
            clipInfo.width = streamInfo.get_width()
            clipInfo.height = streamInfo.get_height()

            tags = streamInfo.get_tags()
            success, orientation = tags.get_string(Gst.TAG_IMAGE_ORIENTATION)
            if success:
                break
        if orientation:
            self._Log(logging.DEBUG, "Orientation %s ", orientation)
            nums = re.findall(r".+-(\d+)", orientation)
            if nums:
                angle = nums[0]
                clipInfo.isVertical = bool(int(angle) // 90 % 2)

        return clipInfo

    def _LoadAssets(self):
        assets_ctr = 0
        for media in self.medias:
            paths = [media.GetFilename()]
            for subMedia in media.GetChildren():
                paths.append(subMedia.GetFilename())

            for path in paths:
                if path:
                    assets_ctr += 1

                    uri = Gst.filename_to_uri(path)
                    ai = AssetInfo(uri)
                    self.assets[path] = ai
                    result = self.project.create_asset(uri, GES.UriClip)
                    if not result:
                        # already added
                        self.assets_added_ctr += 1

        self._Log(logging.DEBUG, "wait for all assets to be loaded")
        while self.assets_added_ctr < assets_ctr:
            self._Log(logging.DEBUG, "assets loaded: %s", self.assets_added_ctr)
            time.sleep(0.1)

    def _GetVideoAndAudioFiles(self, media):
        videos = []
        audios = []
        if media.IsVideo():
            videos.append((media.GetFilename(), media.GetProperty("orientation")))
        else:
            audios.append(media.GetFilename())
        for subMedia in media.GetChildren():
            assert subMedia.IsVideo() != media.IsVideo()
            if subMedia.IsVideo():
                videos.append((subMedia.GetFilename(), subMedia.GetProperty("orientation")))
            else:
                audios.append(subMedia.GetFilename())
        return videos, audios

    def _MakeTimeline(self):
        for media in self.medias:
            startTime = self.timeline.get_duration()

            videos, audios = self._GetVideoAndAudioFiles(media)

            videoDuration = 0
            videoHasAudio = False
            videoStartTime = startTime

            for videoFile, videoOrientation in videos:
                assetInfo = self.assets[videoFile]

                asset = self.project.get_asset(assetInfo.uri, GES.UriClip)
                discovererInfo = asset.get_info()
                clipInfo = self._GetClipInfo(discovererInfo)
                self._Log(logging.INFO, "%s: %s", media.GetFilename(), clipInfo)
                clipSize = Rect(clipInfo.width, clipInfo.height)

                assetDuration = asset.get_duration()

                clipTrans = None
                if self.TRANSITION_DURATION and \
                        videoStartTime > self.TRANSITION_DURATION:
                    videoStartTime -= self.TRANSITION_DURATION
                    clipTrans = GES.TransitionClip.new(
                        GES.VideoStandardTransitionType.CROSSFADE)
                    clipTrans.set_start(videoStartTime)
                    clipTrans.set_duration(self.TRANSITION_DURATION)
                    self.layer_video.add_clip(clipTrans)

                clip = self.layer_video.add_asset(
                    asset, videoStartTime,
                    0, assetDuration,
                    asset.get_supported_formats())

                videoDirection = None
                if videoOrientation != MediaOrientation.AS_IS:
                    if videoOrientation == MediaOrientation.AUTO_DETECT:
                        if clipInfo.isVertical:
                            clipSize = clipSize.Invert()
                            videoDirection = 8

                    if videoOrientation == MediaOrientation.ROTATE_LEFT:
                        clipSize = clipSize.Invert()
                        videoDirection = 3
                    if videoOrientation == MediaOrientation.ROTATE_RIGHT:
                        clipSize = clipSize.Invert()
                        videoDirection = 1
                    if videoOrientation == MediaOrientation.UPSIDE_DOWN:
                        videoDirection = 2

                if videoDirection is not None:
                    effect = GES.Effect.new("videoflip")
                    effect.set_child_property("video-direction", videoDirection)
                    clip.add(effect)

                    self._MakeVerticalClipEffect(
                        asset, videoStartTime, assetDuration, clipSize,
                        videoDirection)

                if clipInfo.hasAudio:
                    videoHasAudio = True

                clipSize = clipSize.FitInside(self.outResolution)

                video_source = clip.find_track_element(None, GES.VideoSource)
                video_source.set_child_property("width", clipSize.width)
                video_source.set_child_property("height", clipSize.height)

                video_source.set_child_property(
                    "posx", clipSize.AlignCenter(self.outResolution).x)
                video_source.set_child_property(
                    "posy", clipSize.AlignCenter(self.outResolution).y)

                videoDuration += assetDuration
                videoStartTime += assetDuration

            audioDuration = 0
            audioStartTime = startTime
            for idxAudio, audioFile in enumerate(audios):
                assetAudioInfo = self.assets[audioFile]

                assetAudio = self.project.get_asset(
                    assetAudioInfo.uri, GES.UriClip)
                assetAudioDuration = assetAudio.get_duration()
                if audioDuration + assetAudioDuration > videoDuration:
                    assetAudioDuration = videoDuration - audioDuration

                audioDuration += assetAudioDuration

                clipAudio = self.layer_audio.add_asset(
                    assetAudio, audioStartTime,
                    0, assetAudioDuration,
                    assetAudio.get_supported_formats())
                if videoHasAudio:
                    clipAudio.set_child_property("volume", 0.5)

                if audioDuration >= videoDuration:
                    if idxAudio < len(audios) - 1:
                        self._Log(logging.WARNING, "not all audio files processed")
                    break

                audioStartTime += assetAudioDuration

        self.timeline.commit()

    def _MakeVerticalClipEffect(self, asset, startTime, duration, clipSize,
                                videoDirection):
        clip_vert = self.layer_vertical_effect.add_asset(
            asset, startTime,
            0, duration, asset.get_supported_formats())

        effect = GES.Effect.new("videoflip")
        effect.set_child_property("video-direction", videoDirection)
        clip_vert.add(effect)

        if not self.isPreview:
            # to slow for real time
            effect = GES.Effect.new("gaussianblur")
            effect.set_child_property("sigma", 4.0)
            clip_vert.add(effect)

        clip_scale = clipSize.ApplyWidth(self.outResolution)

        clip_vert_video_source = clip_vert.find_track_element(
            None, GES.VideoSource)

        clip_vert_video_source.set_child_property("width", clip_scale.width)
        clip_vert_video_source.set_child_property("height", clip_scale.height)

        clip_vert_video_source.set_child_property(
            "posx", clip_scale.AlignCenter(self.outResolution).x)
        clip_vert_video_source.set_child_property(
            "posy", clip_scale.AlignCenter(self.outResolution).y)

        clip_vert_audio_source = clip_vert.find_track_element(None, GES.AudioSource)
        clip_vert_audio_source.set_child_property("mute", True)

    def _GesOnErrorLoadingAsset(self, project, error, asset_id, typ):  # pylint: disable=unused-argument
        self._Log(logging.ERROR, "Could not load asset %s: %s", asset_id, error)
        self.readyEvent.set()

    def _GstOnMessage(self, bus, msg):  # pylint: disable=unused-argument
        '''
        Gstreamer message handler for messages in gstreamer event bus.
        :param bus:
        :param msg:
        '''
        self._Log(logging.DEBUG, '_GstOnMessage: %s', msg.type)

        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            self._Log(logging.ERROR, "Error received from element %s: %s",
                          msg.src.get_name(), err)
            self._Log(logging.DEBUG, "Debugging information: %s", debug)
            self.readyEvent.set()

        elif msg.type == Gst.MessageType.EOS:
            self.readyEvent.set()

        elif msg.type == Gst.MessageType.STATE_CHANGED:
            if msg.src == self.pipeline:
                prev, new, pending = msg.parse_state_changed()
                self._Log(logging.DEBUG, '_GstOnMessage: %s %s %s', prev, new, pending)
                if prev == Gst.State.PAUSED and new == Gst.State.PLAYING:
                    self.posPoller.Enable()
                elif prev == Gst.State.PLAYING and new == Gst.State.PAUSED:
                    self.posPoller.Enable(False)
                    self.readyEvent.set()
        elif msg.type == Gst.MessageType.WARNING:
            warn = msg.parse_warning()
            self._Log(logging.WARNING, '_GstOnMessage: %s %s', msg.src.get_name(), warn)

        return Gst.BusSyncReply.PASS


class PositionPoller(threading.Thread):

    def __init__(self, job, pipeline, duration):
        threading.Thread.__init__(self, name="PositionPoller")
        self._job = job
        self._pipeline = pipeline
        self._active = True
        self._enabled = False
        self._duration = duration

    def run(self):
        while self._active:
            if self._job.IsAborted():
                logging.getLogger("PositionPoller").log(logging.DEBUG, "Job is aborted")
                self._pipeline.set_state(Gst.State.PAUSED)
            if self._enabled:
                try:
                    res, cur = self._pipeline.query_position(Gst.Format.TIME)
                    logging.getLogger("PositionPoller").log(logging.DEBUG, "query_position returned %s %s", res, cur)
                except Exception:  # pylint: disable=broad-except
                    res = False

                if res:
                    fraction = min(cur, self._duration) / self._duration * 100
                    self._job.SetProgress(round(fraction))

            time.sleep(0.5)

        self._job.SetProgress(100)

    def Enable(self, value=True):
        self._enabled = value

    def Stop(self):
        self._active = False


class AssetInfo:

    def __init__(self, uri):
        self.uri = uri
        self.id = None


class ClipInfo:

    def __init__(self):
        self.width = None
        self.height = None
        self.isVertical = None
        self.hasAudio = None

    def __str__(self):
        return "ClipInfo(width={}, height={}, isVertical={}, hasAudio={}".format(
            self.width, self.height, self.isVertical, self.hasAudio)
