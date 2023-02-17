from hashlib import algorithms_available
import config
import classes
import helpers
import random
import numpy as np
import matplotlib.pyplot as plt

a, b, c = 'a', 'b', 'c'
config.Alternatives = [a,b]

def differentPartitionAlgs(S=100, n=10, minShare=8, maxShare=12, startShare=9, trials=3000):
    for i in [2, 3, 4]:
        alg = config.PARTITION_ALGS[i]
        algName = str(alg).split()[1]
        plt.hist(
            [np.var(alg(S, n, minShare, maxShare, startShare)) for i in range(trials)], 
            density=True, 
            bins = 16, 
            color=config.COLOR_DICT[i+4], 
            ec='lightgrey',
            lw=0.2,
            alpha=0.75,
            label=algName
            )

    plt.xlabel(
        r"Variance ($S={S}, n={n}, m = {m}, M = {M}$)".format(
            S=S, n=n, m = minShare, M = maxShare
            )
        )
    plt.ylabel('Frequency')
    plt.grid(linestyle=':', alpha=0.3)
    plt.legend()
    plt.savefig('different-partition-algs.png', dpi=500)

def samePartitionAlg(
    S=100, n=10, minShare=9, maxShare=11, startShare=9, 
    algorithm=helpers.randomConstrained, 
    trials=3000
    ):
    steps = [1, 2, 3]
    for step in steps:
        plt.hist(
            [np.var(algorithm(S, n, minShare-step, maxShare+step, startShare)) for i in range(trials)], 
            density=True, 
            bins = 16, 
            color=config.COLOR_DICT[step], 
            ec='lightgrey',
            lw=0.2,
            alpha=0.6,
            label='[{m}, {M}]'.format(m=minShare-step, M=maxShare+step)
            )

    plt.xlabel(r"Variance ($S={S}, n={n}$) for {A}".format(S=S, n=n, A = str(algorithm).split()[1]))
    plt.ylabel('Frequency')
    plt.grid(linestyle=':', alpha=0.3)
    plt.legend()
    plt.savefig('same-partition-alg.png', dpi=500)

