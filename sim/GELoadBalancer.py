from sim.LoadBalancer import LoadBalancer
from sim.Source import ArrivalSchedule, Source
from sim.Environment import Environment
import numpy as np
import random
import math


class GreedyEpsilonLoadBalancer(LoadBalancer):
    def __init__(self, nServers, environment, model, processReward=1, cancelReward=-10, serverReward=-300, eta=0.15, nServerRange = (1,40), usePartialFit=False, periodLength =1*60*60):
        """
            model: obj with methods predict, fit, fit_partial etc.
            eta: float or callable(periodIndex: int -> float)
        """
        super().__init__(nServers, environment)
        self.model = model # a model that takes (N_t, X_t) and predicts the reward of the next time period
        self.agg = {'totalInQueue': np.mean,'requestStartWaiting':np.sum,'arrivalEvent':np.sum,'requestWaitingTime': np.mean,'requestProcessed':np.sum,'totalTimeInSystem':np.mean,'requestCancelled':np.sum}
        self.currentPeriod = 0
        self.processReward, self.cancelReward, self.serverReward = processReward, cancelReward, serverReward
        self.eta = eta
        self.nServerRange = nServerRange #the range for the bernoulli to sample from
        self.usePartialFit = usePartialFit
        self.periodLength = periodLength
        self.X = None #store the complete feature dataset here
        self.y = None #store the complete target dataset here s

    def getEta(self):
        if callable(self.eta):
            return self.eta(self.currentPeriod)
        else:
            return self.eta

    def getPreviousPeriodContext(self):
        """
        Get the context from the period that just ended (potentially add lags here from previous periods)
        """
        previousPeriodData = self.environment.getPeriodLog() #returns {key: values}
        previousPeriodContext = {key: self.agg[key](vals) for key,vals in previousPeriodData.items() if key in self.agg.keys()} #apply aggregation: go from lists to scalars
        previousPeriodContext ={key:val if not np.isnan(val) else 0 for key,val in previousPeriodContext.items()}
        previousPeriodContext ={key:previousPeriodContext[key] if key in previousPeriodContext.keys() else 0 for key in self.agg.keys()}

        return previousPeriodContext

    def getPreviousPeriodReward(self, context: dict):
        """
        Get the reward of the period that just ended
        """
        nProcessed = context['requestProcessed']
        nCancelled = context['requestCancelled'] if 'requestCancelled' in context.keys() else 0
        nServers = self.nServers
        reward = nProcessed * self.processReward + nCancelled * self.cancelReward + self.periodLength/60/60*nServers*self.serverReward
        print(nProcessed, nCancelled, nServers, reward)
        return reward

    def findModelOptimum(self, context):
        max = -math.inf
        maxArg = 0
        for n in range(self.nServerRange[0], self.nServerRange[1]): #implement better optimization here
            X =  np.append(np.array(list(context.values())), n)
            rewardHat = self.model.predict(X[None,:])[0]
            if rewardHat > max:
                maxArg = n
                max = rewardHat
        print("Max reward for", rewardHat, maxArg)
        return maxArg

    def getNextPeriodNumberOfServers(self, context):
        #take random action or input the context into the model and maximizy the output w.r.t N
        draw = random.random()
        eta = self.getEta()
        self.environment.logData('eta', eta)
        nServers = None
        if draw < eta or self.currentPeriod <= 1: #on first iteration the model is not fitted
            #Take random action
            self.environment.logData("greedyEpsilonActionType", 0)
            nServers = random.randint(self.nServerRange[0], self.nServerRange[1])
        else:
            self.environment.logData("greedyEpsilonActionType", 1)
            nServers = self.findModelOptimum(context) 

        return nServers
        
    def updateModel(self, context, reward):
        #update the model using the context, nServers and observed reward
        if self.currentPeriod > 0:
            newY = np.array([reward])
            self.y = np.append(self.y, newY[None,:], axis=0) if self.y is not None else newY[None,:]
            if not self.usePartialFit:
                #print(self.X.shape,self.y.shape)
                self.model = self.model.fit(self.X, self.y) #make sure the hat the last period x is ignored
                print(self.model.score(self.X, self.y))
            else:
                self.model = self.model.partial_fit(self.X, self.y) #make sure the hat the last period x is ignored
                print(self.model.score(self.X, self.y))

    def updateX(self, context, nOptimal):
        newX = np.array(list(context.values()) + [nOptimal]) #+ [reward] #add the current nServers to X
        self.X = np.append(self.X, newX[None,:], axis=0) if self.X is not None else newX[None,:] #update the data 

    def onPeriodEnd(self):
        #Get the reward of the current period
        previousPeriodContext = self.getPreviousPeriodContext()
        self.environment.resetPeriod()
        #print(previousPeriodContext)
        previousPeriodReward = self.getPreviousPeriodReward(previousPeriodContext)
        self.environment.logData("reward", previousPeriodReward)
        self.updateModel(previousPeriodContext, previousPeriodReward)
        if self.currentPeriod>0:print(self.X.shape,self.y.shape)
        nextPeriodNServers = self.getNextPeriodNumberOfServers(previousPeriodContext)
        self._setNumberOfServers(nextPeriodNServers)
        self.updateX(previousPeriodContext, nextPeriodNServers)
        self.currentPeriod+=1
        print(self.nServers)
        return previousPeriodContext


