from Environment import Environment
from LoadBalancer import LoadBalancer
from Source import Source, ArrivalSchedule

def costCalculate(stopTime, nServers, arrivalsPerSecond, requestTypes, processCost = 1, cancelCost = -10, serverCost = -300):
    env = Environment(stopTime=stopTime)
    loadBalancer = LoadBalancer(nServers=nServers, environment=env)
    source = Source(arrivalsPerSecond, requestTypes, loadBalancer, env)
    env.run(debug=False)
    nCancelled = len(env.log['requestCancelled']) if 'requestCancelled' in env.log.keys() else 0
    cost = len(env.log['requestProcessed']) * processCost + nCancelled * cancelCost + stopTime/60/60*nServers*serverCost
    return cost

def binaryServerSearch(arrivalRate=0.5, searchSpace=[10,40], processCost = 1, cancelCost = -10, serverCost = -300, requestTypes = [(0.5,1,0.1,10), (0.5,2,0.2,10)]):
    arrivalsPerSecond = 20*arrivalRate #Default sampling interval=0.05
    stopTime = 3*60*60
    left = searchSpace[0]
    right = searchSpace[1]
    dif = right-left
    profit = [None]*(right-left)
    while (dif>2):
        mid = (left+right)/2
        left_temp = round((left+mid)/2)
        right_temp = round((right+mid)/2)
        for n in [left_temp,right_temp]:
            profit[n-searchSpace[0]] = costCalculate(stopTime=stopTime,nServers=n,arrivalsPerSecond=arrivalsPerSecond,requestTypes=requestTypes)
        if (profit[left_temp-searchSpace[0]]>profit[right_temp-searchSpace[0]]):
            right = round(mid)
        else:
            left = round(mid)
        dif = right-left
    n_star = left
    for n in range(left,right+1):
        if (profit[n-searchSpace[0]]==None):
            profit[n-searchSpace[0]] = costCalculate(stopTime=stopTime,nServers=n,arrivalsPerSecond=arrivalsPerSecond,requestTypes=requestTypes)
        if (profit[n-searchSpace[0]]>profit[n_star-searchSpace[0]]):
            n_star = n
    return n_star
