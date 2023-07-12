import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from os import listdir
from os.path import isfile, join

from . import m00_helper as helper

#Given a data file with experiments, we want to generate line plots
#Each line plot has an x_var, and y_var, and a l_var determining what each line represents (e.g. rules)
#pandas has good plotting tools, so might just use that for everything
#generalize to allow any l_var instead of just rules

def check_filetype(filename, filetype='csv'):
    if not filename.endswith(filetype):
        raise ValueError(f'File {filename} is not of correct type. Need {filetype}')
    
def var_to_title(s):
    if type(s) is not str:
        return s
    s = s.replace('_', ' ')
    if s.lower() in ['rav', 'irv']: return s.upper() #handle known acronyms
    else: return s.title()


def label_plot(x_var, y_var):
    '''
    
    TO DO
    -------
    Format legend values
    
    '''
    # prefix = helper.get_file_prefix(filename)
    # path = Path("./data")
    # datafile = str([f for f in listdir(path) if isfile(join(path, f)) and f[0:3] == prefix and 'RD' in f and 'moments' not in f])

    title = ""
    x_label, y_label = "", ""
    # if "FRD" in datafile:
    #     title = "FRD: "
    # elif "RD" in datafile:
    #     title = "RD: "

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
    
    title += " vs "

    if x_var.lower() == 'n_voters':
        x_label = "Number of Voters"
    elif x_var.lower() == 'n_cands':
        x_label = "Number of Cands"
    elif x_var.lower() == 'n_issues':
        x_label = "Number of Issues"
    elif x_var.lower() == 'n_reps':
        x_label = "Committee Size"
    elif x_var.lower() == 'voters_p':
        x_label = "Voters' Bernoulli Parameter"
    elif x_var.lower() == 'cands_p':
        x_label = "Cands' Bernoulli Parameter"
    elif x_var.lower() == 'app_k':
        x_label = "Max Approvals Per Voter"
    elif x_var.lower() == "app_thresh":
        x_label = "Approval Threshold"
    elif x_var.lower() == "default_style":
        x_label = "Default Weighting"
    elif x_var.lower() == "default_params":
        x_label = "Default Parameter"
    elif x_var.lower() == "delegation_style":
        x_label = "Delegation Style"
    elif x_var.lower() == "delegation_params":
        x_label = "Delegation Parameter"

    title += x_label

    return title, x_label, y_label

def create_subtitle(x_var:str, y_var:str, params:dict):
    subtitle = ""
    if x_var != 'n_voters':
        subtitle += f'{params["n_voters"]} voters'
    if x_var != 'n_cands':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_cands"]} cands'
    if x_var != 'n_issues':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_issues"]} issues'
    if x_var != 'n_reps':
        if subtitle != "": subtitle += ', '
        subtitle += f'{params["n_reps"]} reps'
    return subtitle

def compare_rules(filename, experiment_name, x_var:str, y_var='mean', save=True, show=False, data_dir='./data/'):
    '''
    Takes in a dataframe of agreements and then plots agreement vs. x_var lines for each rule

    TODO
    ----------
    Change labels of election rules in the legend to title case. 
    For some reason doing this changes the legend keys incorrectly so the colors next to the vals don't match the plot.
    Attempt to change using p.legend(...labels=...) is commented out

    NOTES
    ------
    If the data set has more than one independent variable that was varied, this plot will not come out right.
    If plot exists with the same name it will get overwritten

    '''
    check_filetype(filename, 'csv')
    df = pd.read_csv(data_dir+filename)
    df['election_rules'] = df['election_rules'].apply(lambda x: var_to_title(x))

    p = sns.lineplot(data=df, x=x_var, y=y_var, hue='election_rules')
    title, xlabel, ylabel = label_plot(x_var, y_var)
    if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
    p.legend(title='Election Rules')

    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if save:
        fig = p.get_figure()
        fig.savefig('./plots/'+experiment_name+'_compare_rules_'+y_var+'_vs_'+x_var)
    if show:
        plt.show()


def plot_one_var(filename, experiment_name, x_var:str, y_var='mean', save=True, show=False, data_dir='./data/'):
    check_filetype(filename, 'csv')
    df = pd.read_csv(data_dir+filename)
    df[x_var] = df[x_var].apply(lambda x: var_to_title(x))
    p = sns.lineplot(data=df, x=x_var, y=y_var)
    title, xlabel, ylabel = label_plot(x_var, y_var)
    if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if save:
        fig = p.get_figure()
        fig.savefig('./plots/'+experiment_name+'_'+y_var+'_vs_'+x_var)
    if show:
        plt.show()

def compare(filename, experiment_name, l_var:str, x_var:str, y_var='mean', save=True, show=False, data_dir='./data/'):
    check_filetype(filename, 'csv')
    df = pd.read_csv(data_dir+filename)
    df[l_var] = df[l_var].apply(lambda x: var_to_title(x))
    df[x_var] = df[x_var].apply(lambda x: var_to_title(x))

    p = sns.lineplot(data=df, x=x_var, y=y_var, hue=l_var)
    title, xlabel, ylabel = label_plot(x_var, y_var)
    if y_var == 'mean': p.set_yticks(np.arange(0,101,10)/100)
    p.legend(title=var_to_title(l_var))
    if x_var.lower() == 'election_rules':
        p.set_xticks(p.get_xticks()) #dumb hack to prevent set_xticklabels from issuing a warning
        p.set_xticklabels(p.get_xticklabels(), rotation=20, ha="right")
    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if save:
        plt.figure(figsize=(8,8))
        fig = p.get_figure()
        fig.savefig('./plots/'+experiment_name+'_compare_'+l_var+'_'+y_var+'_vs_'+x_var)
        plt.close(fig)
    if show:
        plt.show()
    

def compare_all(data_dir='./data/', y_var='mean', save=True, show=True)->None:
    path = Path("./data")
    momentfiles = sorted([f for f in listdir(path) if isfile(join(path, f)) and '_moments' in f])
    datafiles = sorted([f for f in listdir(path) if isfile(join(path, f)) and '_data' in f])
    for idx,f in enumerate(momentfiles):
        check_filetype(f, 'csv')
        experiment_name = f[0:-12]
        if experiment_name != datafiles[idx][0:-5]:
            print(f'Mismatch between data and moments files in {data_dir}: {f}')
            print(datafiles[idx][0:-5])
            continue
        df = pd.read_csv(data_dir+f)
        varied = get_columns_with_multiple_unique_values(df.iloc[:,1:14])
        if len(varied) > 2:
            print(f'Moments file contains more than two independent variables, cannot automatically plot comparisons: {f}')
            continue
        elif len(varied) == 2:
            compare(f, experiment_name, l_var=varied[0], x_var=varied[1], y_var=y_var, save=save, show=show, data_dir=data_dir)
            compare(f, experiment_name, l_var=varied[1], x_var=varied[0], y_var=y_var, save=save, show=show, data_dir=data_dir)
        elif len(varied) == 1:
            plot_one_var(f, experiment_name, x_var=varied[0], y_var=y_var, save=save, show=show, data_dir=data_dir)

def get_columns_with_multiple_unique_values(df)->list:
    columns_with_multiple_unique_values = []
    for column in df.columns:
        unique_values = df[column].nunique()
        if unique_values > 1:
            columns_with_multiple_unique_values.append(str(column))
    return columns_with_multiple_unique_values