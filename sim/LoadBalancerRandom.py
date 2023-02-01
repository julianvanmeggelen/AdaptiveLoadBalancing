from __future__ import annotations
import random
from typing import TYPE_CHECKING
from sim.LoadBalancer import LoadBalancer

if TYPE_CHECKING: #only for typechecking
    from sim.Environment import Environment 
    from sim.Request import Request

from sim.Server import Server

class LoadBalancerRandom(LoadBalancer):
    """
    Loadbalancer assigning to servers random
    """
    def __init__(self, nServers, environment: Environment):
        super().__init__(nServers=nServers,environment=environment)
        self.currentServer = random.randint(0,nServers-1)
    
    def handleRequestArrival(self, request: Request):
        """
        Round robin assignment
        """
        self.environment.logData("arrivalEvent")
        self.serverList[self.currentServer].assignRequest(request=request)
        self.currentServer = random.randint(0,self.nServers-1)
    
    
    def onPeriodEnd(self):
        """
        This method will be called on the end of each period, this is the place where the next period number of servers is determined
        """
        return
        #raise NotImplementedError
