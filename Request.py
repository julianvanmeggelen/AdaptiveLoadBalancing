from Environment import Environment

class Request:
    def __init__(self, type, processingTime, timeRequirement, environment):
        '''
        type: type of the request
        processingTime: the processing time of the request, sampled from Gaussian distribution
        '''
        self.type, self.processingTime = type, processingTime
        self.timeRequirement = timeRequirement
        self.environment = Environment
        self.isProcessed = 0
        self.isCancelled = 0
        self.waitingStartTime = None
        self.startTime = None
        self.waitingTime = 0
    
    def startWaiting(self, time):
        '''
        start waiting when the request is pushed into a queue
        '''
        self.waitingStartTime = time
    
    def endWaiting(self, time):
        '''
        end waiting when the request is popped out of a queue
        '''
        self.waitingTime = time - self.waitingStartTime
    
    def startProcessing(self, time):
        '''
        start being processed after the request ends waiting
        '''
        if (self.waitingTime>self.timeRequirement):
            self.isCancelled = 1
        else:
            self.startTime = time
            if (self.startTime+self.processingTime<self.environment.stopTime):
                self.isProcessed = 1
