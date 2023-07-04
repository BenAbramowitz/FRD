import numpy as np

from . import m00_helper as helper
from . import m01_profiles as profiles
from . import m02_election_rules as rules

def majority(binary_matrix):
    n_agents, n_issues = binary_matrix.shape[0], binary_matrix.shape[1]
    vote_sums = np.sum(binary_matrix, axis=0)
    outcomes = [1 if vote_sums[i] > n_agents/2.0
                else 0 if vote_sums[i] < n_agents/2.0
                else np.random.binomial(1, 0.5) for i in range(n_issues)]
    return np.array(outcomes)

def weighted_majority(binary_matrix, weights):
    n_issues = binary_matrix.shape[1]
#     print(f'n_issues: {n_issues}')
#     print(f'issues_profile: {issues_profile}')
#     print(f'weights: {weights}')
#     print(f'n_issues: {n_issues}')
    weighted_profile = (binary_matrix.T * weights).T
#     print(f'weighted_profile: {weighted_profile}')
    vote_sums = np.sum(weighted_profile, axis=0)
#     print(f'vote_sums: {vote_sums}')
    weight_sum = np.sum(weights, axis=0, dtype=float)
#     print(f'weight_sum: {weight_sum}')
    outcomes = [1 if vote_sums[i] > weight_sum/2.0 
                else 0 if vote_sums[i] < weight_sum/2.0 
                else np.random.binomial(1, 0.5) for i in range(n_issues)]
    return np.array(outcomes)

class RD():
    '''
    Elect reps, assign them uniform weights or weights from election, and then take (weighted) majority vote
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

    ###

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
    
    ###

    def voter_majority_vote(self):
        self.voter_majority_outcomes = self.profile.get_voter_majority()
        return self.voter_majority_outcomes

    def elect_reps(self):
        if self.election_rule is None:
            raise ValueError('Election rule is currently None (not set yet), func elect_reps cannot elect reps')
        self.rep_ids, self.cand_election_scores = self.election_rule(self.profile, self.n_reps)
        return self.rep_ids, self.cand_election_scores, self.rep_prefs
    
    def pull_rep_prefs(self):
        c_prefs = self.profile.get_issue_prefs()[1]
        self.rep_prefs = c_prefs[self.rep_ids,:]
        return self.rep_prefs
    
    def outcome_agreement(self):
        if self.default == 'uniform':
            rep_outcomes = majority(self.rep_prefs)
        elif self.default == 'election_scores':
            self.rep_weights = [self.cand_election_scores[c] if c in self.rep_ids else 0 for c in range(self.profile.get_n_cands())]
            rep_outcomes = weighted_majority(self.rep_prefs, self.rep_weights)
        elif self.default == 'borda_scores':
            raise ValueError(f'Default weighting not implemented: {self.default}')
        elif self.default == 'approval_counts':
            raise ValueError(f'Default weighting not implemented: {self.default}')
        else:
            raise ValueError(f'Default weighting not implemented: {self.default}')

        agreement = np.count_nonzero(rep_outcomes == self.profile.get_voter_majority()) / len(rep_outcomes)
        return agreement
    
    def run_RD(self):
        self.elect_reps()
        self.pull_rep_prefs()
        self.voter_majority_vote()
        return self.outcome_agreement()
    
    def new_instance(self):
        self.profile.new_instance()
        self.run_RD()

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