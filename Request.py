from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: #only for typechecking
    from Server import Server 

from Environment import Environment
from Event import Event

class Request:

    def __init__(self, type, processingTime, timeRequirement, environment: Environment):
        '''
        type: type of the request
        processingTime: the processing time of the request, sampled from Gaussian distribution
        '''
        self.type, self.processingTime = type, processingTime
        self.timeRequirement = timeRequirement
        self.environment = environment
        self.isWaiting = False
        self.isBeingProcessed = False
        self.isProcessed = False
        self.isCancelled = False

        self.waitingStartTime = None
        self.processingStartTime = None

        self.waitingTime = 0
        self.totalTimeInSystem = 0

        self.assignedServer = None

        self.startWaiting() #request starts waiting when created

    def assignToServer(self, server: Server):
        self.assignedServer = server

    def cancelRequest(self):
        if self.isProcessed or self.isCancelled:
            return #if processed the request cannot be cancelled anymore
        if self.isBeingProcessed:
            self.assignedServer.currentRequestFinished()
        else:
            self.isCancelled = True
        self.environment.logData("requestCancelled")
        
    def startWaiting(self):
        '''
        start waiting when the request is pushed into a queue
        '''
        self.waitingStartTime = self.environment.currentTime
        self.isWaiting = True
        requestCancelTime = self.environment.currentTime + self.timeRequirement
        requestCancelledEvent = Event(requestCancelTime, self.cancelRequest, "cancelRequest")
        self.environment.scheduleEvent(requestCancelledEvent)
    
    def endWaiting(self):
        '''
        end waiting when the request is popped out of a queue
        '''
        self.waitingTime = self.environment.currentTime - self.waitingStartTime
        self.environment.logData("requestWaitingTime", self.waitingTime)
    
    def startProcessing(self):
        '''
        start being processed 
        '''
        self.endWaiting()
        self.isBeingProcessed = True
        requestProcessingEndTime = self.environment.currentTime + self.processingTime
        self.environment.scheduleEvent(Event(requestProcessingEndTime, self.finishProcessing, 'requestFinishProcessing'))

    def finishProcessing(self):
        self.assignedServer.currentRequestFinished()
        self.isBeingProcessed = False
        self.isProcessed = True
        self.totalTimeInSystem = self.environment.currentTime - self.waitingStartTime
        self.environment.logData("requestProcessed")
        self.environment.logData("totalTimeInSystem", self.totalTimeInSystem)
        
