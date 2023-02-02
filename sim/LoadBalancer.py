from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: #only for typechecking
    from sim.Environment import Environment 
    from sim.Request import Request

from sim.Server import Server

class LoadBalancer:
    """
    Default loadbalancer using the Round-Robin assignment algorithm
    """
    def __init__(self, nServers, environment: Environment):
        self.nServers = nServers 
        self.environment = environment
        self.environment.logData("totalInQueue", 0)
        self.serverList = [Server(environment=environment, id=i) for i in range(nServers)]
        self.currentServer = 0

    def _setNumberOfServers(self, newNumber):
        self.environment.logData("numberOfServers", self.nServers) #log before

        if newNumber > self.nServers:
            diff = newNumber - self.nServers
            newServers = [Server(environment=self.environment, id=i) for i in range(diff)]
            self.serverList = self.serverList + newServers
            self.currentServer = newNumber - 1
        elif newNumber < self.nServers:
            self.serverList = self.serverList[:newNumber]
        
        self.nServers = newNumber
        #print(newNumber)
        self.environment.logData("numberOfServers", self.nServers) # log after

    def handleRequestArrival(self, request: Request):
        """
        Round robin assignment
        """
        self.environment.logData("arrivalEvent")
        if self.currentServer >= self.nServers: self.currentServer = 0
        self.serverList[self.currentServer].assignRequest(request=request)
        self.currentServer += 1
    
    def onPeriodEnd(self):
        """
        This method will be called on the end of each period, this is the place where the next period number of servers is determined
        """
        return
        #raise NotImplementedError

class LoadBalancerShortestQueue(LoadBalancer):
    """
    Loadbalancer assigning to servers random
    """
    def __init__(self, nServers, environment: Environment):
        super().__init__(nServers=nServers,environment=environment)
    
    def handleRequestArrival(self, request: Request):
        """
        Assign to shortest queue
        """
        self.environment.logData("arrivalEvent")
        shortest = min(self.serverList, key=lambda server: len(server.queue.queue))
        shortest.assignRequest(request=request)        
    
    def onPeriodEnd(self):
        """
        This method will be called on the end of each period, this is the place where the next period number of servers is determined
        """
        return
        #raise NotImplementedError



    