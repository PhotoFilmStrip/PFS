# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#

import logging
import threading

from photofilmstrip.core.ux import Ux
from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.Worker import JobAbortedException
from photofilmstrip.lib.jobimpl.WorkLoad import WorkLoad


class RenderJob(VisualJob, Ux):

    def __init__(self, name, renderer, tasks):
        VisualJob.__init__(self, name, groupId="render")
        Ux.__init__(self)
        self.renderer = renderer
        self.tasks = tasks

        self.SetMaxProgress(len(tasks))

        self.resultsForRendererLock = threading.Lock()
        self.resultForRendererIdx = 0
        self.resultsForRendererCache = {}

        self.taskResultCache = {}
        self.finalizeHandler = self.renderer.GetFinalizeHandler()

        self.__logger = logging.getLogger("RenderJob")

    def GetOutputFile(self):
        return self.renderer.GetOutputFile()

    def Done(self):
        if self.IsAborted():
            self.renderer.ProcessAbort()
        self.renderer.Finalize()

        self.__logger.debug("task cache: %s; result cache: %s",
                           len(self.taskResultCache),
                           len(self.resultsForRendererCache))

    def Begin(self):
        # prepare task queue
        self.__logger.debug("%s: prepare task queue", self.GetName())
        for idx, task in enumerate(self.tasks):
            for subTask in task.IterSubTasks():
                self._RegisterTaskResult(subTask, True)

            self._RegisterTaskResult(task, False)

            prt = RendererResultTask(idx, task)
            self.AddWorkLoad(prt)

        # prepare the renderer, creates the sink pipe
        self.renderer.Prepare()

    def _RegisterTaskResult(self, task, isSubTask):
        if isSubTask:
            # no finalize for subtasks
            finalizeHandler = None
        else:
            finalizeHandler = self.finalizeHandler
        # make sure that a real sub task is not processed from FinalizeHandler
        # so generate a special key for subtasks
        key = "{0}{1}".format(task.GetKey(), isSubTask)
        if key in self.taskResultCache:
            trce = self.taskResultCache[key]
            isNew = False
        else:
            trce = TaskResultCacheEntry(task, self, finalizeHandler)
            self.taskResultCache[key] = trce
            isNew = True

        trce.refCount += 1
        return isNew

    def GetWorkLoad(self):
        task = VisualJob.GetWorkLoad(self)
        self.SetInfo(task.GetInfo())

        self.__logger.debug("%s: %s: %s - start",
                            threading.current_thread().getName(),
                            self.GetName(), task.GetKey())

        return task

    def PushResult(self, resultObject):
        '''
        overrides IJobContext.PushResult
        '''
        task = resultObject.GetSource()
        self.__logger.debug("%s: %s: %s - done",
                            threading.current_thread().getName(),
                            self.GetName(), task.GetKey())

        try:
            result = resultObject.GetResult()
            self.resultsForRendererCache[task.idx] = result
        except JobAbortedException:
            pass
        with self.resultsForRendererLock:
            while self.resultForRendererIdx in self.resultsForRendererCache:
                idx = self.resultForRendererIdx

                self.__logger.debug("%s: %s: resultToFetch: %s",
                                    threading.current_thread().getName(),
                                    self.GetName(), idx)

                imgData = self.resultsForRendererCache[idx]
                if imgData:
                    self.renderer.ToSink(imgData)
                del self.resultsForRendererCache[idx]
                self.resultForRendererIdx += 1

                self.StepProgress()

    def ProcessSubTask(self, task, isSubTask=True):
        key = "{0}{1}".format(task.GetKey(), isSubTask)
        trce = self.taskResultCache[key]
        result = trce.GetResult()
        if trce.refCount == 0:
            self.__logger.debug("%s: %s: clear cached result %s",
                                threading.current_thread().getName(),
                                self.GetName(), key)
            del self.taskResultCache[key]
        else:
            self.__logger.debug("%s: %s: result ref count %s %s",
                                threading.current_thread().getName(),
                                self.GetName(), trce.refCount, key)

        return result


class RendererResultTask(WorkLoad):
    '''
    its more like a dummy task just to assure the correct reference counting
    of task results especially concerning sub tasks.
    '''

    def __init__(self, idx, task):
        WorkLoad.__init__(self)
        self.idx = idx
        self.task = task

    def GetKey(self):
        return self.idx

    def Run(self, jobContext):
        # self.task is not really a sub task, but is processed as a sub task to
        # use the result cache
        return jobContext.ProcessSubTask(self.task, False)

    def GetInfo(self):
        return self.task.GetInfo()


class TaskResultCacheEntry:

    NO_RESULT = object()

    def __init__(self, task, renderJob, finalizeHandler):
        self.task = task
        self.renderJob = renderJob
        self.finalizeHandler = finalizeHandler
        self.refCount = 0
        self.result = TaskResultCacheEntry.NO_RESULT
        self.lock = threading.Lock()

    def SetResult(self, result):
        assert self.result is TaskResultCacheEntry.NO_RESULT
        self.result = result

    def GetResult(self):
        with self.lock:
            if self.result is TaskResultCacheEntry.NO_RESULT:
                self.result = self.task.Run(self.renderJob)
                if self.finalizeHandler and self.result:
                    self.result = self.finalizeHandler.ProcessFinalize(self.result)
            self.refCount -= 1
            return self.result
