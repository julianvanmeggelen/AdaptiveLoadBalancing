from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: #only for typechecking
    from LoadBalancer import LoadBalancer 

from Environment import Environment
from Event import Event 
from Request import Request
import random
        
import numpy as np

DEFAULT_REQUEST_PROB = 0.5

class TestLoadBalancer:
    def __init__(self):
        return

    def handleRequestArrival(self, req):
        return

class EventClock:
    def __init__(self, interval, method, environment):
        """
        Execute a method every 'interval' time units
        """
        self.interval = interval
        self.method = method
        self.environment = environment
        self._scheduleNext() #initialize
    
    def _onEventCall(self):
        self.method()
        self._scheduleNext()  
    
    def _scheduleNext(self):
        nextTime = self.environment.currentTime + self.interval
        nextEvent = Event(nextTime, self._onEventCall, "EventClock")
        self.environment.scheduleEvent(nextEvent)   

    
class Source():
    def __init__(self, arrivalsPerSecond: float, requestTypes, loadBalancer: LoadBalancer, environment: Environment, requestProb = DEFAULT_REQUEST_PROB): #requestTypes: list[tuple]
        """
        Parameters
        ----------
        arrivalsPerSecond: float:
            number of arrivals per second (on average)
        requestTypes: list[tuple]
            A list containing info on the request types, structured like [(typeProb, typeMean, typeStd, timeLimit),...]
            where typeProb is the probability of the type arriving and typeMean and typeVar are the
            parameters used when sampling from the Normal distribution.
        loadBalancer: LoadBalancer
            The LoadBalancer instance that this source is connected to.
        environment: Environment
            The Environment instance that this source is connected to.
        """
        self.requestProb = requestProb
        assert self.requestProb <= 1.0, "Requestprob > 1"
        self.requestTypes = requestTypes
        self.loadBalancer = loadBalancer
        self.environment = environment
        self.samplingInterval = self.requestProb/arrivalsPerSecond
        self.clock = EventClock(interval = self.samplingInterval, method=self._onSampleEvent, environment=environment)
        self.setArrivalsPerSecond(arrivalsPerSecond=arrivalsPerSecond)
        self.requestTypeProbs = [requestType[0] for requestType in self.requestTypes]
        self.requestTypeIndices = list(range(0,len(self.requestTypes)))
        self.requestId = 0
        assert sum([requestType[0] for requestType in self.requestTypes]) == 1.0, "typeProbs of provides requestTypes must sum to 1"

    def _getReqId(self):
        self.requestId +=1
        return self.requestId

    def setArrivalsPerSecond(self, arrivalsPerSecond):
        self.arrivalsPerSecond = arrivalsPerSecond
        self.samplingInterval = self.requestProb/arrivalsPerSecond
        self.clock.interval = self.samplingInterval

    def _generateRequest(self):
        """
        Sample the request type from the provided request types and create the Request object.
        """
        sampledRequestIndice = random.choices(self.requestTypeIndices, weights = self.requestTypeProbs)[0]
        _, typeMean, typeStd, typeTimeLimit = self.requestTypes[sampledRequestIndice]
        requestProcessingTime = random.gauss(mu=typeMean, sigma=typeStd)
        request = Request(type=sampledRequestIndice, processingTime = requestProcessingTime, timeRequirement=typeTimeLimit, environment = self.environment, id = self._getReqId())
        self.environment.logData("requestType", sampledRequestIndice)
        return request

    
    def _onSampleEvent(self):
        """
        This method is invoked when the sample event is executed and samples whether a request arrives and 
        creates the Request object and sends it to the loadbalancer.
        """
        invokeArrival = (random.uniform(0,1) < self.requestProb)
        if self.environment.debug: self.environment.logData("sampleEvent")
        if invokeArrival: 
            request = self._generateRequest()
            self.loadBalancer.handleRequestArrival(request)

class ExponentialSource():
    """
    Use exonential interarrival time 
    """
    def __init__(self, arrivalsPerSecond: float, requestTypes, loadBalancer: LoadBalancer, environment: Environment, requestProb = DEFAULT_REQUEST_PROB): #requestTypes: list[tuple]
        """
        Parameters
        ----------
        arrivalsPerSecond: float:
            number of arrivals per second (on average)
        requestTypes: list[tuple]
            A list containing info on the request types, structured like [(typeProb, typeMean, typeStd, timeLimit),...]
            where typeProb is the probability of the type arriving and typeMean and typeVar are the
            parameters used when sampling from the Normal distribution.
        loadBalancer: LoadBalancer
            The LoadBalancer instance that this source is connected to.
        environment: Environment
            The Environment instance that this source is connected to.
        """
        self.requestTypes = requestTypes
        self.loadBalancer = loadBalancer
        self.environment = environment
        self.setArrivalsPerSecond(arrivalsPerSecond=arrivalsPerSecond)
        self.requestTypeProbs = [requestType[0] for requestType in self.requestTypes]
        self.requestTypeIndices = list(range(0,len(self.requestTypes)))
        self.requestId = 0
        assert sum(self.requestTypeProbs) == 1.0, "typeProbs of provides requestTypes must sum to 1"

        self._onSampleEvent() #initialize

    def _getReqId(self):
        self.requestId +=1
        return self.requestId

    def setArrivalsPerSecond(self, arrivalsPerSecond):
        self.arrivalsPerSecond = arrivalsPerSecond

    def _generateRequest(self):
        """
        Sample the request type from the provided request types and create the Request object.
        """
        sampledRequestIndice = random.choices(self.requestTypeIndices, weights = self.requestTypeProbs)[0]
        _, typeMean, typeStd, typeTimeLimit = self.requestTypes[sampledRequestIndice]
        requestProcessingTime = random.gauss(mu=typeMean, sigma=typeStd)
        request = Request(type=sampledRequestIndice, processingTime = requestProcessingTime, timeRequirement=typeTimeLimit, environment = self.environment, id = self._getReqId())
        self.environment.logData("requestType", sampledRequestIndice)
        return request
    
    def _onSampleEvent(self):
        """
        This method is invoked when the sample event is executed and creates the request and schedules the next arrival
        """
        if self.environment.debug: self.environment.logData("sampleEvent")
        request = self._generateRequest()
        self.loadBalancer.handleRequestArrival(request)

        nextInterArrival = random.expovariate(self.arrivalsPerSecond)

        nextSampleEvent =  Event(self.environment.currentTime + nextInterArrival, self._onSampleEvent, "Exponential sample event")
        self.environment.scheduleEvent(nextSampleEvent)

