"""
cProfile progam analysis
"""
from Environment import Environment
from LoadBalancer import LoadBalancer
from Source import Source, ArrivalSchedule, BatchedSource, ExponentialSource
import cProfile
from datetime import datetime
import argparse



def main():
    stopTime = 12*60*60
    env = Environment(stopTime=stopTime, usePrio = True)

    loadBalancer = LoadBalancer(nServers=3, environment=env)

    requestTypes = [(0.5,1,0.1,10), (0.5,2,0.2,10)] #(prob, mu, sigma, cancelTime)
    arrivalsPerSecond = 14
    source = Source(arrivalsPerSecond, requestTypes, loadBalancer, env)

    schedule = [11,12,14,16,14,12,13,15,17,16,14,12] #12 periods
    periodLength = 0.5*60*60 #half an hour per period -> schedule repeated two times in 12 hours
    arrivalSchedule = ArrivalSchedule(periodLength,arrivalSchedule=schedule, environment=env, loadBalancer=loadBalancer, source=source)
    env.run(debug=False)

def printProfile(f):
    import pstats
    p = pstats.Stats('./profile/' + f)
    p.sort_stats('tottime').print_stats()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--f", help="increase output verbosity")
    args = parser.parse_args()

    filename = None

    if args.f:
        if args.f == '-1':
            import os
            print("yes")
            filenames  = os.listdir('./profile/')
            filename = sorted(filenames)[-1]
        else:
            filename = args.f
        printProfile(filename)

       

    else:
        now = datetime.now() # current date and time
        filename = f"profile_{now.strftime('%m%d%Y_%H%M%S')}"
        filedir = './profile/' + filename 
        cProfile.run('main()', filename=filedir)
        printProfile(filename)

