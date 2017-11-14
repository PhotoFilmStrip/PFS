# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
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

import logging
import threading

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.Worker import JobAbortedException
from photofilmstrip.lib.jobimpl.WorkLoad import WorkLoad


class RenderJob(VisualJob):

    def __init__(self, name, renderer, tasks):
        VisualJob.__init__(self, name, groupId="render")
        self.renderer = renderer
        self.tasks = tasks

        self.SetMaxProgress(len(tasks))

        self.resultsForRendererLock = threading.Lock()
        self.resultForRendererIdx = 0
        self.resultsForRendererCache = {}

        self.taskResultLock = threading.Lock()
        self.taskResultCache = {}

        self.__logger = logging.getLogger("RenderJob")

    def GetOutputPath(self):
        return self.renderer.GetOutputPath()

    def Done(self):
        if self.IsAborted():
            self.renderer.ProcessAbort()
        self.renderer.Finalize()

    def Begin(self):
        # prepare task queue
        self.__logger.debug("%s: prepare task queue", self.GetName())
        for idx, task in enumerate(self.tasks):
            for subTask in task.IterSubTasks():
                if self._RegisterTaskResult(subTask):
                    self.AddWorkLoad(subTask)

            if self._RegisterTaskResult(task):
                self.AddWorkLoad(task)

            prt = RendererResultTask(idx, task)
            self.AddWorkLoad(prt)

        # prepare the renderer, creates the sink pipe
        self.renderer.Prepare()

    def _RegisterTaskResult(self, task):
        key = task.GetKey()
        if key in self.taskResultCache:
            trce = self.taskResultCache[key]
            isNew = False
        else:
            trce = TaskResultCacheEntry()
            self.taskResultCache[key] = trce
            isNew = True

        trce.refCount += 1
        return isNew

    def GetWorkLoad(self):
        task = VisualJob.GetWorkLoad(self)
        if isinstance(task, RendererResultTask):
            self.SetInfo(task.GetInfo())

        self.__logger.debug("%s: %s - start", self.GetName(), task)

        return task

    def PushResult(self, resultObject):
        '''
        overrides IJobContext.PushResult
        '''
        task = resultObject.GetSource()
        self.__logger.debug("%s: %s - done", self.GetName(), task)

        try:
            result = resultObject.GetResult()
        except JobAbortedException:
            pass

        if isinstance(task, RendererResultTask):
            self._HandleResultForRenderer(task, result)
        else:
            # results of other tasks are cached
            key = task.GetKey()
            trce = self.taskResultCache[key]
            trce.SetResult(result)

    def PullTaskResult(self, key, decRef=False):
        with self.taskResultLock:
            trce = self.taskResultCache[key]
            try:
                return trce.GetResult()
            finally:
                if decRef:
                    trce.refCount -= 1
                    if trce.refCount == 0:
                        del self.taskResultCache[key]

    def _HandleResultForRenderer(self, task, result):
        self.resultsForRendererCache[task.idx] = result
        with self.resultsForRendererLock:
            while self.resultsForRendererCache.has_key(self.resultForRendererIdx):
                idx = self.resultForRendererIdx

                self.__logger.debug("%s: resultToFetch: %s",
                                    self.GetName(), idx)

                pilCtx = self.resultsForRendererCache[idx]
                if pilCtx:
                    self.renderer.ProcessFinalize(pilCtx)
                del self.resultsForRendererCache[idx]
                self.resultForRendererIdx += 1

                self.StepProgress()


class RendererResultTask(WorkLoad):
    '''
    its more like a dummy task just to assure the correct reference counting
    of task results especially concerning sub tasks.
    '''

    def __init__(self, idx, task):
        WorkLoad.__init__(self)
        self.idx = idx
        self.task = task

    def Run(self, jobContext):
        for subTask in self.task.IterSubTasks():
            jobContext.PullTaskResult(subTask.GetKey(), decRef=True)
        return jobContext.PullTaskResult(self.task.GetKey(), decRef=True)

    def GetInfo(self):
        return self.task.GetInfo()


class TaskResultCacheEntry(object):

    NO_RESULT = object()

    def __init__(self):
        self.refCount = 0
        self.result = TaskResultCacheEntry.NO_RESULT
        self.evt = threading.Event()

    def SetResult(self, result):
        assert self.result is TaskResultCacheEntry.NO_RESULT
        self.result = result
        self.evt.set()

    def GetResult(self):
        if self.result is TaskResultCacheEntry.NO_RESULT:
            self.evt.wait()
        return self.result
