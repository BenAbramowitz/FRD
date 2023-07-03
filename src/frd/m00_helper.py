import numpy as np
import itertools

def create_tiebreakers(n_vals, dtype=int, seed=None):
    '''
    Return n_vals unique random values to use for tiebreaking when sorting/argsorting numpy arrays with random tiebreaking
    '''
    if seed is not None: np.random.seed(seed)
    if dtype is int or dtype is np.array([1]).dtype:
        return np.random.permutation(n_vals)
    elif dtype is float or dtype is np.array([1.0]).dtype:
        return np.random.random(n_vals)
    else:
        raise ValueError('Invalid dtype for create_tiebreakers: {dtype}')

def array1D_to_sorted(array:np.ndarray, seed:int=None, tiebreakers:np.ndarray=None):
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
    dtype = type(array[0])
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

    NOTES
    -------
    Assumes all array elements are non-negative
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

def subset_to_indicator(subset, full_set):
    '''
    Given a full_set and subset create a binary array of length len(full_set) where each index has a 1 if and only if the value at that index in full_set is in the subset.
    
    Example:
    subset = [1,3]
    full_set = [1,4,2,3]
    returns: [1, 0, 0, 1]
    
    '''
    return np.asarray([1 if x in subset else 0 for x in full_set])

def params_dict_to_tuples(params_dict:dict):
    '''
    Given dict where some values are singleton lists and others are longer lists, returns a list of all possible tuples of elements where one element comes from each value list.
    
    Example: 
    params_dict = {'a':[1,2], 'b':[3,4]}
    returns [(1,3),(1,4),(2,3),(2,4)] and ['a','b']
    '''
    param_tuples = list(itertools.product(*params_dict.values()))
    return param_tuples, list(params_dict.keys())

def merge_dicts(list_of_dicts:list):
    '''
    merge a list of dictionaries with unique keys into a single dictionary without altering any of the originals
    '''
    d = {}
    for d2 in list_of_dicts:
        d.update(d2)
    return d