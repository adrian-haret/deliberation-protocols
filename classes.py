from typing import Protocol
import config
from xmlrpc.client import Boolean
import helpers
class Agent:
    def __init__(self, id, evidence = dict(), type = 'keen'):
        """
            Agent types are keen or lazy.

            Indifferent agents are ok with ties, and will not disclose to break a tie. Keen agents will.
        """
        self.id = id # agent id, supposed to be a number

        self.type = type # type is either 'keen' or 'lazy' 
        
        if len(evidence) > 0 and all(isinstance(v, int) for v in evidence.values()):
            self.evidence = helpers.generateEvidenceFromCounts(evidence, self.id) 
            # if evidence given as numbers, converts it to explicit items
        else:
            self.evidence = evidence # assumes evidence given explicitly; if not, should rewrite this
    
    def __str__(self) -> str:
        return helpers.prettyViewAgent(self.id, helpers.evidenceCounts(self))

    def updateEvidence(self, x, EvidenceItems):
        # update step
        if isinstance(EvidenceItems, tuple):
            self.evidence[x] = self.evidence[x] | {EvidenceItems}
        else:
            self.evidence[x] = self.evidence[x] | set(EvidenceItems)

    def preferredTo(self, Outcome) -> set:
        """
            Returns alternatives in the agent's preference order 
            that agent prefers to alternatives in Outcome.

            These are alternatives the agent would be willing to diclose information about
            if provisional winners are alternatives in Outcome: alternatives the agent thinks are 
            at least as good (or better) than the ones in Outcome.
                        
            If agent type is keen the function returns alternatives, if any, that are at least as good
            as all alternatives in Outcome. For instance, for agent with preference a > b > c and 
            Outcome = {a, b}, the function returns a. The upshot is the agent will be willing 
            to disclose information about a and break the tie.

            If agent type is lazy the function returns alternatives, if any, that are 
        """
        if self.type == 'keen':
            if helpers.top(self) == Outcome:
                return set()
            if Outcome < helpers.top(self):
                return helpers.top(self) - Outcome 
            else:
                return {
                    x for x in config.Alternatives if any(helpers.ranks(self)[x] < helpers.ranks(self)[y] for y in Outcome)
                    }

        if self.type == 'lazy':
            minOutcomeRank = min([helpers.ranks(self)[y] for y in Outcome]) if Outcome != set() else 0
            return {x for x in config.Alternatives if helpers.ranks(self)[x] < minOutcomeRank}

    def unhappyWith(self, Outcome) -> Boolean:
        """
            Outcome is something like the outcome under the current preferences. 

            Returns Boolean depending on whether agent is unhappy with current outcome.

            Note that result also depends on agent type (lazy vs keen).
        """
        return self.preferredTo(Outcome) != set()








class Profile:
    def __init__(self, input) -> None:
        self.agentList = input # input assumed to be list of instances of Agent class
        self.agentIds = [Agent.id for Agent in self.agentList]       

    def __getitem__(self, agentID):
        return next(i for i in self.agentList if i.id == agentID)
    
    def __iter__(self):
        return iter(self.agentList)

    def __len__(self):
        return len(self.agentList)

    # def __str__(self) -> str:
    #     s = ''
    #     for i in self.agentList:
    #         s += str(i) + '\n'
    #     return s[:-2]

  
    

                    





