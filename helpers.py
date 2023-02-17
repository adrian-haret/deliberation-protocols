import config
import classes

import random
import scipy.stats as ss
import numpy as np
import matplotlib.pyplot as plt

def generateEvidenceFromCounts(evidence, agentId) -> dict:
    """
        Returns a dictionary of individual evidence items generated according to the numbers
        in the evidence variable. The individual items are indexed by agentId.

        For instance, evidence = {a:2, b:0, c:1}, agentId = 3 becomes:

        {
            a:{(3,1), (3,2)}, 
            b:{},
            c:{(3,1)}
            }
    """
    return {x: {(agentId, i+1) for i in range(evidence[x])} for x in config.Alternatives}

def evidenceCounts(Agent) -> dict:
    """
        Returns a dictionary of the evidence amounts for each alternative, for Agent.
    """
    return {x:len(Agent.evidence[x]) for x in config.Alternatives}

def ranks(Agent) -> dict:
    """
        Returns dictionary where each alternative is assigned a number: 
        its rank in the agents' preference order. The preference order 
        is determined by the amount of evidence for each alternative:
        more evidence for x than for y means x preferred to y.

        Lower rank means better. Ranks start at 1.

        For instance {a:1, b:1, c:2, d:3} encodes the order a ~ b > c > d.
    """
    values = sorted(list(set(evidenceCounts(Agent).values())))[::-1]
    return {x:values.index(evidenceCounts(Agent)[x])+1 for x in config.Alternatives}

def top(Agent) -> set:
    """
        Returns the top alternatives (i.e., those supported by most evidence) of Agent.
    """
    return {x for x in config.Alternatives if ranks(Agent)[x] == min(ranks(Agent).values())}

def mostFrequent(List):
    """
        Returns set of elements of List that appear most often in List.
    """
    counts = {x:List.count(x) for x in set(List)}
    return {x for x in counts.keys() if counts[x] == max(counts.values())}

def pluralityScores(Profile) -> dict:
    """
        Returns dictionary of plurality scores (i.e., number of times an alternative shows up on top)
        for each alternative.
    """
    return {x: sum(map(lambda i: x in top(i), [i for i in Profile])) for x in config.Alternatives}

def pluralityWinners(Profile) -> set:
    """
        Returns alternatives that are plurality winners in the given profile, 
        i.e., that show up most often on top.
    """
    pScores = pluralityScores(Profile)
    return {x for x in config.Alternatives if pScores[x] == max(pScores.values())}

def unhappyAgents(Profile) -> set:
    """
        Returns alternatives that are unhappy with the plurality winners of given profile,
        i.e., that have some alternative they prefer to the plurality winners.
    """
    return {i for i in Profile if i.unhappyWith(pluralityWinners(Profile))}

def thereIsSomethingToDisclose(Input, Outcome, PublicEvidence) -> dict():
    """
        Input should be either an Agent type or Profile type.

        Returns dictionary where keys are agents that have something to disclose.
        Values are dictionaries whose keys are alternatives the agent prefers to Outcome, 
        and values are items of evidence that the agent possesses in facor of those 
        alternatives and that are not already public.
    """
    if Outcome == set():
        return dict()
        
    if isinstance(Input, classes.Agent):
        Agent = Input
        betterAlternatives = Agent.preferredTo(Outcome)
        if betterAlternatives:
            if any(x for x in betterAlternatives if any(e for e in Agent.evidence[x] if e not in PublicEvidence[x])):
                return {
                    Agent: {
                        x: {
                            e for e in Agent.evidence[x] if e not in PublicEvidence[x]
                            } for x in betterAlternatives if {e for e in Agent.evidence[x] if e not in PublicEvidence[x]}
                        }
                    }
        return dict()

    if isinstance(Input, classes.Profile):
        Profile = Input
        return {
            i:thereIsSomethingToDisclose(i, Outcome, PublicEvidence)[i] for i in Profile if thereIsSomethingToDisclose(i, Outcome, PublicEvidence)
            }
    
    return None

