from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: #only for typechecking
    from LoadBalancer import LoadBalancer 

from Environment import Environment
from Event import Event 
from Request import Request
import random
DEFAULT_SAMPLING_INTERVAL = 0.05

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
    def __init__(self, arrivalsPerSecond: float, requestTypes, loadBalancer: LoadBalancer, environment: Environment, samplingInterval = DEFAULT_SAMPLING_INTERVAL): #requestTypes: list[tuple]
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
        self.arrivalsPerSecond = arrivalsPerSecond
        self.samplingInterval = samplingInterval
        self.requestProb = self.samplingInterval * arrivalsPerSecond
        self.requestTypes = requestTypes
        self.loadBalancer = loadBalancer
        self.environment = environment
        self.clock = EventClock(interval = self.samplingInterval, method=self._onSampleEvent, environment=environment)
        assert sum([requestType[0] for requestType in self.requestTypes]) == 1.0, "typeProbs of provides requestTypes must sum to 1"

    def setRequestProb(self, prob):
        self.requestProb = prob

    def _generateRequest(self):
        """
        Sample the request type from the provided request types and create the Request object.
        """
        requestTypeIndices = list(range(0,len(self.requestTypes)))
        requestTypeProbs = [requestType[1] for requestType in self.requestTypes]
        sampledRequestIndice = random.choices(requestTypeIndices, weights = requestTypeProbs)[0]
        _, typeMean, typeStd, typeTimeLimit = self.requestTypes[sampledRequestIndice]
        requestProcessingTime = random.gauss(mu=typeMean, sigma=typeStd)
        request = Request(type=sampledRequestIndice, processingTime = requestProcessingTime, timeRequirement=typeTimeLimit, environment = self.environment)
        self.environment.logData("requestType", sampledRequestIndice)
        return request

    
    def _onSampleEvent(self):
        """
        This method is invoked when the sample event is executed and samples whether a request arrives and 
        creates the Request object and sends it to the loadbalancer.
        """
        invokeArrival = (random.uniform(0,1) < self.requestProb)
        self.environment.logData("sampleEvent")
        if invokeArrival: 
            self.environment.logData("arrivalEvent")
            request = self._generateRequest()
            self.loadBalancer.handleRequestArrival(request)

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
        self.source.setRequestProb(arrivalSchedule[0])
    
    def nextPeriod(self):
        nextPeriodIndex = self.currentPeriodIndex + 1
        if nextPeriodIndex == self.nPeriods: #if at the end of the schedule go back to 0
            nextPeriodIndex = 0
        self.currentPeriodIndex = nextPeriodIndex
        nextPeriodRequestProb = self.arrivalSchedule[nextPeriodIndex]
        self.source.setRequestProb(nextPeriodRequestProb)
        self.loadBalancer.onPeriodEnd()




    


    