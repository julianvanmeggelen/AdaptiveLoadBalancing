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



    