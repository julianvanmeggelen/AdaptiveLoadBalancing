
class EventKey:
    """
    Key used in determining event order
    """
    def __init__(self, time, prio):
        self.time, self.prio = time, prio
    
    def __lt__(self, other):
        if self.time == other.time:
            return self.prio < other.prio
        else:
            return  self.time < other.time

    def __repr__(self):
        return f"{self.time}-{self.prio}"

class Event:
    def __init__(self, time: float, executionMethod: callable, name: str = 'unnamed', prio: int = 9):
        """
        Parameters
        ----------
        time : float
            Time the event should be triggered
        executionMethod : callable
            This function will get called when the event is triggered
        name : str, optional
            Option to provide name to event for debugging purposes
        """

        self.time = time
        self.executionMethod = executionMethod
        self.name = name
        self.isTriggered = False
        self.key: EventKey = EventKey(time, prio)

    def execute(self):
        """
            Calls the executionMethod and locks the event
        """

        if self.isTriggered:
            return Exception("Event has already been triggered")

        self.isTriggered = True
        self.executionMethod()
    
    def __call__(self):
        self.execute()

