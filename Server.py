from Request import Request

class Queue:
    def __init__(self, length):
        '''
        length: maximum number of requests per server
        '''
        self.length = length
        self.size = 0
        self.queue = []
    
    def push(self, request: Request):
        if (self.size<self.length):
            self.size += 1
            self.queue.append(request)
            request.startWaiting()
        else:
            request.isCancelled = 1
    
    def pull(self):
        self.size -= 1
        self.queue[self.size].endWaiting()
        return self.queue.pop()

class Server:
    def __init__(self, queue: Queue):
        '''
        queue: the queue of requests waiting to be processed
        '''
        self.queue = queue
        self.nowServing = []
    
    def startServingNext(self, time):
        '''
        start process the next request when nowServing is empty
        '''
        self.nowServing.append(self.queue.pull())
        self.nowServing[0].startProcessing(time)
