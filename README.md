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

An instance of an FRD problem consists of three sequential components: (1) creating preference profiles, (2) an election, and (3) weighted/delegative voting.

### To Add an Election Rule:
1. Implement the rule in frd/m02_election_rules.py
2. Add the rule to rule_dispatcher in frd/m02_election_rules.py so it can be called by its name (string vs. Callable)
3. Add the rule name to the appropriate list of rules in m04_simulate.py (determines which election profiles get created in each iter)

### Implementation Details
- Currently ordinal prefs (orders, ordermaps) cannot be incomplete. This is because these ordinal preferences are dicts where keys are voters and values are static 1D numpy arrays of fixed length.
- Unlike the other rules, RAV does not break ties randomly. It breaks ties lexicographically. However, this does not impact our current experiments because all agent prefs are independent Bernoulli random variables.
- Chamberlain-Courant and k-Medians are not currently implemented (both NP-Hard).
- Preference intensities need to be drawn from [0,1] or some sub-interval of it. Currently we only draw them uniformly. Drawing them from a normal distribution requires truncation at the boundaries 0 and 1, and numpy doesn't have a function for this. Scipy has a truncnorm function for this, but causes headaches trying to run on old MacOS, and would rather avoid the dependency if possible. Would be easier to draw from numpy.random.beta() if we need something other than random.
- Currently if an agent delegates on one issue they delegate on all issues rather than independently per-issue. Doesn't matter currently because prefs over issues for each agent are drawn i.i.d. Bernoulli, but might matter in the future.


### Bottlenecks and Efficiency
- The n_reps param (committee size) has a relatively big impact on runtime because increasing it slows down the election, weighting of the reps, and weighted majority voting by the reps.
- RAV currently runs much slower than borda, plurality, max_approval, and max_agreement (~20x). It uses for loops and a dict of approvals rather than approval_indicators.
- score_orders and score_ordermaps currently use nested for loops that are relatively slow. Can speed up with map or comprehensions later if needed. Only rules currently built on scoring rules are Borda and Plurality which are both fast even with big params.
- Delegations for FRD currently implemented using nested for loops, making them slow. Can speed up later if needed.

## To Do
- Parameters for intensity distribution should be arguments, not hard coded (currently just low and high for uniform)
- Complete unit testing (in test_frd.py)
- Add Chamberlain Courant and k-Medians to replicate NP-Hard rules

