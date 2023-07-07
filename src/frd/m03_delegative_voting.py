import numpy as np

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

def weighted_majority(binary_matrix:np.ndarray, weights, verbose=False)->np.ndarray:
    '''
    Implemented weighted majority voting where preferences are binary and weights are non-negative

    PARAMS
    -------
    binary_matrix (np.ndarray): Size n_agents x n_issues, cell values are {0,1}
    weights: 1D array of len n_agents (binary_matrix.shape[0]) with non-negative weights
    **verbose: whether to print info for the steps in the weighted majority vote calculation

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
    if verbose:
        print('---------------------------')
        print(f'n_issues: {n_issues}')
        print(f'issues_profile: {binary_matrix}')
        print(f'weights: {weights}')
        print(f'n_issues: {n_issues}')
        print(f'weighted_profile: {weighted_profile}')
        print(f'vote_sums: {vote_sums}')
        print(f'weight_sum: {weight_sum}')
        print(f'outcomes: {outcomes}')
    return np.array(outcomes)

class RD():
    '''
    Elect reps, assign defautl weights, take (weighted) majority vote, then compare to voter majority
    '''
    def __init__(self, profile:profiles.Profile=None, election_rule:str=None, n_reps:int=None, default='uniform', default_params=None) -> None:
        self.profile = profile
        if election_rule is not None:
            self.election_rule = rules.rule_dispatcher(election_rule)
        else:
            self.election_rule = None
        self.n_reps = n_reps
        self.default, self.default_params = default, default_params

        self.voter_majority_outcomes = profile.get_voter_majority()

        self.rep_ids = []
        self.rep_prefs = None
        self.rep_weights = None
        self.cand_election_scores = None
    
    ###

    def voter_majority_vote(self):
        self.voter_majority_outcomes = self.profile.get_voter_majority()
        return self.voter_majority_outcomes

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
            raise ValueError('Election rule is currently None (not set yet), func elect_reps cannot elect reps')
        elif self.election_rule == rules.random_winners:
            self.rep_ids, self.cand_election_scores = self.election_rule(range(self.profile.get_n_cands()), self.n_reps)
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
            rep_outcomes = majority(self.rep_prefs)
        elif self.default == 'election_scores':
            #Give reps their election scores and all other cands zero, then thake weighted_majority vote
            self.rep_weights = [self.cand_election_scores[c] if c in self.rep_ids else 0 for c in range(self.profile.get_n_cands())]
            rep_outcomes = weighted_majority(self.rep_prefs, self.rep_weights)
        elif self.default == 'borda_scores':
            raise ValueError(f'Default weighting not implemented: {self.default}')
        elif self.default == 'approval_counts':
            raise ValueError(f'Default weighting not implemented: {self.default}')
        else:
            raise ValueError(f'Default weighting not implemented: {self.default}')

        agreement = np.count_nonzero(rep_outcomes == self.profile.get_voter_majority()) / len(rep_outcomes)
        return float(agreement)
    
    def run_RD(self)->float:
        self.elect_reps()
        self.pull_rep_prefs()
        self.voter_majority_vote()
        return self.outcome_agreement()
    
    # def new_instance(self):
    #     self.profile.new_instance()
    #     self.run_RD()

    ### Setters

    def set_election_rule(self, rule:str):
        self.election_rule = rules.rule_dispatcher(rule)

    def set_profile(self, profile):
        self.profile = profile

    def set_n_reps(self, n_reps):
        self.n_reps = n_reps

    def set_default(self, default):
        self.default = default

    def set_default_params(self, default_params):
        self.default_params = default_params

    ### Getters

    def get_election_rule(self):
        return self.election_rule

    def get_profile(self):
        return self.profile

    def get_n_reps(self):
        return self.n_reps

    def get_default(self):
        return self.default

    def get_default_params(self):
        return self.default_params
    

class WRD(RD):
    '''
    Allows delegation only once after election, so weights of reps are constant across all issues
    '''
    pass

class FRD(RD):
    '''

    INHERITED METHODS
    -----------------
    same: voter_majority_vote, elect_reps, pull_rep_prefs
    overwritten: outcome_agreement

    NOTES
    ------
    The main differences between FRD and its parent class RD are that in FRD the weights are issue-specific, so voters can alter the weight of the reps on each issue individually.
    The easiest way to implement this sems to be a 3D numpy array (n_voters x n_cands x n_issues).
    '''
    def __init__(self, profile:profiles.Profile, election_rule, n_reps, delegation_style:str, delegation_params, default='uniform') -> None:
        super().__init__(profile, election_rule, n_reps, default)
        self.default_style = delegation_style
        self.delegation_params = delegation_params

    def default_weights(self):
        '''Set default issue-specific weight of each rep for every issue'''
        pass

    def determine_delegators(self):
        pass

    def incisive_delegation(self):
        pass

    def outcome_agreement(self):
        pass