def prettyViewAgent(AgentId, EvidenceCountDict):
    """
        Prints agent i as a list of alternatives with the amount of evidence supporting them:

        i: ---a   [3]
            ----b [4]
            --c   [2]

        The numbers in parantheses stand for amount of evidence for the respective alternative.
    """
    rowLength = 50
    prefix = '0{id}: '.format(id = AgentId) if AgentId < 10 else '{id}: '.format(id = AgentId)

    x = config.Alternatives[0]
    s = prefix + '-'* EvidenceCountDict[x] + str(x)
    s += ' '*(rowLength - len(s)) + '[{e}]'.format(e = EvidenceCountDict[x]) + '\n'

    for i in range(1, len(config.Alternatives)):
        x = config.Alternatives[i]
        evidenceBlock = '-'* EvidenceCountDict[x] + str(x) 
        currentLength = len(prefix) + len(evidenceBlock)
        row = ' '*len(prefix) + evidenceBlock + ' '*(rowLength - currentLength) + '[{e}]'.format(e = EvidenceCountDict[x]) + '\n'
        s += row
    return s

def prettyViewHistory(history):
    s = '{type} protocol\n\n'.format(type = history[0]['type'])

    if history[0]['type'] == 'seq-const':
        for r in history.keys():
            s += '\tRound {round}\n'.format(round = r)
            if r == 0:
                s += 'Initial profile:\n\n'
                for i in history[r]['profile at round end'].keys():
                    s += prettyViewAgent(i, {x: len(history[r]['profile at round end'][i][x]) for x in config.Alternatives}) +'\n'

            if r > 0:
                nominees = []
                for i in history[r]['nominations'].keys():
                    S = sorted(list(history[r]['nominations'][i]))
                    nominees += S

                    if i in history[r]['disclosers'].keys():
                        s += 'Agent {i} nominates {S}, discloses for {x}.\n\t\t\t\tWinning: {W}\n'.format(
                            i = i.id, 
                            S = ', '.join(S), 
                            x = list(history[r]['disclosers'][i].keys())[0],
                            W = ', '.join(sorted(mostFrequent(nominees)))
                        )
                    else:
                        s+= "Agent {i} nominates {S}.\n\t\t\t\tWinning: {W}\n".format(
                            i=i.id, 
                            S = ', '.join(S), 
                            W = ', '.join(sorted(mostFrequent(nominees)))
                            )
                s += '\nEnd of round winners: {W}.\n'.format(
                    W = ', '.join(sorted(mostFrequent(nominees)))
                ) 
                
                if len(history[r]['disclosers'].keys()) > 0:
                    s+= '\nProfile after updates:\n\n'
                    for i in history[r]['profile at round end'].keys():
                        s += prettyViewAgent(i, {x: len(history[r]['profile at round end'][i][x]) for x in config.Alternatives}) +'\n' 
                else:    
                    s += 'No unhappy agents that have something to disclose. We stop.\n'
                    s += 'Final winners: {w}.'.format(
                        w = ','.join(history[max(history.keys())]['winners at round end'])
                    )
    
    if history[0]['type'] == 'sim':
        for r in history.keys():
            s += '\tRound {round}\n'.format(round = r)
            if r == 0:
                s += 'Initial profile:\n\n'
                for i in history[r]['profile at round end'].keys():
                    s += prettyViewAgent(i, {x: len(history[r]['profile at round end'][i][x]) for x in config.Alternatives}) +'\n'

            if r > 0:
                s += 'Current winners: {W}\n\n'.format(
                    W = ', '.join(history[r]['winners at round start'])
                    )
                for i in history[r]['nominations'].keys():
                    if i in history[r]['disclosers'].keys():
                        s += 'Agent {i} discloses for {x}.\n'.format(
                            i = i.id, 
                            x = list(history[r]['disclosers'][i].keys())[0]
                        )
                
                if len(history[r]['disclosers'].keys()) > 0:
                    s+= '\nProfile after updates:\n\n'
                    for i in history[r]['profile at round end'].keys():
                        s += prettyViewAgent(i, {x: len(history[r]['profile at round end'][i][x]) for x in config.Alternatives}) +'\n' 
                else:    
                    s += 'No unhappy agents that have something to disclose. We stop.\n'
                    s += 'Final winners: {w}.'.format(
                        w = ','.join(history[max(history.keys())]['winners at round end'])
                    )        

    return s

