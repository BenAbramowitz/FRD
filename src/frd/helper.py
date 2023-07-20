import numpy as np
import itertools

def create_tiebreakers(n_vals, dtype=int, seed=None)->np.ndarray:
    '''
    Return numpy array of len n_vals with unique random values to use for random tiebreaking when sorting/argsorting numpy arrays

    PARAMS
    ------
    n_vals (int): Length of random array to return
    **dtype: Whether to return array of ints or floats
    **seed: Random seed to set

    RETURNS
    -------
    np.ndarray of length n_vals and given dtype with random values
    '''
    if seed is not None: np.random.seed(seed)
    if dtype is int or dtype is np.array([1]).dtype:
        return np.random.permutation(n_vals)
    elif dtype is float or dtype is np.array([1.0]).dtype:
        return np.random.random(n_vals)
    else:
        raise ValueError('Invalid dtype for create_tiebreakers: {dtype}')

def array1D_to_sorted(array:np.ndarray, seed:int=None, tiebreakers=None, dtype=int):
    '''
    Does sort/argsort with ties are broken randomly instead of lexicographically.

    PARAMS
    --------
    array (np.ndarray): 1D array of values to sort/argsort with random tie-breaking for equal values
    **seed (int): rnadom seed for creating tiebreakers
    **tiebreakers (np.ndarray): 1D numpy array of tiebreaker values
    
    RETURNS
    --------
    array_augments (np.ndarray): 3 col array where first col are the values in array sorted (least to greatest),
    second col has values used for tie-breaking, and third col has the sorted indices of the original vals. 
    e.g. If each value in the input array corresponds to a cand, then the third col has the ids of the cands ordered from least
    to greatest in terms of those values.

    NOTES
    ------
    Created this because argsort and lexsort break ties lexicographically, and we want random tiebreaking
    Made tiebreakers an arg so tiebreakers can be reused across profiles without having to regenerate each time

    '''
    if tiebreakers is None: 
        if seed is not None: np.random.seed(seed)
        tiebreakers = create_tiebreakers(len(array), dtype, seed=seed)
    indices = np.arange(len(array), dtype=dtype)
    array_augmented = np.column_stack((array, tiebreakers, indices))
    sorted_indices = np.lexsort((array_augmented[:, 1], array_augmented[:, 0])) #applies leftmost arg last
    return array_augmented[sorted_indices]

def normalize1D(array, keep_zeros = True):
    '''
    Scale elements of 1D array so they sum to unity
    If all elements are zero, there is the option to leave it alone or to make the elements sum to 1

    PARAMS
    --------
    array: 1D array (list or numpy array) of non-negative values.

    RETURNS
    -------
    np.ndarray (float) of equal length to input array with elements that sum to 1

    '''
    total = np.sum(np.asarray(array))
    if total == 0:
        if keep_zeros == True:
            return array
        else:
            return np.ones_like(array) / len(array)
    else:
        return array / total
    
def normalize_rows_2D(array):
    '''
    Scale rows of 2D array so each row sums to unity
    '''
    return np.array(list(map(normalize1D,array)))

def subset_to_indicator(subset, full_set)->np.ndarray:
    '''
    Given a full_set and subset create a binary array of length len(full_set) where each index has a 1 if and only if the value at that index in full_set is in the subset.
    
    Example:
    subset = [1,3]
    full_set = [1,4,2,3]
    returns: [1, 0, 0, 1]

    PARAMS:
    --------
    subset (Hashable)
    full_set (Hashable)
    
    '''
    return np.asarray([1 if x in subset else 0 for x in full_set])

def params_dict_to_tuples(params_dict:dict):
    '''
    Given dict where some values are singleton lists and others are longer lists, returns a list of all possible tuples of elements where one element comes from each value list.
    
    Example: 
    params_dict = {'a':[1,2], 'b':[3,4]}
    returns [(1,3),(1,4),(2,3),(2,4)] and ['a','b']

    PARAMS
    ------
    params_dict (dict): keys can be anything (generally strings), all values are assumed to be non-empty lists

    RETURNS
    -------
    param_tuples (list of tuples): Each tuple is an ordered set of parameter values with each element coming from the list of values of a different item in param_dict
    list of keys: A list of the keys in the original params_dict, which correspond in order to each of the tuples
    '''
    param_tuples = list(itertools.product(*params_dict.values()))
    return param_tuples, list(params_dict.keys())

def merge_dicts(list_of_dicts:list):
    '''
    merge a list of dictionaries into a single dictionary without altering any of the originals

    NOTES
    -------
    Generally assumes no two dicts have the same key, otherwise update() overwrites the value each time. Will not throw exception/warning.
    '''
    d = {}
    for d2 in list_of_dicts:
        d.update(d2)
    return d

def append_dict_values(dict1, dict2):
    '''
    Valuse from dict2 are appended to values with corresponding keys in dict1
    If key does not exist in dict1, then it is created, with value copied from dict2
    Assumes all values are lists in both dicts
    '''
    for k in dict2.keys():
        dict1[k] = dict1.get(k,[]) + dict2[k]
    return dict1

def get_file_prefix(f)->str:
    '''
    Return the numeric prefix of a string (generally representing a file)

    PARAMS
    ------
    f (str): filename or other string with numeric prefix
    '''
    prefix = ""
    for char in str(f):
        if char != '_':
            prefix += char
        else:
            break
    return prefix

def vals_to_list(d):
    '''
    Takes in a dictionary and changes all values to lists that are not already lists
    '''
    d = {k:v if type(v) is list else [v] for k,v in d.items()}
    return d