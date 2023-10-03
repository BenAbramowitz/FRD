import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import os
from os import listdir
from os.path import isfile, join
import logging

from . import helper as helper

#Given a data file with experiments, we want to generate line plots
#Each line plot has an x_var, and y_var, and a l_var determining what each line represents (e.g. rules)
#pandas has good plotting tools, so might just use that for everything
#generalize to allow any l_var instead of just rules

def check_filetype(filename, filetype='csv'):
    if not filename.endswith(filetype):
        raise ValueError(f'File {filename} is not of correct type. Need {filetype}')
    
def var_to_title(s):
    if type(s) is not str: return s
    elif s.lower() in ['rav', 'irv']: return s.upper() #handle known acronyms
    elif s.lower() == 'cands_p': return 'Candidates\' Bernoulli parameter' #handle case where p is Bernoulli parameter
    elif s.lower() == 'voters_p': return 'Voters\' Bernoulli parameter' #handle case where p is Bernoulli parameter
    s = s.replace('_', ' ')
    if s[0:2] == 'n ':
        if s[2:] == 'reps':
            return 'Representatives'
        elif s[2:] == 'cands':
            return 'Candidates'
        elif s[2:] == 'issues':
            return 'Issues'
        elif s[2:] == 'voters':
            return 'Voters'
        else:
            return s[2:].title()
    return s.title()


def label_plot(x_var, y_var):
    '''
    
    '''

    title = ""
    x_label, y_label = "", ""

    if y_var == 'mean':
        y_label = "Mean Agreement"
    elif y_var == 'variance':
        y_label = "Agreement Variance"
    elif y_var == 'skew':
        y_label = "Agreement Skewness"
    elif y_var == "kurtosis":
        y_label = "Agreement Kurtosis"
    else:
        raise ValueError(f"Do not know how to use {y_var} in title of plot")
    
    title += y_label

    if x_var.lower() == 'n_voters':
        x_label = "Number of Voters"
    elif x_var.lower() == 'n_cands':
        x_label = "Number of Candidates"
    elif x_var.lower() == 'n_issues':
        x_label = "Number of Issues"
    elif x_var.lower() == 'n_reps':
        x_label = "Number of Representatives"
    elif x_var.lower() == 'voters_p':
        x_label = "Voters' Bernoulli Parameter"
    elif x_var.lower() == 'cands_p':
        x_label = "Candidates' Bernoulli Parameter"
    elif x_var.lower() == 'app_k':
        x_label = "Max Approvals Per Voter"
    elif x_var.lower() == "app_thresh":
        x_label = "Approval Threshold"
    elif x_var.lower() == "default_style":
        x_label = "Default Weighting"
    elif x_var.lower() == "del_style":
        x_label = "Delegation Style"
    elif x_var.lower() == "best_k":
        x_label = "Best k"
    elif x_var.lower() == "n_delegators":
        x_label = "Number of Delegators"
    elif x_var.lower() == "election_rules":
        x_label = ""

    if x_label:
        title += " vs "
        title += x_label

    return title, x_label, y_label

def create_subtitle(x_var:str, y_var:str, params:dict):
    subtitle = ""
    if x_var != 'n_voters':
        subtitle += f'{params["n_voters"]} voters'
    if x_var != 'n_cands':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_cands"]} candidates'
    if x_var != 'n_issues':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_issues"]} issues'
    if x_var != 'n_reps':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_reps"]} representatives'
    return subtitle

# def compare_rules(filename, experiment_name, x_var:str, y_var='mean', save=True, show=False, data_dir='../data/'):
#     '''
#     Takes in a dataframe of agreements and then plots agreement vs. x_var lines for each rule

#     TODO
#     ----------
#     Change labels of election rules in the legend to title case. 
#     For some reason doing this changes the legend keys incorrectly so the colors next to the vals don't match the plot.
#     Attempt to change using p.legend(...labels=...) is commented out

#     NOTES
#     ------
#     If the data set has more than one independent variable that was varied, this plot will not come out right.
#     If plot exists with the same name it will get overwritten

#     '''
#     check_filetype(filename, 'csv')
#     df = pd.read_csv(data_dir+filename)
#     df['election_rules'] = df['election_rules'].apply(lambda x: var_to_title(x))

#     p = sns.lineplot(data=df, x=x_var, y=y_var, hue='election_rules')
#     title, xlabel, ylabel = label_plot(x_var, y_var)
#     if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
#     p.legend(title='Election Rules')

#     p.set(title=title, xlabel=xlabel, ylabel=ylabel)
#     if save:
#         fig = p.get_figure()
#         fig.savefig('../plots/'+experiment_name+'_compare_rules_'+y_var+'_vs_'+x_var)
#     if show:
#         plt.show()


