from . import m00_helper as helper
from . import m01_profiles as profiles
from . import m02_election_rules as rules
from . import m03_delegative_voting as d_voting

APPROVAL_RULES = ['max_approval', 'rav']
ORDINAL_RULES = ['borda', 'plurality'] #stv, chamberlain_courant, k_median, copeland...
AGREEMENT_RULES = ['max_agreement']

def profiles_needed(election_rules_list):
    election_rules_set = set(election_rules_list)
    approvals = not election_rules_set.isdisjoint(APPROVAL_RULES) #bool
    ordinals = not set(election_rules_set).isdisjoint(ORDINAL_RULES) #bool
    agreements = not set(election_rules_set).isdisjoint(AGREEMENT_RULES) #bool
    return {'approvals':approvals, 'ordinals':ordinals, 'agreements':agreements}

def run_simulation(n_iter, profile_param_vals, election_param_vals, del_voting_param_vals):
    '''
    PARAMS
    --------
    - n_iter (int): number of iterations
    - profile_param_vals (dict): keys are params corresponding to what's needed to construct a profile, values are lists
    - election_param_vals (dict): keys are params for what's needed to elect reps (given profile), values are lists
    - del_voting_param_vals (dict): keys are params for what's needed to conduct delegative voting (given profile and elected reps), values are lists


    RETURNS
    -------
    data (dict): dict keys are tuples of param values, dict values are lists of agreements of length n_iter

    experiment_params (dict): full dict of experiment params (merged n_iter, profile, election, and del_voting params)


    NOTES
    -----
    
    
    '''
    experiment_params = helper.merge_dicts([profile_param_vals, election_param_vals, del_voting_param_vals])
    experiment_params['n_iter'] = [n_iter]
    data = {} #keys are tuples of all params, values are lists of agreements
    for it in range(n_iter):
        for profile_params in helper.params_dict_to_tuples(profile_param_vals)[0]:
            # print(f'\nprofile params: {profile_params}')
            (n_voters, n_cands, n_issues, voters_p, cands_p, approval_params) = profile_params

            prof = profiles.Profile(n_voters, n_cands, n_issues, 
                                    voters_p, cands_p, approval_params)
            
            # create new instance
            # find profile derivatives needed, and derive only the profiles necessary in profle object (depends on election_param_vals)
            election_rules = election_param_vals.get('election_rules')
            prof.new_instance(**profiles_needed(election_rules))
            # print(f'election rules: {election_rules}')
            # print(vars(prof))

            for election_params in helper.params_dict_to_tuples(election_param_vals):
                # elect reps to get rep_ids and election_scores (if election rule provides them)
                
                for del_voting_params in helper.params_dict_to_tuples(del_voting_param_vals):
                    # pull rep prefs
                    # determine whether RD, WRD, or FRD
                    # if RD: do majority vote
                    # if WRD: set weights (same for all issues), weighted majority vote 
                    # if FRD: set default issue-specific weights, update weights by delegation, weighted majority vote
                    # compute agreement with voter majority
                    # add agreement to list in data dict with key as ordered tuple of unpacked params from profile, election, and voting
                    pass


    return data, experiment_params