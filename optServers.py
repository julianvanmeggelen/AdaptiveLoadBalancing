
import pandas as pd
import numpy as np
optResultsDf = pd.read_csv('../data/optServers3.csv')['Optimal number of servers']
arrivalsPerSecondList = np.arange(7.5,25.5,1)
optResultsDf = optResultsDf.to_dict()
optResults = {k:v for k,v in zip(arrivalsPerSecondList, optResultsDf.values())}

y = np.array(list(optResults.values()))
x = np.array(list(optResults.keys()))
A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y, rcond=None)[0]

def getOptServer(arrivalsPerSecond):
    """
    Get optimum for the given arrivalsPerSecond
    """
    return round(m*arrivalsPerSecond+c)