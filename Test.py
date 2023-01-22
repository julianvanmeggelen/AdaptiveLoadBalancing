import unittest
from Event import Event
from Environment import Environment
from Source import Source, TestLoadBalancer, EventClock
from Request import Request
from Server import Server
from Server import Queue

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
        self.assertEqual(a[0],1)
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

class EventClockTest(unittest.TestCase):
    def testEventClock(self):
        def add(a,b):
            return a + b
            
        env = Environment(stopTime=10)
        env.debug=True
        count = TestValue(val=0)
        clock = EventClock(1,lambda: count.add(1) , environment=env)
        env.run()
        self.assertEqual(count.val, 10)


class SourceTest(unittest.TestCase):
    def testEventScheduling(self):
        from Source import DEFAULT_REQUEST_PROB
        stopTime = 10
        arrivalsPerSecond = 10
        samplingInterval = 0.1
        arrivalsPerSecond = DEFAULT_REQUEST_PROB / samplingInterval
        env = Environment(stopTime=stopTime)
        env.debug=True
        loadBalancer = TestLoadBalancer()
        source = Source(arrivalsPerSecond, [(0.5,1,0.1,10),(0.5,2,0.2,10)], loadBalancer, env)
        env.run(debug=True)
        nSamples = len(env.log["sampleEvent"])
        self.assertEqual(nSamples, stopTime/samplingInterval) #number of sample events should be stopTime/samplingInterval

    def testArrivalSampling(self):
        stopTime = 10
        env = Environment(stopTime=stopTime)
        loadBalancer = TestLoadBalancer()
        arrivalsPerSecond = 10
        source = Source(arrivalsPerSecond, [(0.5,1,0.1,10),(0.5,2,0.2,10)], loadBalancer, env)
        env.run(debug=True)
        nSamples = len(env.log["sampleEvent"])
        #nArrival = len(env.log["arrivalEvent"])
        #print(nSamples, nArrival)
        #print(nArrival/nSamples)
        #self.assertAlmostEqual(arrivalsPerSecond * stopTime, nArrival, delta=15) #test sample prob of arrival approximately equal to provided requestProb

    #def testRequestTypeSampling(self):
class QueueTest(unittest.TestCase):
    def testPushPull(self):
        env = Environment(stopTime=10)
        q = Queue(environment=env)
        correctOrder = []
        for i in range(10):
            req = Request(1,1,10,env)
            q.push(req)
            correctOrder.append(req.id)
        pulledOrder  = []
        for i in range(10):
            req = q.pull()
            pulledOrder.append(req.id)
        self.assertListEqual(pulledOrder, correctOrder)
    
    def testSize(self):
        env = Environment(stopTime=10)
        q = Queue(environment=env)
        req = Request(1,1,10,env)
        idToRemove = req.id
        q.push(req)
        req = Request(1,1,10,env)
        q.push(req)
        q.remove(idToRemove)
        self.assertEqual(q.size, 1)
        self.assertNotEqual(q.pull().id, idToRemove)

    def testSize2(self):
        env = Environment(stopTime=10)
        q = Queue(environment=env)
        req = Request(1,1,10,env)
        allIds = []
        for i in range(10):
            req = Request(1,1,10,env)
            q.push(req)
            allIds.append(req.id)
        for i in range(5):
            q.remove(allIds[i])
        self.assertEqual(q.size, 5)

    def testPull(self):
        env = Environment(stopTime=10)
        q = Queue(environment=env)
        allIds = []
        for i in range(10):
            req = Request(1,1,10,env)
            q.push(req)
            allIds.append(req.id)
        for i in range(10):
            q.remove(allIds[i])
            print(q.size)
        
        self.assertRaises(IndexError, q.pull)

class ServerTest(unittest.TestCase):
    def testServer(self):
        env = Environment(stopTime=10)
        server = Server(environment = env)

        for i in range(10): #assign 10 requests to the server, should be all finished within the time limit
            env.scheduleEvent(Event(0, lambda: server.assignRequest(Request(0, 1, 10, env)), "assignToServer"))
            print(len(env.eventQueue))
        
        print(len(env.eventQueue))
        env.run(debug=True)
        self.assertEqual(len(server.queue), 0)
        self.assertEqual(len(env.log["requestProcessed"]), 10)

class RequestTest(unittest.TestCase):
    def testCancel(self):
        env = Environment(stopTime=10)
        env = Environment(stopTime=10)
        req = Request(0, 1, 10, env) #request gets cancelled after 10 seconds
        env.run(debug=True)
        print(env.log['requestCancelled'])
        self.assertTrue(req.isCancelled)

    def testFinishprocessing(self):
        env = Environment(stopTime=10)
        server = Server(environment = env)
        req = Request(0, 1, 10, env) #request gets cancelled after 10 seconds, duration 1 sec
        req.assignToServer(server)
        req.startProcessing()
        env.run(debug=True)
        print(env.log['requestProcessed'])
        self.assertFalse(req.isCancelled)
        self.assertTrue(req.isProcessed)

    
if __name__ == '__main__':
    unittest.main()
    