def protocolsDifferentN():
    nRange = range(5, 31)
    A, B = 50, 30
    protocols = ['sim', 'seq-const']
    alg = config.PARTITION_ALGS[4]
    trials = 200
    fig, ax = plt.subplots()

    for i in range(len(protocols)):
        successRates = []
        for n in nRange:
            aMin, aMax, aStart = (A//n)-2, (A//n)+2, (A//n)-1
            bMin, bMax, bStart = (B//n)-2, (A//n)+2, (B//n)-1

            successes = 0
            for trial in range(trials):
                aDist = alg(A, n=n, minShare=aMin, maxShare=aMax, startShare=aStart)
                bDist = alg(B, n=n, minShare=bMin, maxShare=bMax, startShare=bStart)
                P = classes.Profile(
                    [
                        classes.Agent(id = i+1, evidence = {a:aDist[i], b:bDist[i]}, type='lazy') for i in range(n)
                        ]
                    )
                D = classes.Deliberation(Profile = P, Protocol = protocols[i])
                if D.finalWinners == {a}:
                    successes += 1
            successRates.append(successes/trials)
        ax.plot(
            nRange, 
            successRates, 
            color=config.COLOR_DICT[i+1],
            linewidth=2.0,
            marker='.',
            label='{p}'.format(p = protocols[i])
            )
    
    ax.grid(linestyle=':')
    ax.set_xlim(min(nRange)-0.25, max(nRange)+0.5)
    plt.xticks([i for i in nRange if i%2 == 0])
    plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('$n$')
    plt.title('Comparing protocols, A = {A}, B = {B}'.format(A = A, B = B))
    plt.ylabel('Success rate')
    ax.legend()
    plt.show()

def evidenceGap():
    B = 30
    protocol = 'seq-const'
    aRange = range(B+1, 3*B+1)
    profileSizes = {
        1:10, 
        2:15, 
        3:20, 
        4:25
        }
    alg = config.PARTITION_ALGS[4]
    trials = 200
    fig, ax = plt.subplots()
    for i in profileSizes.keys():
        n = profileSizes[i]
        mb, Mb, sb = (B//n)-2, (B//n)+2, (B//n)-1
        successRates = []
        for A in aRange:
            ma, Ma, sa = (A//n)-6, (A//n)+6, (A//n)-1
            successes = 0
            for trial in range(trials):
                aDist = alg(A, n=n, minShare=ma, maxShare=Ma, startShare=sa)
                bDist = alg(B, n=n, minShare=mb, maxShare=Mb, startShare=sb)
                P = classes.Profile(
                    [classes.Agent(id = i+1, evidence = {a:aDist[i], b:bDist[i]}) for i in range(n)]
                    )
                D = classes.Deliberation(Profile = P, Protocol = protocol)
                if D.finalWinners == {a}:
                    successes += 1
            successRates.append(successes/trials)
        ax.plot(
            aRange, 
            successRates, 
            color=config.COLOR_DICT[i],
            linewidth=2.0,
            marker='.',
            label='$n$ = {n}'.format(n=n)
            )
        
    ax.grid(linestyle=':')
    ax.set_xlim(min(aRange)-0.25, max(aRange)+0.5)
    plt.xticks([i for i in aRange if i%5 == 0])
    plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('Amount of evidence for $a$')
    plt.title('{p} protocol, $B$ = {B}'.format(p = protocol, B = B))
    plt.ylabel('Success rate with {a} protocol'.format(a = protocol))
    ax.legend()
    plt.show()

def protocolsDifferentAgentType(trials, n, B):
    protocols = ['sim', 'seq-const']
    aRange = range(B+1, 101)
    agentTypes = ['lazy', 'keen']
    alg = config.PARTITION_ALGS[4]
    fig, ax = plt.subplots()
    colorKey = 0
    for protocol in protocols:
        for type in agentTypes:
            colorKey += 1
            successRates = []
            for A in aRange:
                aMin, aMax, aStart = (A//n)-2, (A//n)+2, (A//n)-1
                bMin, bMax, bStart = (B//n)-2, (A//n)+2, (B//n)-1

                successes = 0
                for trial in range(trials):
                    aDist = alg(A, n=n, minShare=aMin, maxShare=aMax, startShare=aStart)
                    bDist = alg(B, n=n, minShare=bMin, maxShare=bMax, startShare=bStart)
                    P = classes.Profile(
                        [
                            classes.Agent(id = j+1, evidence = {a:aDist[j], b:bDist[j]}, type=type) for j in range(n)
                            ]
                        )
                    D = classes.Deliberation(Profile = P, Protocol = protocol)
                    if D.finalWinners == {a}:
                        successes += 1
                successRates.append(successes/trials)

            if type == 'lazy':
                ax.plot(
                    aRange, 
                    successRates, 
                    color=config.COLOR_DICT[colorKey],
                    linewidth=1.8,
                    marker='.',
                    label='{p}, {t}'.format(p = protocol, t=type)
                    )
    
            if type == 'keen':
                ax.plot(
                    aRange, 
                    successRates, 
                    color=config.COLOR_DICT[colorKey],
                    linewidth=1.7,
                    marker='.',
                    alpha=0.5,
                    label='{p}, {t}'.format(p = protocol, t=type)
                    )
    
    ax.grid(linestyle=':')
    ax.set_xlim(min(aRange)-0.25, max(aRange)+0.5)
    plt.xticks([31] + [i for i in aRange if i%5 == 0])
    plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('$|E(a)|$')
    plt.title('$|E(b)|$ = {B}, n = {n}'.format(B = B, n = n))
    plt.ylabel('Success rate')
    ax.legend()
    plt.savefig('plot1.png', dpi=500)

def varEvidenceDifferentN(trials):
    nRange = range(5, 10)
    A, B = 50, 30
    protocol = 'sim'
    alg = config.PARTITION_ALGS[4]
    gaps = {
        1: {
            a:(1, 1, 0),
            b:(1, 1, 0)
        },
        2: {
            a:(1, 1, 0),
            b:(3, 5, 1)
        }
    }
    fig, ax = plt.subplots()
    for i in gaps.keys():
        successRates = []
        for n in nRange:
            aMin, aMax, aStart = (A//n)-gaps[i][a][0], (A//n)+gaps[i][a][1], (A//n)-gaps[i][a][2]
            bMin, bMax, bStart = (B//n)-gaps[i][b][0], (A//n)+gaps[i][b][1], (B//n)-gaps[i][b][2]

            successes = 0
            for trial in range(trials):
                aDist = alg(A, n=n, minShare=aMin, maxShare=aMax, startShare=aStart)
                bDist = alg(B, n=n, minShare=bMin, maxShare=bMax, startShare=bStart)
                P = classes.Profile(
                    [
                        classes.Agent(id = i+1, evidence = {a:aDist[i], b:bDist[i]}) for i in range(n)
                        ]
                    )
                D = classes.Deliberation(Profile = P, Protocol = protocol)
                if D.finalWinners == {a}:
                    successes += 1
            successRates.append(successes/trials)
        ax.plot(
            nRange, 
            successRates, 
            color=config.COLOR_DICT[i],
            linewidth=2.0,
            marker='.',
            label='$a_i\in[{aMin}, {aMax}], b_i\in[{bMin}, {bMax}]$'.format(
                aMin=(A//n)-gaps[i][a][0], 
                aMax=(A//n)+gaps[i][a][1], 
                bMin=(B//n)-gaps[i][b][0], 
                bMax=(B//n)+gaps[i][b][1]
                )
            )
    
    ax.grid(linestyle=':')
    ax.set_xlim(min(nRange)-0.25, max(nRange)+0.5)
    plt.xticks([i for i in nRange if i%2 == 0])
    plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('$n$')
    plt.title('{p} protocol, A = {A}, B = {B}'.format(p = protocol, A = A, B = B))
    plt.ylabel('Success rate')
    ax.legend()
    plt.savefig('plot2.png', dpi=500)

def varEvidenceConstantN(trials, n, B):
    aRange = range(B, 101)
    protocols = ['sim', 'seq-const']
    alg = config.PARTITION_ALGS[4]
    gaps = {
        1: {
            a:(1, 1, 1),
            b:(1, 1, 1)
        },
        2: {
            a:(1, 1, 1),
            b:(3, 7, 1)
        }
    }
    fig, ax = plt.subplots()
    colorKey = 0
    for protocol in protocols:
        for i in gaps.keys():
            colorKey += 1
            successRates = []
            for A in aRange:
                aMin, aMax, aStart = (A//n)-gaps[i][a][0], (A//n)+gaps[i][a][1], (A//n)-gaps[i][a][2]
                bMin, bMax, bStart = (B//n)-gaps[i][b][0], (A//n)+gaps[i][b][1], (B//n)-gaps[i][b][2]

                successes = 0
                for trial in range(trials):
                    aDist = alg(A, n=n, minShare=aMin, maxShare=aMax, startShare=aStart)
                    bDist = alg(B, n=n, minShare=bMin, maxShare=bMax, startShare=bStart)
                    P = classes.Profile(
                        [
                            classes.Agent(id = i+1, evidence = {a:aDist[i], b:bDist[i]}, type='lazy') for i in range(n)
                            ]
                        )
                    D = classes.Deliberation(Profile = P, Protocol = protocol)
                    if D.finalWinners == {a}:
                        successes += 1
                successRates.append(successes/trials)
            
            if i == 1:
                ax.plot(
                    aRange, 
                    successRates, 
                    color=config.COLOR_DICT[colorKey],
                    marker='.',
                    linewidth=1.8,
                    label='{p}, $a_i$:(-{aMin}, {aMax}), $b_i$:(-{bMin}, {bMax})'.format(
                        p = protocol,
                        aMin=gaps[i][a][0], 
                        aMax=gaps[i][a][1], 
                        bMin=gaps[i][b][0], 
                        bMax=gaps[i][b][1]
                        )
                    )

            if i == 2:
                ax.plot(
                    aRange, 
                    successRates, 
                    color=config.COLOR_DICT[colorKey],
                    marker='.',
                    linewidth=1.5,
                    alpha=0.5,
                    label='{p}, $a_i$:(-{aMin}, {aMax}), $b_i$:(-{bMin}, {bMax})'.format(
                        p = protocol,
                        aMin=gaps[i][a][0], 
                        aMax=gaps[i][a][1], 
                        bMin=gaps[i][b][0], 
                        bMax=gaps[i][b][1]
                        )
                    )

    
    ax.grid(linestyle=':')
    ax.set_xlim(min(aRange)-0.25, max(aRange)+0.5)
    plt.xticks([i for i in aRange if i%5 == 0])
    plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('$|E(a)|$')
    plt.title('$|E(b)|$ = {B}, n = {n}'.format(B = B, n = n))
    plt.ylabel('Success rate')
    ax.legend()
    plt.savefig('plot2.png', dpi=500)

def varRoundsToTermination(trials, n, B):
    aRange = range(B, 101)
    protocols = ['sim', 'seq-const']
    alg = config.PARTITION_ALGS[4]
    gaps = {
        1: {
            a:(1, 1, 1),
            b:(1, 1, 1)
        },
        2: {
            a:(1, 1, 1),
            b:(3, 7, 1)
        }
    }
    fig, ax = plt.subplots()
    colorKey = 0
    for protocol in protocols:
        for i in gaps.keys():
            colorKey += 1
            avgNrRounds = []
            for A in aRange:
                aMin, aMax, aStart = (A//n)-gaps[i][a][0], (A//n)+gaps[i][a][1], (A//n)-gaps[i][a][2]
                bMin, bMax, bStart = (B//n)-gaps[i][b][0], (A//n)+gaps[i][b][1], (B//n)-gaps[i][b][2]

                r = []
                for trial in range(trials):
                    aDist = alg(A, n=n, minShare=aMin, maxShare=aMax, startShare=aStart)
                    bDist = alg(B, n=n, minShare=bMin, maxShare=bMax, startShare=bStart)
                    P = classes.Profile(
                        [
                            classes.Agent(id = i+1, evidence = {a:aDist[i], b:bDist[i]}, type='lazy') for i in range(n)
                            ]
                        )
                    D = classes.Deliberation(Profile = P, Protocol = protocol)
                    r.append(max(D.History.keys()))
                avgNrRounds.append(sum(r)/trials)
            
            if i == 1:
                ax.plot(
                    aRange, 
                    avgNrRounds, 
                    color=config.COLOR_DICT[colorKey],
                    marker='.',
                    linewidth=1.8,
                    label='{p}, $a_i$:(-{aMin}, {aMax}), $b_i$:(-{bMin}, {bMax})'.format(
                        p = protocol,
                        aMin=gaps[i][a][0], 
                        aMax=gaps[i][a][1], 
                        bMin=gaps[i][b][0], 
                        bMax=gaps[i][b][1]
                        )
                    )

            if i == 2:
                ax.plot(
                    aRange, 
                    avgNrRounds,
                    color=config.COLOR_DICT[colorKey],
                    marker='.',
                    linewidth=1.5,
                    alpha=0.5,
                    label='{p}, $a_i$:(-{aMin}, {aMax}), $b_i$:(-{bMin}, {bMax})'.format(
                        p = protocol,
                        aMin=gaps[i][a][0], 
                        aMax=gaps[i][a][1], 
                        bMin=gaps[i][b][0], 
                        bMax=gaps[i][b][1]
                        )
                    )

    
    ax.grid(linestyle=':')
    ax.set_xlim(min(aRange)-0.25, max(aRange)+0.5)
    plt.xticks([i for i in aRange if i%5 == 0])
    # plt.yticks(np.linspace(0, 1, 11))
    plt.xlabel('$|E(a)|$')
    plt.title('$|E(b)|$ = {B}, n = {n}'.format(B = B, n = n))
    plt.ylabel('Average number of rounds')
    ax.legend()
    plt.savefig('plot3.png', dpi=500)