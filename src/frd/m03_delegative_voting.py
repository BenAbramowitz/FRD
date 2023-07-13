import numpy as np
import copy
import logging

from . import m00_helper as helper
from . import m01_profiles as profiles
from . import m02_election_rules as rules

def majority(binary_matrix)->np.ndarray:
    '''
    Majority voting (unweighted) over many binary issues , where rows are agents and columns are issues

    RETURNS
    -------
    outcomes (np.ndarray): 1D array of len n_issues
    '''
    n_agents, n_issues = binary_matrix.shape[0], binary_matrix.shape[1]
    vote_sums = np.sum(binary_matrix, axis=0)
    outcomes = [1 if vote_sums[i] > n_agents/2.0
                else 0 if vote_sums[i] < n_agents/2.0
                else np.random.binomial(1, 0.5) for i in range(n_issues)]
    return np.array(outcomes)

def weighted_majority(binary_matrix:np.ndarray, weights)->np.ndarray:
    '''
    Implemented weighted majority voting where preferences are binary and weights are non-negative

    PARAMS
    -------
    binary_matrix (np.ndarray): Size n_agents x n_issues, cell values are {0,1}
    weights: 1D array of len n_agents (binary_matrix.shape[0]) with non-negative weights

    RETURNS
    --------
    outcomes (np.ndarray): binary array of len n_issues
    '''
    n_issues = binary_matrix.shape[1]
    weighted_profile = (binary_matrix.T * weights).T

    vote_sums = np.sum(weighted_profile, axis=0)
    weight_sum = np.sum(weights, axis=0, dtype=float)
    outcomes = [1 if vote_sums[i] > weight_sum/2.0 
                else 0 if vote_sums[i] < weight_sum/2.0 
                else np.random.binomial(1, 0.5) for i in range(n_issues)]
    return np.array(outcomes)

class RD():
    '''
    Elect reps, apply default weighting, take (weighted) majority vote, then compare to voter majority outcomes
    '''
    def __init__(self, profile:profiles.Profile, election_rule:str, n_reps:int, default:str) -> None:
        self.profile = profile
        self.election_rule = rules.rule_dispatcher(election_rule)
        self.n_reps = n_reps
        self.n_cands = self.profile.get_n_cands()
        self.rep_ids = []
        self.delegator_ids = []
        self.rep_prefs = None
        self.default = default
        self.cand_election_scores = None
        self.voter_majority_outcomes = profile.get_voter_majority()

    def elect_reps(self):
        '''
        Elect a subset of n_reps cands as reps (or 'winners')

        RETURNS
        --------
        rep_ids (list, 1D): The integer ids of cands who get elected
        cand_election_scores (np.ndarray, 1D): The scores assigned to all cands during the election process (can be used as default weighting by RD/FRD)
        rep_prefs (np.ndarray, 2D): 
        '''
        if self.election_rule is None:
            raise ValueError('Election rule is currently None, func elect_reps cannot elect reps')
        elif self.election_rule == rules.random_winners:
            self.rep_ids, self.cand_election_scores = self.election_rule(range(self.n_cands), self.n_reps)
        else:
            self.rep_ids, self.cand_election_scores = self.election_rule(self.profile, self.n_reps)
        return self.rep_ids, self.cand_election_scores, self.rep_prefs
    
    def pull_rep_prefs(self)->np.ndarray:
        '''
        use rep ids to extract sub-array of rep prefs from the larger array of cand prefs
        '''
        c_prefs = self.profile.get_issue_prefs()[1]
        self.rep_prefs = c_prefs[self.rep_ids,:]
        return self.rep_prefs

    def outcome_agreement(self)->float:
        '''
        Apply the default weighting (param), then run weighted majority voting on rep prefs (not cand prefs).
        Once the vector of n_issues binary outcomes is determined its Hamming distance to the voter majority outcome vector is computed.
        agreement = fraction of issues on which the outcome is the same = 1 - (normalized Hamming distance)
        '''
        if self.default == 'uniform':
            logging.debug(f'RD with uniform default, no delegation. Using majority voting to get rep outcomes')
            rep_outcomes = majority(self.rep_prefs)
        elif self.default == 'election_scores':
                #Give reps their election scores and all other cands zero, then take weighted_majority vote
                logging.debug(f'RD with election scores default, no delegation. Using weighted majority voting to get rep outcomes')
                rep_weights = [self.cand_election_scores[c] if c in self.rep_ids else 0 for c in range(self.n_cands)]
                rep_outcomes = weighted_majority(self.rep_prefs, rep_weights)
        else:
            raise ValueError(f'Default weighting not implemented: {self.default}')

        agreement = np.count_nonzero(rep_outcomes == self.voter_majority_outcomes) / len(rep_outcomes)
        return float(agreement)
    
    def run_RD(self, quick=False)->float:
        logging.debug(f'run_RD running with quick set to {quick}')
        if quick == False:
            self.elect_reps()
            self.pull_rep_prefs()
        return self.outcome_agreement()

    ### Setters

    def set_election_rule(self, rule:str):
        self.election_rule = rules.rule_dispatcher(rule)

    def set_n_reps(self, n_reps):
        self.n_reps = n_reps

    def set_default(self, default):
        self.default = default

    ### Getters

    def get_election_rule(self):
        return self.election_rule

    def get_profile(self):
        return self.profile

    def get_n_reps(self):
        return self.n_reps

    def get_default(self):
        return self.default
    
    def get_rep_ids(self):
        return self.rep_ids


