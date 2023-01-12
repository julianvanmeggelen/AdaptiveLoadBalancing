class Event:
    def __init__(self, time: float, executionMethod: callable, name: str = 'unnamed'):
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

