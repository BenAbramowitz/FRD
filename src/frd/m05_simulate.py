import multiprocessing as mp
from multiprocessing import Pool

from . import m00_helper as helper
from . import m01_profiles as profiles
from . import m02_election_rules as rules
from . import m03_delegative_voting as d_voting
from . import m04_save_data as save_data


APPROVAL_RULES = ['max_approval', 'rav']
ORDINAL_RULES = ['borda', 'plurality']
AGREEMENT_RULES = ['max_agreement']
WHALRUS_RULES = ['irv']

def profiles_needed(election_rules_list):
    election_rules_set = set(election_rules_list)
    approvals = not election_rules_set.isdisjoint(APPROVAL_RULES) #bool
    ordinals = not set(election_rules_set).isdisjoint(ORDINAL_RULES) #bool
    agreements = not set(election_rules_set).isdisjoint(AGREEMENT_RULES) #bool
    whalrus = not set(election_rules_set).isdisjoint(WHALRUS_RULES) #bool
    return {'approvals':approvals, 'ordinals':ordinals, 'agreements':agreements, 'whalrus_orders':whalrus}

def tuple_to_hashable(tup):
    #Converts a tuple with non-hashable types into a tuple of strings (e.g. to be used as keys in dict)
    return tuple(str(x) for x in tup)

def single_iter(profile_param_vals:tuple, election_param_vals:dict, del_voting_param_vals:dict)->dict:
    ''''''
    data = {} #keys are tuples of all params, values are lists of agreements

    for profile_params in helper.params_dict_to_tuples(profile_param_vals)[0]:
        # create new profile instance
        (n_voters, n_cands, n_issues, voters_p, cands_p, app_k, app_thresh) = profile_params
        prof = profiles.Profile(n_voters, n_cands, n_issues, voters_p, cands_p, app_k, app_thresh)
        election_rules = election_param_vals.get('election_rules')
        prof.new_instance(**profiles_needed(election_rules)) # derive only the election profiles necessary

        for election_params in helper.params_dict_to_tuples(election_param_vals)[0]:
            # elect reps to get rep_ids and election_scores (if election rule provides scores)
            election_rule_name, n_reps = election_params
            if n_reps > n_cands: continue #skip nonsenical case where number of reps to elect is greater than number of cands

            #create rd and frd objects to be reused where necessary, depending on delegation params. Run elections only once per iter
            made_rd=False
            if None in del_voting_param_vals['delegation_style']:
                rd = d_voting.RD(prof, election_rule_name, n_reps, default='uniform')
                rd.elect_reps()
                rd.pull_rep_prefs()
                made_rd=True
            if del_voting_param_vals['delegation_style'] != [None]:
                frd = d_voting.FRD(prof, election_rule_name, n_reps, del_style=None, best_k=None, n_delegators = None, default='uniform')
                if made_rd == True: frd.set_rep_ids(rd.get_rep_ids()) #avoid running same election twice, use same reps from rd object
                else: frd.elect_reps()
            
            for del_voting_params in helper.params_dict_to_tuples(del_voting_param_vals)[0]:
                default, del_style, best_k, n_delegators = del_voting_params
                if n_delegators and n_delegators > n_voters: continue #skip nonsensical case
                if best_k and best_k > n_reps: continue #skip nonsensical case
                if del_style is None: #RD
                    rd.set_default(default)
                    agreement = rd.run_RD(quick=True)
                else: #FRD
                    frd.set_delegation_params(default=default, del_style=del_style, best_k=best_k, n_delegators = n_delegators)
                    agreement = frd.run_FRD(quick=True)
                data[tuple_to_hashable(profile_params+election_params+del_voting_params)] = [agreement]
    return data

def single_iter_unpacker(args):
    return single_iter(*args)

def sim_parallel(n_iter:int, profile_param_vals:dict, election_param_vals:dict, del_voting_param_vals:dict, save:bool=True, experiment_name=None, data_dir='./data/'):
    data = {}
    print(f'Parallelizing iterations on up to {mp.cpu_count()-1} CPUs')
    with Pool(mp.cpu_count()-1) as pool:
        for iter_data in pool.imap_unordered(single_iter_unpacker, [[profile_param_vals, election_param_vals, del_voting_param_vals]]*n_iter):
            helper.append_dict_values(data, iter_data)
    if save:
        experiment_params = helper.merge_dicts([profile_param_vals, election_param_vals, del_voting_param_vals])
        param_names = helper.params_dict_to_tuples(experiment_params)[1]
        filename = save_data.pickle_data(data, experiment_params, experiment_name=experiment_name,data_dir=data_dir)
        return data, param_names, n_iter, experiment_params, filename
    return data


    