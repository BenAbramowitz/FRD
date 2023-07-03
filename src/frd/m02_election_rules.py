import numpy as np
# import itertools
# import copy
from . import m00_helper as helper
from . import m01_profiles as profiles


def random_winners(cands, n_winners, seed=None):
    if seed is not None: np.random.seed(seed)
    if n_winners > len(cands):
        raise ValueError(f'Cannot elect {n_winners} reps with only {len(cands)} cands')
    return np.random.choice(cands, n_winners, replace=False), None #does not score the winners

def score_ordermaps(profile:profiles.Profile, score_vector:np.ndarray):
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
    n_cands = vars(profile)['n_cands']
    ordermaps = vars(profile)['ordermaps']

    if n_cands != len(score_vector):
        raise ValueError('Score vector {score_vector} has length not equal to num cands: {n_cands}')
    scores = np.zeros_like(score_vector)

    for ordermap in ordermaps.values():
        for c_id, rank in enumerate(ordermap):
            scores[c_id] += score_vector[rank]
    return scores

def score_orders(profile, score_vector):
    '''
    Given an ordermap and a score_vector, return a vector of the scores of the candidates
    
    PARAMS:
    profile (np.ndarray): Profile object with orders attribute (dict of 1D numpy arrays)
                            The value ordermap[v][j] is the cand voter v ranks in position j (0 <= j <= n_cands)
    score_vector (np.ndarray): 1D array of numbers of score increase a cand gets based on the rank a voter gives them
    
    NOTES
    -----
    Currently using nested for loops which is very slow but easy to read and debug
    '''
    n_cands = vars(profile)['n_cands']
    orders = vars(profile)['orders']

    if n_cands != len(score_vector):
        raise ValueError('Score vector {score_vector} has length not equal to num cands: {n_cands}')
    scores = np.zeros_like(score_vector)

    for order in orders.values():
        for rank, c_id in enumerate(order):
            scores[c_id] += score_vector[rank]
    return scores

def scoring_rule(profile:profiles.Profile, score_vector, n_winners, seed=None):
    scores = score_orders(profile, score_vector)
    augmented_scores = helper.array1D_to_sorted_indices(scores, seed)
    winners = augmented_scores[:,2][-n_winners:].astype(int)
    return winners, scores

def plurality(profile:profiles.Profile, n_winners:int, seed=None):
    n_cands = vars(profile)['n_cands']
    score_vector = np.zeros(n_cands, dtype=int)
    score_vector[0] += 1
    winners, scores = scoring_rule(profile, score_vector, n_winners, seed)
    return winners, scores

def borda(profile:profiles.Profile, n_winners:int, seed=None):
    n_cands = vars(profile)['n_cands']
    score_vector = np.arange(n_cands-1, -1, -1, dtype=int)
    winners, scores = scoring_rule(profile, score_vector, n_winners, seed)
    return winners, scores

# def stv_whalrus(profile:profiles.Profile, n_winners:int, seed=None):
#     orders = vars(profile)['orders'].values()
#     whalrus_order = whalrus.BallotOrder(orders) #?
#     total_order = whalrus.RuleIRV(whalrus_order, tie_break=whalrus.Priority.RANDOM).strict_order_
#     winners = total_order[:n_winners]
#     return winners

def max_approval(profile, n_winners, seed=None):
    approvals = vars(profile)['approvals'].values()
    approval_counts = np.sum(np.vstack(approvals), axis=0)
    # print(f'approval counts: {approval_counts}')
    winners = helper.array1D_to_sorted(approval_counts, seed)[:,2][-n_winners:]
    return winners, approval_counts

def rav(profile, n_winners, seed=None):
    n_cands = vars(profile)['n_cands']
    candidates = list(range(n_cands))
    approvals = vars(profile)['approvals']
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
        
        tiebreakers = helper.create_tiebreakers(len(order), dtype=int)
        array_augmented = np.column_stack((order, tiebreakers))
        order_tiebroken = np.lexsort((array_augmented[:, 1], array_augmented[:, 0]))
        result.append(order_tiebroken[0])
    return result, None #does not score the winners

def max_agreement(profile, n_winners, seed=None):
    agreements = vars(profile)['agreements'].values()
    agreement_sums = np.sum(np.vstack(agreements), axis=0)
    augmented_agreements = helper.array1D_to_sorted(agreement_sums, seed)
    agreements_tiebroken = augmented_agreements[:,0]
    winners = augmented_agreements[:,2][-n_winners:]
    return winners, agreements_tiebroken

def rule_dispatcher(rule_name:str):
    if rule_name == 'borda':
        return borda
    elif rule_name == 'plurality':
        return plurality
    elif rule_name == 'random_winners':
        return random_winners
    elif rule_name == 'max_approval':
        return max_approval
    elif rule_name == 'rav':
        return rav
    elif rule_name == 'max_agreement':
        return max_agreement
    else:
        raise ValueError(f'Unable to dispatch rule: {rule_name}')