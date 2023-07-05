import numpy as np
# import pandas as pd
# import pickle
from scipy import stats

def load_data(filename):
    '''load the experiment data from data folder and return the data dict
    
    TO DO
    -------
    Needs to work regardless of whether file is pickle or csv
    '''
    pass

def four_moments(array):
    '''given data dict, get the mean and variance for each run. Write results to csv file.'''
    mean = np.mean(array)
    variance = np.var(array)
    skew = stats.skew(array)
    kurtosis = stats.kurtosis(array)
    return mean, variance, skew, kurtosis

def analyze(data, save=True):
    '''given dict of analyzed data for each run, convert to DataFrame and save to csv file'''
    pass