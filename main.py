from itertools import count
import numpy as np
import matplotlib.pyplot as plt
import config
import classes
import helpers
import experiments
import random

a, b, c, d, e = 'a', 'b', 'c', 'd', 'e'
config.Alternatives = [a,b]
config.PARTITION_ALGS = {
    1: helpers.randomSlicing,
    2: helpers.randomConstrained,
    3: helpers.randomIncrement,
    4: helpers.randomDeviate
}

# Exmp = {
#     a: 3*[0] + 4*[0] + 20*[1] + 6*[0], 
#     b: 3*[1] + 4*[4] + 20*[0] + 6*[0]
#     }

Exmp = {
    a: [2,2,1,1,1],
    b: [0,0,2,2,2],
}


publicEvidence = {
    a: {}, 
    b: {}
    }

##### Examples
# A = classes.Agent(id = 1, evidence={a:0, b:2}, type='keen')
# print(A.preferredTo({a,b}))

# n = len(Exmp[a])
# P = classes.Profile([classes.Agent(id = i+1, evidence = {a:Exmp[a][i], b:Exmp[b][i]}, type='lazy') for i in range(n)])
# D = classes.Deliberation(Profile = P, Protocol = 'sim')
# print(D)


##### Experiments
# experiments.differentPartitionAlgs()
# experiments.samePartitionAlg(algorithm=helpers.randomDeviate)

nrTrials = 5000
experiments.protocolsDifferentAgentType(trials=nrTrials, n=10, B=30)
experiments.varEvidenceConstantN(trials=nrTrials, n=10, B=30)
experiments.varRoundsToTermination(trials=nrTrials, n=10, B=30)