class GreedyEpsilonLoadBalancerContextSampling(LoadBalancer):
    """
    context sampled from dist, see experiments/quadraticarrivalprocess.ipynb
    """
    def __init__(self, nServers, environment, model, processReward=1, cancelReward=-10, serverReward=-300, eta=0.15, nServerRange = (1,40), usePartialFit=False, periodLength =1*60*60, linear=True):
        """
            model: obj with methods predict, fit, fit_partial etc.
            eta: float or callable(periodIndex: int -> float)
        """
        super().__init__(nServers, environment)
        self.model = model # a model that takes (N_t, X_t) and predicts the reward of the next time period
        self.agg = {'totalInQueue': np.mean,'requestStartWaiting':np.sum,'arrivalEvent':np.sum,'requestWaitingTime': np.mean,'requestProcessed':np.sum,'totalTimeInSystem':np.mean,'requestCancelled':np.sum}
        self.currentPeriod = 0
        self.processReward, self.cancelReward, self.serverReward = processReward, cancelReward, serverReward
        self.eta = eta
        self.nServerRange = nServerRange #the range for the bernoulli to sample from
        self.usePartialFit = usePartialFit
        self.periodLength = periodLength
        self.X = None #store the complete feature dataset here
        self.y = None #store the complete target dataset here s
        self.linear = linear
        if not linear:
            self.A = np.random.uniform(0,0.5,(6,6))
            self.B = np.random.uniform(0,0.5,(6,6))
        else:    
            self.A = np.random.uniform(0,1,6)
            self.B = np.random.uniform(0,1,6)
        self.mu = np.array([0,0,0,0,0,0]) #for mv normal
        self.cov = np.diag([1,1,1,1,1,1]) #for mv normal

    def getEta(self):
        if callable(self.eta):
            return self.eta(self.currentPeriod)
        else:
            return self.eta


    def getPreviousPeriodContext(self):
        """
        !!! This only used for the computation of the reward not for the model!
        """
        previousPeriodData = self.environment.getPeriodLog() #returns {key: values}
        previousPeriodContext = {key: self.agg[key](vals) for key,vals in previousPeriodData.items() if key in self.agg.keys()} #apply aggregation: go from lists to scalars
        previousPeriodContext ={key:val if not np.isnan(val) else 0 for key,val in previousPeriodContext.items()}
        previousPeriodContext ={key:previousPeriodContext[key] if key in previousPeriodContext.keys() else 0 for key in self.agg.keys()}

        return previousPeriodContext

    def getPreviousPeriodReward(self):
        """
        Get the reward of the period that just ended
        """
        context = self.getPreviousPeriodContext()
        nProcessed = context['requestProcessed']
        nCancelled = context['requestCancelled'] if 'requestCancelled' in context.keys() else 0
        nServers = self.nServers
        reward = nProcessed * self.processReward + nCancelled * self.cancelReward + self.periodLength/60/60*nServers*self.serverReward
        print(nProcessed, nCancelled, nServers, reward)
        return reward

    def findModelOptimum(self, context):
        max = -math.inf
        maxArg = 0
        for n in range(self.nServerRange[0], self.nServerRange[1]): #implement better optimization here
            X =  np.append(context, n)
            rewardHat = self.model.predict(X[None,:])[0]
            if rewardHat > max:
                maxArg = n
                max = rewardHat
        print("Max reward for", rewardHat, maxArg)
        return maxArg

    def getNextPeriodNumberOfServers(self, context):
        #take random action or input the context into the model and maximizy the output w.r.t N
        draw = random.random()
        eta = self.getEta()
        self.environment.logData('eta', eta)
        nServers = None
        if draw < eta or self.currentPeriod <= 1: #on first iteration the model is not fitted
            #Take random action
            self.environment.logData("greedyEpsilonActionType", 0)
            nServers = random.randint(self.nServerRange[0], self.nServerRange[1])
        else:
            self.environment.logData("greedyEpsilonActionType", 1)
            nServers = self.findModelOptimum(context) 

        return nServers
        
    def updateModel(self, context, reward):
        #update the model using the context, nServers and observed reward
        if self.currentPeriod > 0:
            newY = np.array([reward])
            self.y = np.append(self.y, newY[None,:], axis=0) if self.y is not None else newY[None,:]
            if not self.usePartialFit:
                #print(self.X.shape,self.y.shape)
                self.model = self.model.fit(self.X, self.y) #make sure the hat the last period x is ignored
                print(self.model.score(self.X, self.y))
            else:
                self.model = self.model.partial_fit(self.X, self.y) #make sure the hat the last period x is ignored
                print(self.model.score(self.X, self.y))

    def updateX(self, context, nOptimal):
        newX = np.append(context, nOptimal) #+ [reward] #add the current nServers to X
        self.X = np.append(self.X, newX[None,:], axis=0) if self.X is not None else newX[None,:] #update the data 

    def onPeriodEnd(self, previousPeriodContext):
        previousPeriodReward = self.getPreviousPeriodReward()
        self.environment.resetPeriod()
        self.environment.logData("reward", previousPeriodReward)
        self.updateModel(previousPeriodContext, previousPeriodReward)
        if self.currentPeriod>0:print(self.X.shape,self.y.shape)
        nextPeriodNServers = self.getNextPeriodNumberOfServers(previousPeriodContext)
        self._setNumberOfServers(nextPeriodNServers)
        self.updateX(previousPeriodContext, nextPeriodNServers)
        self.currentPeriod+=1
        print(self.nServers)
        return previousPeriodContext

def sigmoid(a):
    return 1/(1+np.exp(-a))