class Deliberation:
    def __init__(self, Profile, Protocol='sim') -> None:
        self.Profile = Profile
        self.Protocol = Protocol
        self.History = {
            0: {
                'type': self.Protocol,
                'winners at round start': helpers.pluralityWinners(self.Profile), # winners of profile before update
                'disclosers': dict(), # dictionary of agents who have something to disclose
                'nominations': {i:set() for i in self.Profile}, # dict with what alternatives each agent nominates
                'profile at round end': {i.id:{x:e for x, e in i.evidence.items()} for i in self.Profile},
                'winners at round end': helpers.pluralityWinners(self.Profile) # winners of profile after profile update
            }
        }

        if Protocol == 'sim':
            self.finalWinners = self.simultaneous()
        if Protocol == 'seq-const':
            self.finalWinners = self.sequential()
        
        self.nrRounds = max(self.History.keys())
    
    def __str__(self) -> str:
        return helpers.prettyViewHistory(self.History)
    
    def simultaneous(self, disclosure='one'):
        """
            Disclosure can be 'one' or 'all'.
        """
        publicEvidence = {x:set() for x in config.Alternatives}
        currentWinners = helpers.pluralityWinners(self.Profile)
        round = 0
        iHaveSomethingToShare = helpers.thereIsSomethingToDisclose(self.Profile, currentWinners, publicEvidence)
        
        while iHaveSomethingToShare:
            round +=1 # increment the deliberation round variable
            roundDisclosers = dict()
            nominations = {i:{x for x in helpers.top(i)} for i in self.Profile}

            # first, everyone who has something to say discloses an item of evidence
            # disclosed evidence gets added to a dictionary
            disclosedEvidence = {x:set() for x in config.Alternatives} # evidence disclosed this round
            for i in iHaveSomethingToShare.keys(): # for every agent who has something to say
                if disclosure == 'one':
                    chosenAlternative = sorted(list(iHaveSomethingToShare[i].keys()))[0] # pick an alternative
                    disclosedItem = sorted(list(iHaveSomethingToShare[i][chosenAlternative]))[0] # pick some evidence for that alternative
                    disclosedEvidence[chosenAlternative].add(disclosedItem)
                
                if disclosure == 'all':
                    for x in iHaveSomethingToShare[i].keys():
                        disclosedEvidence[x] = iHaveSomethingToShare[i][x]
                
                roundDisclosers[i] = disclosedEvidence
                    
            # disclosed evidence gets added to the public evidence 
            # every agent updates their evidence sets with the evidence disclosed this round
            for x in disclosedEvidence.keys():
                publicEvidence[x] = publicEvidence[x] | disclosedEvidence[x]

                for i in self.Profile:
                    i.updateEvidence(x, disclosedEvidence[x])

            # update the winners with respect to the updated profile, while remembering initial winners (for history)
            winnersAtRoundStart = {x for x in currentWinners}
            currentWinners = helpers.pluralityWinners(self.Profile)

            # update the history
            self.History[round] = {
                'winners at round start': winnersAtRoundStart, # winners of profile before update
                'disclosers': roundDisclosers, # dictionary of agents who have something to disclose
                'nominations': nominations,
                'profile at round end': {i.id:{x:e for x, e in i.evidence.items()} for i in self.Profile},
                'winners at round end': currentWinners # winners of profile after profile update
                }

            # lastly, recompute the dictionary of agents who have something to say
            iHaveSomethingToShare = helpers.thereIsSomethingToDisclose(self.Profile, currentWinners, publicEvidence)
        
        # update history dictionary with the last step
        self.History[round+1] = {
            'winners at round start': helpers.pluralityWinners(self.Profile),
            'disclosers': dict(), # dictionary of agents who have something to disclose
            'nominations': dict(),
            'profile at round end': {i.id:{x:e for x, e in i.evidence.items()} for i in self.Profile},
            'winners at round end': helpers.pluralityWinners(self.Profile) # winners of profile after profile update
            }

        return self.History[max(self.History.keys())]['winners at round end']

    def sequential(self):
        publicEvidence = {x:set() for x in config.Alternatives}
        round = 0
        disclosureHappened = True
        currentWinners = set() # before any nominations there is no winner

        while disclosureHappened:
            round += 1
            disclosureHappened = False
            winnersAtRoundStart = {x for x in currentWinners} # winners at end of previous round
            nominations = {i:set() for i in self.Profile}
            currentNominees = []
            roundDisclosers = dict()
            for i in self.Profile: # go through every agent
                iHaveSomethingToShare = helpers.thereIsSomethingToDisclose(i, currentWinners, publicEvidence)

                # first find out if agent is unhappy with current outcome and has unreleased evidence             
                if iHaveSomethingToShare: # so, if there is something the agent can disclose
                    # pick an alternative, the first one alphabetically
                    chosenAlternative = sorted(list(iHaveSomethingToShare[i].keys()))[0] 

                    # pick a non-public item of evidence for that alternative
                    disclosedItem = sorted(list(iHaveSomethingToShare[i][chosenAlternative]))[0] 

                    # update the dictionary of agents who disclose this round
                    roundDisclosers[i] = {chosenAlternative:{disclosedItem}}

                    # update public evidence for that alternative (the agent has released that evidence)
                    publicEvidence[chosenAlternative] = publicEvidence[chosenAlternative] | {disclosedItem}

                    # every other agent updates their evidence sets with the released item of evidence
                    for j in self.Profile:
                        if j.id != i.id:
                            j.updateEvidence(chosenAlternative, disclosedItem)
                    
                    # update the variable that keeps track of whether disclosure happened 
                    # (if it doesn't at some round we stop)
                    disclosureHappened = True
                
                # agent decides who to nominate
                iNominees = i.preferredTo(currentWinners) if i.preferredTo(currentWinners) else helpers.top(i)
                nominations[i] = iNominees
                currentNominees += list(iNominees)

                # update currentWinners variable with the plurality winners over currentNominees
                currentScores = {x:currentNominees.count(x) for x in config.Alternatives} 
                currentWinners = {x for x in config.Alternatives if currentScores[x] == max(currentScores.values())}

            # update history dictionary
            self.History[round] = {
                'winners at round start': winnersAtRoundStart,
                'disclosers': roundDisclosers, # dictionary of agents who have something to disclose
                'nominations': nominations,
                'profile at round end': {i.id:{x:e for x, e in i.evidence.items()} for i in self.Profile},
                'winners at round end': helpers.pluralityWinners(self.Profile) # winners of profile after profile update
                }

        return self.History[max(self.History.keys())]['winners at round end']
