from sortedcontainers import SortedDict
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
        self.eventQueue = SortedDict() 
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
        self.eventQueue[e.time] = e
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

    def logData(self, key, data):
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

    def run(self, debug=True):
        """Run environment untill the stopTime is reached or untill the eventQueue is empty
        
        Parameters
        ----------
        debug : bool
            Print debugging messages?
        """
        while self.currentTime < self.stopTime and len(self.eventQueue) > 0:   
            self.debug = debug
            nextEventTime, nextEvent = self.eventQueue.popitem(index=0)
            self._handleEvent(nextEvent)
        if len(self.eventQueue) == 0: warnings.warn("Event queueu is empty before stopTime was reached")
        return self
        
    