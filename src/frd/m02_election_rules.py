import numpy as np
from typing import Tuple, Callable #to type hint tuples
# import itertools
# import copy
from . import m00_helper as helper
from . import m01_profiles as profiles

'''
All election rules return two values: a list of rep ids of winning cands, and the scores of all cands from the election (not just the rep scores)
'''


def random_winners(cands, n_winners, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Given list of cands, chooses n_winners uniformly at randoml without replacement
    '''
    if seed is not None: np.random.seed(seed)
    if n_winners > len(cands):
        raise ValueError(f'Cannot elect {n_winners} reps with only {len(cands)} cands')
    return np.random.choice(cands, n_winners, replace=False), np.ones(len(cands)) #election_scores are uniform

def score_ordermaps(profile:profiles.Profile, score_vector:np.ndarray)->Tuple[np.ndarray, np.ndarray]:
    '''
    Given an ordermap and a score_vector, return a vector of the scores of the candidates
    
    PARAMS:
    profile (np.ndarray): Profile object with ordermaps attribute (dict of 1D numpy arrays)
                            The value ordermap[i][j] is the rank voter i gives to cand j
    score_vector (np.ndarray): 1D array of numbers of score increase a cand gets based on the rank a voter gives them
    
    NOTES
    -----
    Currently using nested for loops which is very slow but easy to read and debug
    '''
    n_cands = profile.get_n_cands() #vars(profile)['n_cands']
    ordermaps = profile.get_ordermaps() #vars(profile)['ordermaps']

    if n_cands != len(score_vector):
        raise ValueError('Score vector {score_vector} has length not equal to num cands: {n_cands}')
    scores = np.zeros_like(score_vector)

    for ordermap in ordermaps.values():
        for c_id, rank in enumerate(ordermap):
            scores[c_id] += score_vector[rank]
    return scores

def score_orders(profile, score_vector)->np.ndarray:
    '''
    Given an ordermap and a score_vector, return a vector of the scores of the candidates
    
    PARAMS
    ------
    profile (np.ndarray): Profile object with orders attribute (dict of 1D numpy arrays)
                            The value ordermap[v][j] is the cand that voter v ranks in position j (0 <= j < n_cands)
    score_vector (np.ndarray): 1D array with score increase a cand gets based on the rank a voter gives them
            Example: with 4 cands and Borda, score_vector is [3,2,1,0]

    RETURNS
    -------
    scores (np.ndarray): 1D array of non-negative scores of len n_cands, in order (score cand with id x is in position x)
    
    TODO
    -----
    Rewrite to run faster. Currently using nested for loops which are easy to read, but slow.
    '''
    n_cands = profile.get_n_cands() #vars(profile)['n_cands']
    orders = profile.get_orders() #vars(profile)['orders']

    if n_cands != len(score_vector):
        raise ValueError(f'Score vector {score_vector} has length not equal to num cands: {n_cands}')
    
    scores = np.zeros_like(score_vector)
    for order in orders.values():
        for rank, c_id in enumerate(order):
            scores[c_id] += score_vector[rank]
    return scores

def scoring_rule(profile:profiles.Profile, score_vector, n_winners, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Applies scoring rule according to given scoring vector and profile. Returns top n_winners with ties broken randomly and the cand scores
    '''
    scores = score_orders(profile, score_vector)
    augmented_scores = helper.array1D_to_sorted(scores, seed)
    winners = augmented_scores[:,2][-n_winners:].astype(int)
    return winners, scores

def plurality(profile:profiles.Profile, n_winners:int, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Applies plurality voting to elect top n_winners cands with highest plurality scores, breaking ties randomly
    Score vector is [1, 0, 0, ...., 0]
    '''
    n_cands = profile.get_n_cands() #vars(profile)['n_cands']
    score_vector = np.zeros(n_cands, dtype=int)
    score_vector[0] += 1
    winners, scores = scoring_rule(profile, score_vector, n_winners, seed)
    return winners, scores

def borda(profile:profiles.Profile, n_winners:int, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Uses the Borda rule to elect n_winners from cands with highest Borda scores, breaking ties randomly
    Score vector is [n_cands-1, n_cands-2, ..., 1, 0]
    '''
    n_cands = profile.get_n_cands() #vars(profile)['n_cands']
    score_vector = np.arange(n_cands-1, -1, -1, dtype=int)
    winners, scores = scoring_rule(profile, score_vector, n_winners, seed)
    return winners, scores

# def stv_whalrus(profile:profiles.Profile, n_winners:int, seed=None):
#     orders = vars(profile)['orders'].values()
#     whalrus_order = whalrus.BallotOrder(orders) #?
#     total_order = whalrus.RuleIRV(whalrus_order, tie_break=whalrus.Priority.RANDOM).strict_order_
#     winners = total_order[:n_winners]
#     return winners

def max_approval(profile:profiles.Profile, n_winners:int, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Elects the n_winners cands with the most total approvals from voters, breaking ties randomly
    '''
    approval_indicators = list(profile.get_approval_indicators().values())
    #print(f'\n\napprovals_indicators: {approval_indicators}')
    approval_counts = np.sum(np.vstack(approval_indicators), axis=0)
    # print(f'approval counts: {approval_counts}')
    winners = helper.array1D_to_sorted(approval_counts, seed)[:,2][-n_winners:]
    return winners, approval_counts

def rav(profile:profiles.Profile, n_winners:int)->Tuple[np.ndarray, np.ndarray]:
    '''
    Implements Repeated Alternative Vote with lexicographic teibreaking
    The election scores are approval counts, determinedby the profile not really by the rule
    '''
    n_cands = profile.get_n_cands()
    candidates = list(range(n_cands))
    approvals = profile.get_approvals()
    result = []
    # approvals = {v_id:v_pref for v_id, v_pref in enumerate(approvals)}
    while len(result) < n_winners:
        # Select the winner weighted 1/approval set intersection.
        non_winners = set(candidates) - set(result)
        c_scores = {c:0 for c in non_winners}
        for v_id, v_pref in approvals.items():
            # every non-winning approved candidate get 1/intersection points..
            intersect = len(set(result).intersection(v_pref)) + 1
            for c in non_winners:
                if c in v_pref:
                    c_scores[c] += 1.0 / intersect
        # choose the highest score...
        #print(c_scores)
        order = [k for k in sorted(c_scores, key=c_scores.get, reverse=True)]
        result.append(order[0])
    return np.asarray(result), max_approval(profile, n_winners)[1] #election scores are approval counts

def max_agreement(profile, n_winners, seed=None)->Tuple[np.ndarray, np.ndarray]:
    '''
    Takes the top n_winners cands with the largest sum of scores from the candidates
    Scores are the sums of values from the voters given to each cand

    TODO
    ------
    Rename, because the scores from voters do not have to be equal to agreements with cands
    
    '''
    agreements = list(profile.get_agreements().values()) # agreements = list(vars(profile)['agreements'].values())
    agreement_sums = np.sum(np.vstack(agreements), axis=0)
    augmented_agreements = helper.array1D_to_sorted(agreement_sums, seed)
    agreements_tiebroken = augmented_agreements[:,0]
    winners = augmented_agreements[:,2][-n_winners:].astype(int)
    #print(f"max_agreement winners: {winners}")
    return winners, agreement_sums

def rule_dispatcher(rule_name:str)->Callable:
    '''
    Given the name of an election rule as a string, return the Callable function to implement that rule
    '''
    if not isinstance(rule_name, str):
        raise ValueError(f'Rule name must be a string, cannot be: {rule_name}')
    if rule_name.lower() == 'borda':
        return borda
    elif rule_name.lower() == 'plurality':
        return plurality
    elif rule_name.lower() == 'random_winners':
        return random_winners
    elif rule_name.lower() == 'max_approval':
        return max_approval
    elif rule_name.lower() == 'rav':
        return rav
    elif rule_name.lower() == 'max_agreement':
        return max_agreement
    else:
        raise ValueError(f'Unable to dispatch rule: {rule_name}')