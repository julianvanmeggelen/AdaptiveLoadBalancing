from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: #only for typechecking
    from Request import Request 

from Environment import Environment
import math

class Queue:

    def __init__(self, length=math.inf):
        '''
        length: maximum number of requests per server
        '''
        self.length = length
        self.size = 0
        self.queue: list[Request] = []
    
    def push(self, request: Request):
        if (self.size<self.length):
            self.size += 1
            self.queue.append(request)
        else:
            request.cancelRequest()

    def updateQueue(self):
        """
        Remove cancelled requests from queue
        """
        self.queue = [req for req in self.queue if not req.isCancelled]
        self.size = len(self.queue)
    
    def pull(self) -> Request:
        """
        Retreive next request that is not cancelled
        """
        self.updateQueue()
        nextRequest = self.queue.pop()
        self.size -= 1
        return nextRequest

    def __len__(self):
        self.updateQueue()
        return self.size

class Server:
    def __init__(self, environment: Environment):
        '''
        environment: the simulation environment
        '''
        self.queue: Queue = Queue()
        self.environment: Environment = environment
        self.nowServing: Request = None

    def assignRequest(self, request: Request):
        """
        LoadBalancer uses this method to assign request to this server
        """
        request.assignToServer(self)
        self.queue.push(request)
        if self.nowServing is None:
            self.startServingNext()

    def currentRequestFinished(self):
        """
        Invoked by the request if the request is cancelled while being processed or if the request is finished
        """
        self.nowServing = None
        self.startServingNext()

    def startServingNext(self):
        '''
        start process the next request if there is a request waiting
        '''
        if len(self.queue) > 0:
            nextRequest = self.queue.pull()
            nextRequest.startProcessing()
            self.nowServing = nextRequest
