from typing import Tuple #to type hint tuples
import logging

import numpy as np
import whalrus

from . import helper as helper

class Profile():
    def __init__(self, n_voters:int, n_cands:int, n_issues:int, voters_p, cands_p, app_k, app_thresh):
        self.n_voters, self.n_cands = n_voters, n_cands
        self.n_issues = n_issues
        self.voters_p, self.cands_p = voters_p, cands_p

        self.v_intensities:np.ndarray = None #1D array
        self.v_pref:np.ndarray = None #np.empty((n_voters, n_issues))
        self.c_pref:np.ndarray = None #np.empty((n_cands, n_issues))
        
        self.distances = None #np.empty((n_voters, n_cands))
        self.app_k:int = app_k #voters can approve at most app_k cands
        self.app_thresh:float = app_thresh #voters only approve of cand if dist between them is strictly below app_thresh

        self.approvals = {} #dict of numpy arrays
        self.approval_indicators = {} #dict of numpy arrays
        # self.ordermaps = {} #dict of numpy arrays
        self.orders = {} #dict of numpy arrays
        self.whalrus_orders = None #whalrus Profile object made from orders
        self.agreements = {} #dict of numpy arrays
        

        self.voter_majority_outcomes = None

    def create_issue_prefs(self, intensity_dist)->Tuple[np.ndarray, np.ndarray]:
        '''
        Create voter and cand prefs over issues and reset any values that were derived from voter/cands prefs 
        (e.g. distances, voter majority, and election profiles)

        RETURNS
        -------
        v_pref (np.ndarray)(n_voters x n_issues): 2D binary numpy array of voter prefs over issues drawn from Bernoulli with param voters_p
        c_pref (np.ndarray)(n_cands x n_issues): 2D binary numpy array of cand prefs over issues drawn from Bernoulli with param cands_p

        NOTES
        -------
        Since a single profile object may be used many times instead of creating a new profile in each instance, this method can be used to generate new issue prefs
        with the same parameters, and resets any values based on the issue prefs to prevent mismatch

        For normally distributed intensities the mean is 0.5 and variance is 1.
        '''

        if intensity_dist is None and self.voters_p is not None:
            self.v_pref = np.random.binomial(1, self.voters_p, size=(self.n_voters, self.n_issues))
        elif intensity_dist is not None:
            if intensity_dist == 'uniform':
                logging.debug('Generating prefs from uniformly distributed intensities')
                self.v_intensities = np.random.uniform(low=0, high=1, size=(self.n_voters,))
            elif intensity_dist == 'normal':
                logging.debug('Generating prefs from normally distributed intensities with mean 0.5 and variance 1')
                self.v_intensities = np.random.normal(0.5, 1, self.n_voters)
            else:
                raise ValueError(f'Intensity dist not available: {intensity_dist}')
            self.v_pref = np.empty((self.n_voters, self.n_issues))
            for v in range(self.n_voters):
                self.v_pref[v] = np.random.binomial(1, self.v_intensities[v], size=(self.n_issues))
            self.v_pref = np.round(self.v_pref)
        self.c_pref = np.random.binomial(1, self.cands_p, size=(self.n_cands, self.n_issues))
        self.reset_derivatives()
        return self.v_pref, self.c_pref
    
    def reset_derivatives(self)->None:
        '''
        Reset all voters derived from issue prefs to be empty/None
        '''
        self.distances = None #np.empty((n_voters, n_cands))
        self.approvals = {} #dict of numpy arrays
        self.approval_indicators = {} #dict of numpy arrays
        # self.ordermaps = {} #dict of numpy arrays
        self.orders = {} #dict of numpy arrays
        self.agreements = {} #dict of numpy arrays
        self.voter_majority_outcomes = None #numpy array of len n_issues
    
    def voter_majority_vote(self)->np.ndarray:
        '''
        Compute the (unweighted) voter majority on every issue with random tiebreaking
        Tiebreaking only occurs if n_voters is even

        TODO
        ------
        Speed up by removing for loop and just using array operations
        '''
        self.voter_majority_outcomes = np.random.binomial(1, 0.5, size=(self.n_issues)) #initialized randomly so unchanged vals break ties randomly
        for i in range(self.n_issues):
            ones = np.sum(self.v_pref[:,i], axis=0)
            if ones > self.n_voters / 2:
                self.voter_majority_outcomes[i] = 1
            elif ones < self.n_voters / 2:
                self.voter_majority_outcomes[i] = 0
        return self.voter_majority_outcomes
        
    def issues_to_distances(self)->np.ndarray:
        '''
        Compute normalized pairwise Hamming distances between every voter-cand pair based on their issue prefs
        Distance of 0 means cand and voter have identical prefs over issues, 1 means exact opposite
        Distance is equal to the fraction of issues the voter and cand disagree on

        RETURNS
        -------
        distances (np.ndarray): 2D numpy array, size n_voters x n_cands containing floats in [0.0,1.0]
        '''
        hamming_distances = np.sum(self.v_pref[:, None] != self.c_pref, axis=2)
        self.distances = hamming_distances / self.n_issues
        return self.distances

    def distances_to_approvals(self):
        '''
        Voters report approvals of cands based on distances between their prefs
        Voters will approve only if distance is below a threshold, and a voter can approve at most k cands
        If more than k cands have distances below the threshold, then the voter approves of those with lowest distances, breaking ties randomly

        RETURNS
        -----
        self.approvals (dict of 1D np.ndarrays)(voter:binary array): valeus are binary arrays where 
                        approvals[v][c] = 1 iff voter v approves cand c, else 0
                        voter ids are keys of the dict, indices of the value array 

        NOTES
        -----
        If threshold is 1.0, then voter will approve exactly k cands.
        If k >= n_cands, voter will approve all cands whose distance from them is below the threshold
        If threshold = 0 or k = 0, voter will not approve any cands

        '''
        if self.distances is None:
            self.issues_to_distances()
        approvable = np.asarray(self.distances < self.app_thresh)
        for v_id in range(self.n_voters):
            if np.sum(approvable[v_id]) <= self.app_k:
                #self.approval_indicators[v_id] = approvable[v_id]
                self.approvals[v_id] = np.nonzero(approvable[v_id])[0]
            else: #voter would approve more than k based on threshold if allowed to
                distances_augmented = helper.array1D_to_sorted(self.distances[v_id], seed=None, tiebreakers=None)
                self.approvals[v_id] = distances_augmented[:,2][:self.app_k].astype(int)
                #self.approval_indicators[v_id] = np.asarray([1 if c in self.approvals[v_id] else 0 for c in range(self.n_cands)])
        return self.approvals#, self.approval_indicators
    
    def approvals_to_indicators(self)->dict:
        '''
        Takes voters' approvals, which are arrays of integer cand ids, and turns them into indicator arrays where 1 at index means they approve cand with index=cand id
        '''
        if self.approvals == {}:
            self.distances_to_approvals()
        self.approval_indicators = {v_id:helper.subset_to_indicator(self.approvals[v_id], range(self.n_cands)) for v_id in range(self.n_voters)}
        return self.approval_indicators
    
    def distances_to_orders(self)->dict:
        '''
        Voters report approvals of cands based on distances between their prefs

        RETURNS
        -----
        self.orders (dict of 1D np.ndarrays): keys are voter ids, each value is ordered list of cand ids of len n_cands
        self.ordermaps[v][3] = c means voter v ranks cand c in 4th place
        '''
        if self.distances is None:
            self.issues_to_distances()
        self.orders = {v_id:helper.array1D_to_sorted(self.distances[v_id], seed=None)[:,2].astype(int) for v_id in range(self.n_voters)}
        return self.orders
    
    # def orders_to_ordermaps(self)->dict:
    #     '''
    #     RETURNS
    #     -------
    #     self.ordermaps (dict of 1D numpy arrays): keys are voters, values are lists of indices of len n_cands
    #     self.ordermaps[v][c] = 3 means voter v ranks cand c in 4th place

    #     NOTES
    #     ------
    #     Can use argsort here with its lexicographic tiebreaking because random tiebreaking is already used to construct the orders

    #     '''
    #     if self.orders == {}:
    #         self.distances_to_orders()
    #     self.ordermaps = {v_id:np.argsort(self.orders[v_id]) for v_id in range(self.n_voters)}
    #     return self.ordermaps
    
    def orders_to_whalrus(self):
        if self.orders == {}:
            self.distances_to_orders()
        self.whalrus_orders = whalrus.Profile([whalrus.BallotOrder(self.orders[v].tolist()) for v in range(self.n_voters)])
        return self.whalrus_orders

    
    def distances_to_agreements(self):
        if self.distances is None:
            self.issues_to_distances()
        self.agreements = {v_id: 1 - self.distances[v_id] for v_id in range(self.n_voters)}
        return self.agreements
    
    def new_instance(self, intensity_dist=None, approvals = True, ordinals = True, agreements = True, whalrus_orders=True):
        '''
        Creates new profile, distances, and derived election profiles indicated by kwargs.

        NOTES
        -----
        Assumes the profile has already been used so all the relevant params are defined and stay the same
            (n_voters, n_cands, n_issues, voters_p, cands_p, and approval_params).
        This is to save time and memory creating new instances with consistent params without a new Profile object each time
        '''
        self.create_issue_prefs(intensity_dist) #automatically resets all derivatives from issue prefs
        self.issues_to_distances()
        self.voter_majority_vote()
        if approvals: 
            self.distances_to_approvals() #used for max_approval
            logging.debug('created approvals')
            self.approvals_to_indicators() #used for rav
            logging.debug('created approval indicators')
        if ordinals:
            self.distances_to_orders() #used for scoring rules, e.g. Borda and Plurality
            logging.debug('created pref orders')
            # self.orders_to_ordermaps()
            if whalrus_orders:
                self.orders_to_whalrus()
                logging.debug('created whalrus orders')
        if agreements:
            self.distances_to_agreements() #used for max_agreement
            logging.debug('created agreement prefs for election (1- distances)')
        return vars(self)


    ## Setters

    # def set_ordermaps(self, ordermaps):
    #     self.ordermaps = ordermaps

    def set_agreements(self, agreements):
        self.agreements = agreements

    def set_issue_prefs(self, v_pref, c_pref):
        self.v_pref = v_pref
        self.c_pref = c_pref
        self.reset_derivatives()
        return self.v_pref, self.c_pref
    
    def set_approval_params(self, k, threshold):
        self.app_k, self.app_thresh = k, threshold
        self.approvals, self.approval_indicators = {}, {} #reset
    
    def set_approvals(self, approvals:dict):
        self.approvals = approvals

    def set_orders(self, orders):
        self.orders = orders

    ##Getters

    def get_v_intensities(self):
        return self.v_intensities

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
    
    def get_approval_indicators(self):
        return self.approval_indicators

    def get_orders(self):
        return self.orders
    
    def get_whalrus_orders(self):
        return self.whalrus_orders

    def get_distances(self):
        return self.distances

    def get_agreements(self):
        return self.agreements
    
    def get_voter_majority(self):
        return self.voter_majority_outcomes