class BatchedSource():
    """
    Generate all requests for a period in a vectorized way
    """
    def __init__(self, arrivalsPerSecond: float, requestTypes, loadBalancer: LoadBalancer, environment: Environment, periodLength: float, requestProb = DEFAULT_REQUEST_PROB):
        self.requestProb = requestProb
        assert self.requestProb <= 1.0, "Requestprob > 1"
        self.requestTypes = requestTypes
        self.loadBalancer = loadBalancer
        self.environment = environment
        self.periodLength = periodLength
        self.clock = EventClock(interval = self.periodLength, method=self._onSampleEvent, environment=environment)
        self.requestTypeProbs = [requestType[0] for requestType in self.requestTypes]
        self.requestTypeIndices = list(range(0,len(self.requestTypes)))
        self.setArrivalsPerSecond(arrivalsPerSecond=arrivalsPerSecond)
        self.requestId = 0

        assert len(requestTypes) == 2, "This source only works with two requesttypes"
        assert sum([requestType[0] for requestType in self.requestTypes]) == 1.0, "typeProbs of provides requestTypes must sum to 1"

    def setArrivalsPerSecond(self, arrivalsPerSecond):
        self.arrivalsPerSecond = arrivalsPerSecond
        self.samplingInterval = self.requestProb/arrivalsPerSecond
        self.nSamplesPerPeriod = round(self.periodLength/self.samplingInterval)

    def _getReqId(self):
        self.requestId +=1
        return self.requestId

    def _generateRequests(self, requestTypeIndex, requestTimes):
        _, typeMean, typeStd, typeTimeLimit = self.requestTypes[requestTypeIndex]
        requestProcessingTimes = np.random.normal(typeMean, typeStd, len(requestTimes))
        for t, requestProcessingTime in zip(requestTimes,requestProcessingTimes) :
            e = Event(t, lambda: self.loadBalancer.handleRequestArrival(Request(type=requestTypeIndex, processingTime = requestProcessingTime, timeRequirement=typeTimeLimit, environment = self.environment, id = self._getReqId())))
            self.environment.scheduleEvent(e)

    def _onSampleEvent(self):
        samplingTimes = self.environment.currentTime + np.arange(0,self.periodLength, self.samplingInterval)
        samples = np.random.rand(self.nSamplesPerPeriod)
        requestTimes = samplingTimes[samples < self.requestProb]
        typeOneProb = self.requestTypeProbs[0]
        requestTypes = (np.random.rand(len(requestTimes)) < typeOneProb).astype(int)
        requestTypeOneTimes = requestTimes[requestTypes == 0]
        self._generateRequests(0, requestTypeOneTimes)
        requestTypeTwoTimes = requestTimes[requestTypes == 1] 
        self._generateRequests(1, requestTypeTwoTimes)

class ArrivalSchedule:
    """
    Sets the arrival prob. for every period with length periodLength and notififies the loadBalancer that a new period has started.
    Can be easily extended to emulate any arrival process. Possibly depending on historic simulation data.
    """
    def __init__(self, periodLength, arrivalSchedule: list, environment, source, loadBalancer):
        self.periodIndex = 0
        self.arrivalSchedule = arrivalSchedule
        self.source = source
        self.loadBalancer = loadBalancer
        self.clock = EventClock(periodLength, self.nextPeriod, environment)
        self.currentPeriodIndex = 0
        self.nPeriods = len(arrivalSchedule)
        self.source.setArrivalsPerSecond(arrivalSchedule[0])
    
    def nextPeriod(self):
        nextPeriodIndex = self.currentPeriodIndex + 1
        if nextPeriodIndex == self.nPeriods: #if at the end of the schedule go back to 0
            nextPeriodIndex = 0
        self.currentPeriodIndex = nextPeriodIndex
        nextPeriodRequestProb = self.arrivalSchedule[nextPeriodIndex]
        self.source.setArrivalsPerSecond(nextPeriodRequestProb)
        self.loadBalancer.onPeriodEnd()




    


    