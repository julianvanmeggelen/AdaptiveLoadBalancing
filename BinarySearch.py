from Environment import Environment
from LoadBalancer import LoadBalancer
from Source import Source, ArrivalSchedule
import math
import numpy as np

def costCalculate(stopTime, nServers, arrivalsPerSecond, requestTypes, processCost = 1, cancelCost = -10, serverCost = -300):
    env = Environment(stopTime=stopTime)
    loadBalancer = LoadBalancer(nServers=nServers, environment=env)
    source = Source(arrivalsPerSecond, requestTypes, loadBalancer, env)
    env.run(debug=False)
    nCancelled = len(env.log['requestCancelled']) if 'requestCancelled' in env.log.keys() else 0
    cost = len(env.log['requestProcessed']) * processCost + nCancelled * cancelCost + stopTime/60/60*nServers*serverCost
    return cost

def binaryServerSearch(arrivalsPerSecond, searchSpace=[10,40], processCost = 1, cancelCost = -10, serverCost = -300, requestTypes = [(0.5,1,0.1,10), (0.5,2,0.2,10)], simDuration=3*60*60):
    stopTime = simDuration
    left = searchSpace[0]
    right = searchSpace[1]
    dif = right-left
    while (dif>2):
        mid = (left+right)/2
        left_temp = math.floor(mid)
        right_temp = left_temp+1
        cost_left = costCalculate(stopTime=stopTime,nServers=left_temp,arrivalsPerSecond=arrivalsPerSecond,requestTypes=requestTypes, processCost=processCost,cancelCost=cancelCost,serverCost=serverCost)
        cost_right = costCalculate(stopTime=stopTime,nServers=right_temp,arrivalsPerSecond=arrivalsPerSecond,requestTypes=requestTypes, processCost=processCost,cancelCost=cancelCost,serverCost=serverCost)
        if (cost_left>cost_right):
            right = right_temp
        else:
            left = left_temp
        dif = right-left
    cost_middle = costCalculate(stopTime=stopTime,nServers=left+1,arrivalsPerSecond=arrivalsPerSecond,requestTypes=requestTypes)
    cost_list = [cost_left,cost_middle,cost_right]
    n_star = left+int(np.where(cost_list==np.max(cost_list))[0][0])
    return n_star