class FRD():
    '''

    '''
    def __init__(self, profile:profiles.Profile, election_rule, n_reps, del_style, best_k, n_delegators, default='uniform') -> None:
        self.profile = profile
        self.n_voters, self.n_cands = profile.get_n_voters(), profile.get_n_cands()
        self.n_issues = profile.get_n_issues()
        self.n_reps = n_reps
        self.default=default
        self.del_style = del_style
        self.best_k = best_k
        self.n_delegators = n_delegators
        self.delegator_ids = []
        self.election_rule = rules.rule_dispatcher(election_rule)
        self.rep_ids = []
        self.weighting = {i:np.zeros((self.n_voters, self.n_cands)) for i in range(self.n_issues)}
        self.rep_weights = {i:np.zeros(self.n_cands) for i in range(self.n_issues)}
        self.voter_majority_outcomes = self.profile.get_voter_majority()

    def elect_reps(self):
        if self.election_rule == rules.random_winners:
            self.rep_ids, self.cand_election_scores = self.election_rule(range(self.n_cands), self.n_reps)
        else:
            self.rep_ids, self.cand_election_scores = self.election_rule(self.profile, self.n_reps)
        return self.rep_ids, self.cand_election_scores

    # def pull_rep_prefs(self):
    #     c_prefs = self.profile.get_issue_prefs()[1]
    #     self.rep_prefs = c_prefs[self.rep_ids,:]
    #     return self.rep_prefs

    def default_weighting(self):
        '''
        Set default weight given by each voter to each rep on each issue

        TO DO
        ------
        Implement election scores as default
        
        '''
        if self.default == 'uniform':
            for i in range(self.n_issues):
                for v in range(self.n_voters):
                    self.weighting[i][v] = [1/self.n_reps if c in self.rep_ids else 0 for c in range(self.n_cands)]
        else:
            raise ValueError(f'Default {self.default} not implemented for FRD')

    def select_n_delegators(self):
        '''
        Select n random delegators to be the ones who delegate on every issue.
        
        NOTE
        ----
        Assumes it is the same n voters delegating on every issue.
        '''
        self.delegator_ids = np.random.choice(self.n_voters, self.n_delegators, replace=False)
        return self.delegator_ids

    def incisive_delegation(self):
        '''
        If a voter is a delegator they give weight 1 to a rep who agrees with them on each issue and 0 to the rest.
        Weighting is issue-specific.
        If there is no rep who agrees with them on some issue (so reps are unanimous and voter disagrees), they stick with default

        '''
        v_prefs, c_prefs = self.profile.get_issue_prefs()
        self.select_n_delegators()
        # print(f'delegators: {self.delegator_ids}')
        for i in range(self.n_issues):
            r0 = np.where(c_prefs[:,i] == 0)[0].tolist() #rep who votes 0 on this issue
            r1 = np.where(c_prefs[:,i] == 1)[0].tolist() #rep who votes 1 on this issue
            for v in self.delegator_ids:
                if r0 and v_prefs[v,i] == 0:
                     self.weighting[i][v] = np.zeros(self.n_cands)
                     self.weighting[i][v,r0[0]] = 1
                elif r1 and v_prefs[v,i] == 1:
                    self.weighting[i][v] = np.zeros(self.n_cands)
                    self.weighting[i][v,r1[0]] = 1
        #print(f'Incisive weighting: {self.weighting}')
        return self.weighting
    
    def find_best_k(self):
        self.select_n_delegators()
        orders = self.profile.get_orders()
        best_ks = {v:[] for v in range(self.n_voters)}
        for v in self.delegator_ids:
            for c in orders[v]:
                if c in self.rep_ids:
                    best_ks[v].append([c])
                    if len(best_ks[v]) == self.best_k:
                        break
        return best_ks
    
    def best_k_delegation(self):
        #use the top k reps from each voter to create delegations
        best_k = self.find_best_k()
        for v in self.delegator_ids:
            for r in best_k[v]:
                for i in range(self.n_issues):
                    self.weighting[i][v,r] = 1.0/len(best_k[v])
        return self.weighting
    
    def weight_reps(self):
        self.default_weighting()
        self.select_n_delegators()
        if self.del_style == 'best_k':
            self.best_k_delegation()
        elif self.del_style == 'incisive':
            self.incisive_delegation()
        self.rep_weights= {i:np.sum(self.weighting[i],axis=0) for i in range(self.n_issues)}
        #print(f'weighting: {self.weighting}')
        #print(f'rep_weights: {self.rep_weights}')
        return self.rep_weights
    
    def weighted_majority(self):
        '''
        Computes weighted majority vote on each issue, where rep weights can be different for each issue
        '''

        outcomes = []
        for i in range(self.n_issues):
            #print(f'\nissue: {i}')
            rep_weights  = self.rep_weights[i]
            #print(f'rep weights after delegation: ', rep_weights)
            c_prefs = self.profile.get_issue_prefs()[1]
            #print(f'cand prefs: {c_prefs[:,i]}')
            #print(f'voter prefs: {self.profile.get_issue_prefs()[0][:,i]}')

            weighted_profile = (c_prefs.T * rep_weights).T
            #print(f'weighted profile: {weighted_profile[:,i]}')

            vote_sum = np.sum(weighted_profile[:,i])
            weight_sum = np.sum(rep_weights, dtype=float)
            outcomes+=[1 if vote_sum > weight_sum/2.0 
                        else 0 if vote_sum < weight_sum/2.0 
                        else np.random.binomial(1, 0.5)]
        return outcomes

    def outcome_agreement(self):
        rep_outcomes = self.weighted_majority()
        #print(f'rep_outcomes: {rep_outcomes}')
        if len(rep_outcomes) != self.n_issues: raise Exception('Num outcomes must be same as number of issues')
        agreement = np.count_nonzero(rep_outcomes == self.voter_majority_outcomes) / self.n_issues
        #print(f'agreement: {agreement}')
        return agreement
    
    def set_delegation_params(self, default, del_style, best_k, n_delegators):
        self.default = default
        self.del_style = del_style
        self.best_k = best_k
        self.n_delegators = n_delegators

    def set_rep_ids(self, rep_ids):
        self.rep_ids = rep_ids


    def run_FRD(self, quick=False):
        if quick == False:
            self.elect_reps()
        self.weight_reps()
        agreement = self.outcome_agreement()
        return agreement