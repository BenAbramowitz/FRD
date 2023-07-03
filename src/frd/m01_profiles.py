from typing import Tuple #to type hint tuples

import numpy as np

from . import m00_helper as helper


class Profile():
    def __init__(self, n_voters:int, n_cands:int, n_issues:int, voters_p, cands_p, approval_params:Tuple[int,float]):
        self.n_voters, self.n_cands = n_voters, n_cands
        self.n_issues = n_issues
        self.voters_p, self.cands_p = voters_p, cands_p

        self.v_pref:np.ndarray = None #np.empty((n_voters, n_issues))
        self.c_pref:np.ndarray = None #np.empty((n_cands, n_issues))
        
        self.distances = None #np.empty((n_voters, n_cands))
        self.approval_params = approval_params

        self.approvals = {} #dict of numpy arrays
        self.approval_indicators = {} #dict of numpy arrays
        self.ordermaps = {} #dict of numpy arrays
        self.orders = {} #dict of numpy arrays
        self.agreements = {} #dict of numpy arrays

        self.voter_majority_outcomes = None

    def create_issue_prefs(self):
        self.v_pref = np.random.binomial(1, self.voters_p, size=(self.n_voters, self.n_issues))
        self.c_pref = np.random.binomial(1, self.cands_p, size=(self.n_cands, self.n_issues))
        return self.v_pref, self.c_pref
    
    def voter_majority_vote(self):
        self.voter_majority_outcomes = np.random.binomial(1, 0.5, size=(self.n_issues)) #initialized randomly so unchanged vals break ties randomly
        for i in range(self.n_issues):
            ones = np.sum(self.v_pref[:,i], axis=0)
            if ones > self.n_voters / 2:
                self.voter_majority_outcomes[i] = 1
            elif ones < self.n_voters / 2:
                self.voter_majority_outcomes[i] = 0
        return self.voter_majority_outcomes
        
    def issues_to_distances(self):
        hamming_distances = np.sum(self.v_pref[:, None] != self.c_pref, axis=2)
        self.distances = hamming_distances / self.n_issues
        return self.distances

    def distances_to_approvals(self):
        '''
        Voters report approvals of cands based on distances between their prefs
        Voters will approve only if distance is below a threshold, and a voter can approve at most k cands

        RETURNS
        -----
        self.approvals (dict of 1D np.ndarrays)(voter:binary array): valeus are binary arrays where 
                        approvals[v][c] = 1 iff voter v approves cand c, else 0
                        voter ids are keys of the dict, indices of the value array 

        NOTES
        -----
        self.derivation_params must be a tuple (k, threshold)
        If threshold is 1.0, then voter will approve exactly k cands
        If k >= n_cands, voter will approve all cands whose distance from them is below the threshold
        '''
        if self.distances is None:
            self.issues_to_distances()
        k, threshold = self.approval_params
        approvable = np.asarray(self.distances < threshold)
        for v_id in range(self.n_voters):
            if np.sum(approvable[v_id]) <= k:
                #self.approval_indicators[v_id] = approvable[v_id]
                self.approvals[v_id] = np.nonzero(approvable[v_id])[0]
            else: #voter would approve more than k based on threshold if allowed to
                distances_augmented = helper.array1D_to_sorted(self.distances[v_id], seed=v_id, tiebreakers=None)
                self.approvals[v_id] = distances_augmented[:,2][:k].astype(int)
                #self.approval_indicators[v_id] = np.asarray([1 if c in self.approvals[v_id] else 0 for c in range(self.n_cands)])
        return self.approvals#, self.approval_indicators
    
    def approvals_to_indicators(self):
        if self.approvals == {}:
            self.distances_to_approvals()
        self.approval_indicators = {v_id:helper.subset_to_indicator(self.approvals[v_id], range(self.n_cands)) for v_id in range(self.n_voters)}

    def distances_to_ordinals(self)->Tuple[dict, dict]:
        if self.distances is None:
            self.issues_to_distances()
        return self.distances_to_orders(), self.orders_to_ordermaps()
    
    def distances_to_orders(self)->dict:
        '''
        Voters report approvals of cands based on distances between their prefs

        RETURNS
        -----
        self.orders (dict of 1D np.ndarrays): keys are voter ids, values are ordered lsit of cand ids
        '''
        if self.distances is None:
            self.issues_to_distances()
        self.orders = {v_id:helper.array1D_to_sorted(self.distances[v_id], seed=v_id)[:,2].astype(int) for v_id in range(self.n_voters)}
        return self.orders
    
    def orders_to_ordermaps(self)->dict:
        '''
        RETURNS
        -------
        self.ordermaps (dict of 1D numpy arrays): keys are voters, values are lists of indices
        self.ordermaps[v][c] = 3 means voter v ranks cand v third

        NOTES
        ------
        Can use argsort here with its lexicographic tiebreaking because random tiebreaking is already used to construct the orders

        '''
        if self.orders == {}:
            self.distances_to_orders()
        self.ordermaps = {v_id:np.argsort(self.orders[v_id]) for v_id in range(self.n_voters)}
        return self.ordermaps
    
    def distances_to_agreements(self):
        if self.distances is None:
            self.issues_to_distances()
        self.agreements = {v_id: 1 - self.distances[v_id] for v_id in range(self.n_voters)}
        return self.agreements
    
    def new_instance(self, approvals = True, ordinals = True, agreements = True, seed=None):
        '''
        Creates new profile, distances, and derived election profiles indicated by kwargs.

        NOTES
        -----
        Assumes the profile has already been used so all the relevant params are defined and stay the same
            (n_voters, n_cands, n_issues, voters_p, cands_p, and approval_params).
        This is to save time and memory creating new instances with consistent params without a new Profile object each time
        '''
        if seed is not None:
            np.random.seed(seed)
        self.create_issue_prefs()
        self.issues_to_distances()
        self.voter_majority_vote()
        if approvals: 
            self.distances_to_approvals()
            self.approvals_to_indicators()
        if ordinals:
            self.distances_to_ordinals()
        if agreements:
            self.distances_to_agreements()
        return vars(self)


    ## Setters

    def set_ordermaps(self, ordermaps):
        self.ordermaps = ordermaps

    def set_agreements(self, agreements):
        self.agreements = agreements

    def set_issue_prefs(self, v_pref, c_pref):
        self.v_pref = v_pref
        self.c_pref = c_pref
        return self.v_pref, self.c_pref
    
    def set_approval_params(self, k, threshold):
        self.approval_params = (k, threshold)
        self.approvals, self.approval_indicators = {}, {} #reset
    
    def set_approvals(self, approvals:dict):
        self.approvals = approvals

    def set_orders(self, orders):
        self.orders = orders

    ##Getters

    def get_n_cands(self):
        return self.n_cands
    
    def get_n_voters(self):
        return self.n_voters
    
    def get_n_issues(self):
        return self.n_issues
    
    def get_approval_params(self):
        return self.approval_params

    def get_issue_prefs(self):
        return self.v_pref, self.c_pref

    def get_approvals(self):
        return self.approvals

    def get_orders(self):
        return self.orders

    def get_distances(self):
        return self.distances

    def get_agreements(self):
        return self.agreements
    
    def get_voter_majority(self):
        return self.voter_majority_outcomes

#Quick Tests
# if __name__ == '__main__':
#     import m00_helper as helper

#     N_VOTERS = 1
#     N_CANDS = 5
#     N_ISSUES = 3
#     VOTERS_P = 0.5
#     CANDS_P = 0.5
#     APPROVAL_PARAMS = (2, 0.5)
#     SEED = 2

#     np.random.seed(SEED)
#     profile = Profile(N_VOTERS, N_CANDS, N_ISSUES, VOTERS_P, CANDS_P, APPROVAL_PARAMS)
#     profile.create_issue_prefs()
#     profile.issues_to_distances()
#     profile.distances_to_approvals()
#     profile.distances_to_ordinals()
#     profile.distances_to_agreements()
#     print(vars(profile))
#     print('\n\n\n')
#     profile.new_instance(seed=SEED+1)
#     vars(profile)