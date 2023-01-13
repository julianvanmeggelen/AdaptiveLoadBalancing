#from LoadBalancer import LoadBalancer TODO: switch to using these classes when implemented
from Environment import Environment
from Event import Event 
from Request import Request
import random


class LoadBalancer:
    def __init__(self):
        return
    def handleRequestArrival(self, req):
        return
        
class TestLoadBalancer:
    def __init__(self):
        return

    def handleRequestArrival(self, req):
        return

class Source():
    def __init__(self, samplingInterval: float, requestProb: float, requestTypes: list[tuple], loadBalancer: LoadBalancer, environment: Environment):
        """
        Parameters
        ----------
        samplingInterval: float
            The interval between each sample moment
        requestProb: float
            The probability of a request being spawned at each sample moment
        requestTypes: list[tuple]
            A list containing info on the request types, structured like [(typeProb, typeMean, typeStd, timeLimit),...]
            where typeProb is the probability of the type arriving and typeMean and typeVar are the
            parameters used when sampling from the Normal distribution.
        loadBalancer: LoadBalancer
            The LoadBalancer instance that this source is connected to.
        environment: Environment
            The Environment instance that this source is connected to.
        """
        self.samplingInterval = samplingInterval
        self.requestProb = requestProb
        self.requestTypes = requestTypes
        self.loadBalancer = loadBalancer
        self.environment = environment
        assert sum([requestType[0] for requestType in self.requestTypes]) == 1.0, "typeProbs of provides requestTypes must sum to 1"


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
        if self.environment.debug: self.environment.logData("requestType", sampledRequestIndice)
        return request

    
    def _onSampleEvent(self):
        """
        This method is invoked when the sample event is executed and samples whether a request arrives and 
        creates the Request object and sends it to the loadbalancer.
        """
        invokeArrival = (random.uniform(0,1) > self.requestProb)
        if self.environment.debug: self.environment.logData("sampleEvent")
        if invokeArrival: 
            if self.environment.debug: self.environment.logData("arrivalEvent")
            request = self._generateRequest()
            self.loadBalancer.handleRequestArrival(request)

        self.scheduleNextSampleEvent()


    def scheduleNextSampleEvent(self):
        """
        Schedule the next sampling event in the environment. This method can be used to initialize the
        environment with it's first event.
        """
        nextEventTime = self.environment.currentTime + self.samplingInterval
        nextEvent = Event(nextEventTime, self._onSampleEvent, "Arrival sampling event")
        self.environment.scheduleEvent(nextEvent)





    


    