def writeHistoryToFile(history):
    filename = '{type}_deliberation_history.txt'.format(type = history[0]['type'])

    with open(filename, 'w') as f:
        f.write(prettyViewHistory(history))

def partitions(n, E, parent=tuple()):
    """
        n, number of agents
        E, amount of evidence to be divided among the n agents

        produces all permutations
    """
    if n > 1:
        for i in range(E + 1):
            for x in partitions(n - 1, i, parent + (E - i,)):
                yield x
    else:
        yield parent + (E,)

def varPartitions(n, E, desiredVariance = 'low'):
    maxVar = np.var([E] + [0]*(n-1))
    cut1, cut2 = maxVar/8, (2/3)*maxVar
    for p in partitions(n, E):
        v = np.var(p)
        if desiredVariance == 'low' and np.var(p)<= cut1:
            yield p
        if desiredVariance == 'high' and np.var(p) >= cut2:
            yield p

def randomSlicing(S, n, minShare, maxShare, startShare=0):
    """
        Returns a list of n random integers in the interval [minShare, maxShare] with sum S.

        The procedure works by iteratively selecting a random number s in [minShare, maxShare]
        and subtracting the chosen number from S (slicing off, as it were, a portion of size s).

        When the remaining amount of evidence is insufficient 
        (less than maxShare or minShare), the procedure selects slices out of the remaining amount 
        of evidence.
    """
    if n*minShare > S or n*maxShare < S:
        return None
    
    d = [0]*n
    for i in range(n-1):
        if S >= maxShare:
            d[i] = random.randint(minShare, maxShare)
        if minShare < S < maxShare:
            d[i] = random.randint(minShare, S)
        if S <= minShare:
            d[i] = random.randint(0, S)
        S -= d[i]
    d[n-1] = S
    return d

def randomConstrained(S, n, minShare, maxShare, startShare=0):
    """
        Returns a list of n random integers in the interval [minShare, maxShare] with sum S.
    """

    hit = False
    while not hit:
        total, count = 0, 0
        nums = []
        while total < S and count < n:
            r = random.randint(minShare, maxShare)
            total += r
            count += 1
            nums.append(r)

        if total == S and count == n: 
            hit = True
    return nums

def randomIncrement(S, n, minShare, maxShare, startShare=0):
    """
        Returns a list of n random integers in the interval 
        [minShare, maxShare] that add up to S.

        The algorithm initializes all values to minShare, then randomly selects 
        one value and increments it by 1, provided the value does not exceed maxShare.
    """
    if n*minShare > S or n*maxShare < S:
        return None

    d = [minShare]*n
    while sum(d) < S:
        i = random.choice(range(n))
        if d[i] < maxShare:
            d[i] += 1
        
    return d

def randomDeviate(S, n, minShare, maxShare, startShare):
    """
        Returns a list of n random integers that add up to S.

        The algorithm initializes all values to startShare, then randomly selects
        one value and randomly increments/decrements it by 1, provided the deviation 
        from startShare does not exceed maxDownDev on the lower side, and maxUpDev on 
        the upper side.
    """
    minShare, maxShare, startShare = max(minShare, 0), min(maxShare, S), max(startShare, 0)

    if startShare*n > S or maxShare*n < S or minShare*n > S:
        return None 

    d = [startShare]*n
    while sum(d) < S:
        i = random.choice(range(n))
        x = random.choice([-1, 1])

        if minShare <= d[i] + x <= maxShare:
            d[i] += x
    return d