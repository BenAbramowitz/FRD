# FRD
README.md for Flexible Representative Democracy

This is the implementation and code used for our forthcoming SCW journal paper, which will also be available on arXiv. The code for our IJCAI 2019 paper differed slightly (been refactored).

For more information on Flexible Representative Democracy, please see our publications. Please cite these publications if you use this code in any academic capacity or are just feeling friendly.


## Setup / Installation
```bash pip install -r requirements.txt```

## Run Experiments
```python -m main```

The parameters for experiments are found in config.json, where each experiment is read in as a dict with its parameters as keys.
All current experiments compare the election rules, so that each plot has a line per election rule. Each experiment varies one other parameter to serve as the independent variable in the experiment.

The parameters within main.py control which of the experiments from config.json to run, the random seed, the number of iterations to run each experiment to average over, whether to save the data (overwriting any existing data for that experiment), and whether to time the runs.

The generic experiment structure has 3 steps: Profile creation, election, and weighted (delegative) voting. Each of these has its own module (m01, m02, and m03) and its own set of parameters.



## Dev Notes

### Project Organization
Code in /src, data in /data, plots in /plots

src contains the central package /frd, the main package for with modules for running FRD/RD experiments.

main.py and tests are in the same directory as src.

An instance of an FRD problem consists of three sequential components: (1) creating preference profiles, (2) an election, and (3) weighted/delegative voting. There is one module for each of these steps, so they are prefixed m01, m02, and m03 respectively, with m00 reserved for general helper/utility functions. Naming conventions for modules within each directory is that we try to keep them ordered so that mX only imports mY if Y < X. So m02_election_rules can import m01_profiles but not vice versa. This helps prevent any potential import cycles.

### To Add an Election Rule:
1. Implement the rule in frd/m02_election_rules.py
2. Add the rule to rule_dispatcher in frd/m02_election_rules.py so it can be called by its name (string vs. Callable)
3. Add the rule name to the appropriate list of rules in m04_simulate.py (determines which election profiles get created in each iter)

### Implementation Details
- Currently ordinal prefs (orders, ordermaps) cannot be incomplete. This is because these ordinal preferences are dicts where keys are voters and values are static 1D numpy arrays of fixed length.
- Unlike the other rules, RAV does not break ties randomly. It breaks ties lexicographically. However, this does not impact our current experiments because all agent prefs are independent Bernoulli random variables.
- Currently Chamberlain-Courant and k-Medians are not currently implemented (both NP-Hard).
- Functionality for ordermaps is currently commented out because it is not currently being used for any election rule


### Bottlenecks and Efficiency
- The n_reps param (committee size) has a relatively big impact on runtime because increasing it slows down the election, weighting of the reps, and weighted majority voting by the reps.
- RAV currently runs much slower than borda, plurality, max_approval, and max_agreement (~20x). It uses for loops and a dict of approvals rather than approval_indicators.
- score_orders and score_ordermaps currently use nested for loops that are relatively slow. Can speed up with map or comprehensions later if needed. Only rules currently built on scoring rules are Borda and Plurality which are both fast even with big params.
- Delegations for FRD currently implemented using nested for loops, making them slow. Can speed up later if needed.

## To Do
- Complete unit testing (in test_frd.py)
- Add Chamberlain Courant and k-Medians
- Add function for generating plots from all available data