def plot_one_var(filename, experiment_name, x_var:str, y_var='mean', save=True, show=False, data_dir=Path("./data")):
    logging.info(f'Creating one line plot for experiment {experiment_name}')
    check_filetype(filename, 'csv')
    df = pd.read_csv(os.path.join(data_dir,filename))
    df[x_var] = df[x_var].apply(lambda x: var_to_title(x))
    sns.set(rc={"figure.figsize":(8, 8)})
    sns.set_style("white")
    p = sns.lineplot(data=df, x=x_var, y=y_var)
    title, xlabel, ylabel = label_plot(x_var, y_var)
    if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if save:
        fig = p.get_figure()
        plotname = os.path.join("../plots", experiment_name+'_'+y_var+'_vs_'+x_var)
        fig.savefig(plotname)
        if not show: plt.close(fig)
    if show:
        plt.show()

def plot_two_var(filename, experiment_name, l_var:str, x_var:str, y_var='mean', save=True, show=False, data_dir=Path("./data")):
    logging.info(f'Creating two line plots for experiment {experiment_name}')
    check_filetype(filename, 'csv')
    df = pd.read_csv(os.path.join(data_dir,filename))
    df[l_var] = df[l_var].apply(lambda x: var_to_title(x))
    df[x_var] = df[x_var].apply(lambda x: var_to_title(x))

    sns.set(rc={"figure.figsize":(8, 8)})
    sns.set_style("white")
    # p = sns.lineplot(data=df, x=x_var, y=y_var, hue=l_var, dashes=False, markers=True, style=l_var)
    p = sns.lineplot(data=df, x=x_var, y=y_var, hue=l_var, dashes=False)

    #format the plot
    title, xlabel, ylabel = label_plot(x_var, y_var)
    if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
    p.legend(title=var_to_title(l_var))
    if x_var.lower() == 'election_rules':
        p.set_xticks(p.get_xticks()) #dumb hack to prevent set_xticklabels from issuing a warning
        p.set_xticklabels(p.get_xticklabels(), rotation=20, ha="right")
    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    
    #Create figure for plot and save/show it
    if save: 
        fig = p.get_figure()
        plotname = os.path.join("../plots", experiment_name+'_'+y_var+'_vs_'+x_var)
        fig.savefig(plotname)
        if not show: plt.close(fig)
    if show: 
        plt.show()
    

def plot_moments(momentsfile:str, y_var:str='mean', save:bool=True, show:bool=False, data_dir=Path("./data")):
    '''
    Given file with moments data and a y_var, create a plot showing the behavior of the independent variable(s)

    TODO
    -----
    determine if one var or two far then call the correct plotting function
    Call this in compare_all to simplify
    '''
    #
    check_filetype(momentsfile, 'csv')
    experiment_name = momentsfile.partition('_moments')[0]
    df = pd.read_csv(os.path.join(data_dir,momentsfile))
    varied = get_columns_with_multiple_unique_values(df.iloc[:,1:-4])#Only the independent variables, ignore index column
    if len(varied) > 2:
        print(f'Moments file contains more than two independent variables, cannot automatically plot comparisons: {momentsfile}')
    elif len(varied) == 2:
        print(f"Independent variables: {varied[0]} and {varied[1]}")
        plot_two_var(momentsfile, experiment_name, l_var=varied[0], x_var=varied[1], y_var=y_var, save=save, show=show, data_dir=data_dir)
        plot_two_var(momentsfile, experiment_name, l_var=varied[1], x_var=varied[0], y_var=y_var, save=save, show=show, data_dir=data_dir)
    elif len(varied) == 1:
        plot_one_var(momentsfile, experiment_name, x_var=varied[0], y_var=y_var, save=save, show=show, data_dir=data_dir)


def compare_all(data_dir=Path("./data"), y_var='mean', save=True, show=True)->None:
    '''
    For all experiments with 1 or 2 independent variables, read in the moments, and create a line plot
    The variable for the y-axis is given, and the x_var and l_var are inferred
    x_var goes on the x_axis and l_var determines each of the separate lines on the plot ('hue')

    TODO
    ------
    Update the way data and moments files are matched up so it depends only on their prefix and not their order in the files list

    '''
    #get list of all experiments for which we have the moments analyzed
    path = Path(data_dir)
    momentfiles = sorted([f for f in listdir(path) if isfile(join(path, f)) and '_moments' in f])

    #for each experiment, read in the data and plot based on number of idnependent variables
    for idx,f in enumerate(momentfiles):
        plot_moments(f, y_var=y_var, save=save, show=show, data_dir=data_dir)

def get_columns_with_multiple_unique_values(df:pd.DataFrame)->list:
    '''
    Given a DataFrame return names of columns that contain more than one value

    NOTES
    -----
    Used to identify the independent variables from an experiment
    '''
    columns_with_multiple_unique_values = []
    for column in df.columns:
        unique_values = df[column].nunique()
        if unique_values > 1:
            columns_with_multiple_unique_values.append(str(column))
    return columns_with_multiple_unique_values