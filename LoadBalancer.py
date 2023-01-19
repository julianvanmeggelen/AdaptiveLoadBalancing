from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: #only for typechecking
    from Environment import Environment 
    from Request import Request

from Server import Server

class LoadBalancer:
    """
    Default loadbalancer using the Round-Robin assignment algorithm
    """
    def __init__(self, nServers, environment: Environment):
        self.nServers = nServers 
        self.environment = environment
        self.serverList = [Server(environment=environment, id=i) for i in range(nServers)]
        self.currentServer = 0
    
    def handleRequestArrival(self, request: Request):
        """
        Round robin assignment
        """
        if self.currentServer >= self.nServers: self.currentServer = 0
        self.serverList[self.currentServer].assignRequest(request=request)
        self.currentServer += 1

        nQueue = sum([server.queue.size for server in self.serverList])
        self.environment.logData("totalInQueue", nQueue)
    
    def onPeriodEnd(self):
        """
        This method will be called on the end of each period, this is the place where the next period number of servers is determined
        """
        return
        #raise NotImplementedError

    