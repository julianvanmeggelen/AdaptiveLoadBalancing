from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import uuid1
if TYPE_CHECKING: #only for typechecking
    from Request import Request 

from Environment import Environment
import math

class Queue:

    def __init__(self, environment: Environment, length=math.inf, id=0):
        '''
        length: maximum number of requests per server
        '''
        self.id = id
        self.length = length
        self.size = 0
        self.queue: list[Request] = []
        self.environment = environment
    
    def push(self, request: Request):
        if (self.size<self.length) and not request.isCancelled:
            self.size += 1
            self.queue.append(request)
        else:
            request.cancelRequest()
        self.logSize(self.size)

    def updateQueue(self):
        """
        Remove cancelled requests from queue
        """
        self.queue = [req for req in self.queue if not req.isCancelled]
        self.size = len(self.queue)
    
    def pull(self) -> Request:
        """
        Retrieve next request that is not cancelled
        """
        self.updateQueue()
        nextRequest = self.queue.pop()
        self.size -= 1
        self.logSize(self.size)
        return nextRequest

    def logSize(self, size):
        size = self.__len__() if size is None else size
        print(size)
        logKey = f"queueSize_{self.id}"
        self.environment.logData(logKey, size)

    def __len__(self):
        self.updateQueue()
        return self.size

class Server:
    def __init__(self, environment: Environment, id=None):
        '''
        environment: the simulation environment
        '''
        self.id = id if id is not None else uuid1()
        self.queue: Queue = Queue(environment, id=self.id)
        self.environment: Environment = environment
        self.nowServing: Request = None
        

    def assignRequest(self, request: Request):
        """
        LoadBalancer uses this method to assign request to this server
        """
        request.assignToServer(self)
        if self.nowServing is None:
            request.startProcessing()
            self.nowServing = request
        else:
            self.queue.push(request)



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
