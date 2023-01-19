from sortedcontainers import SortedKeyList
import warnings

from Event import Event


class Environment:
    def __init__(self, stopTime):
        """
        Parameters
        ----------
        stopTime : float
            Time the simulation should be stopped
        """
        self.stopTime = stopTime
        self.currentTime = 0
        self.eventQueue: SortedKeyList = SortedKeyList(key=lambda e: e.key) 
        self.debug = 0
        self.log = {} #dictionary for storage of arbitary statistics
        self.logTime = {} #store timestamps of logs
    
    def scheduleEvent(self, e: Event):
        """Add event to eventqueue

        Parameters
        ----------
        e : Event
            The event that needs to be scheduled
        """
        self.eventQueue.add(e)
        if self.debug: print(f"{self.currentTime} | Planned event for time {e.time} with name {e.name}")
    
    def _handleEvent(self, e:Event):
        """Handle event to eventqueue (private method)
        
        Parameters
        ----------
        e : Event
            The event that needs to be handled
        """
        self.currentTime = e.time
        e.execute()
        if self.debug: print(f"{self.currentTime} | Handled event at time {e.time} with name {e.name}")

    def logData(self, key, data=1):
        """Log arbitrary data to the environment
        
        Parameters
        ----------
        key : str
            Unique identifier for the data stream
        data: any
            Data to log to the stream 
        """

        if key not in self.log.keys():
            self.log[key] = [data]
            self.logTime[key] = [self.currentTime]
        else:
            self.log[key].append(data)
            self.logTime[key].append(self.currentTime)

    def run(self, debug=True, showProgress = False):
        """Run environment untill the stopTime is reached or untill the eventQueue is empty
        
        Parameters
        ----------
        debug : bool
            Print debugging messages?
        """
        
        while len(self.eventQueue) > 0:   
            self.debug = debug
            nextEvent = self.eventQueue.pop(index=0)
            nextEventTime = nextEvent.time
            if nextEventTime > self.stopTime: break
            self._handleEvent(nextEvent)
            if showProgress:
                print(f"{int(self.currentTime)} | {int(self.currentTime/self.stopTime*10)*'=' + '>'}", end='\r')

        if len(self.eventQueue) == 0: warnings.warn("Event queueu is empty before stopTime was reached")
        return self
        
    