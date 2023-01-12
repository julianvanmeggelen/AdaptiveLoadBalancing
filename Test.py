import unittest
from Event import Event
from Environment import Environment

class TestValue:
    def __init__(self, val):
        self.val = val
    
    def add(self, other):
        self.val+=other

class EventTest(unittest.TestCase):
    def testExecutionMethod(self):
        a = TestValue(1)
        method = lambda: a.add(1)
        e = Event(10, method)
        e.execute()
        self.assertEqual(a.val, 2)

    def testAlreadyTriggered(self):
        a = TestValue(1)
        method = lambda: a.add(1)
        e = Event(10, method)
        e.execute()
        e.execute()
        self.assertTrue(e.isTriggered, 2)
        self.assertEqual(a.val, 2)


class  EnvironmentTest(unittest.TestCase):
    def testExecutionOrder(self):
        a = []
        e1 = Event(3, lambda: a.append(2))
        e2 = Event(2, lambda: a.append(1))
        env = Environment(stopTime=10)
        env.scheduleEvent(e1)
        env.scheduleEvent(e2)
        env.run()
        self.assertEqual(a[0],2)
        self.assertEqual(a[1],2)
    
    def testLogData(self):
        env = Environment(stopTime=10)
        e1 = Event(3, lambda: env.logData("test", 2))
        env.scheduleEvent(e1)
        e2 = Event(2, lambda: env.logData("test", 1))
        env.scheduleEvent(e2)
        env.run()
        self.assertListEqual(env.log["test"], [1,2]) #test correct order
        self.assertListEqual(env.logTime["test"], [2,3]) #test correct timestamps

        



    
if __name__ == '__main__':
    unittest.main()
    
