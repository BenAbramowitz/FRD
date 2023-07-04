# FRD
README.md for Flexible Representative Democracy

This is the implementation and code used for our forthcoming SCW journal paper, which will also be available on arXiv. The code for our IJCAI 2019 paper differed slightly (been refactored).

For more information on Flexible Representative Democracy, please see our publications. Please cite these publications if you use this code in any academic capacity or are just feeling friendly.


## Setup / Installation
```bash pip install -r requirements.txt```

## Run Experiments
```[Stay Tuned]```

The generic experiment structure has 3 steps: Profile creation, election, and weighted (delegative) voting. Each of these has its own module (m01, m02, and m03).


## Dev Notes / Implementation Details

### Project Organization
Code in /src, data in /data, plots in /plots

src contains the central package /frd, the main package for with modules for running FRD/RD experiments.

main.py and tests are in the same directory as src (for easy imports).

An instance of an FRD problem consists of three sequential components: (1) creating preference profiles, (2) an election, and (3) weighted/delegative voting. There is one module for each of these steps, so they are prefixed m01, m02, and m03 respectively, with m00 reserved for general helper/utility functions. Naming conventions for modules within each directory is that we try to keep them ordered so that mX only imports mY if Y < X. So m02_election_rules can import m01_profiles but not vice versa. This helps prevent any potential import cycles.

### To Add an Election Rule:
1. Implement the rule in frd/m02_election_rules.py
2. Add the rule to rule_dispatcher in frd/m02_election_rules.py so it can be called by its name (string vs. Callable)
3. Add the rule name to the appropriate list of rules in m04_simulate.py (determines which election profiles get created in each iter)

### Election Rule Implementations
- Currently stv/irv not implemented. Could use whalrus, but need to convert the profile order to a whalrus ballot . If we want to use whalrus for other rules in the future it will be more efficient to have this conversion be a method of the Profile object.
- Currently Chamberlain-Courant and k-Medians are not implemented either (both NP-Hard).
- Still have ordermaps implemented from earlier implementation but does not currently appear to be needed. Might be useful for implementing STV, but if not it can probably be removed.

### Data Types
- Currently ordinal prefs (orders, ordermaps) cannot be incomplete. This differs from older version. This is because these ordinal preferences are dicts where keys are voters and values are 1D numpy arrays of fixed length. Old version had dict of dicts, as in {v1 : {c1:0, c2:1}, v2: {c1:1, c2:0}}

### Bottlenecks
- RAV currently runs about 20 times slower than borda, plurality, max_approval, and max_agreement (scales with n_cands). It uses for loops and a dict of approvals rather than approval_indicators.
- score_orders and score_ordermaps currently use nested for loops that are relatively slow, but easy to read and debug. Can speed up with map or comprehensions later if needed. Only rules currently built on scoring rules are Borda and Plurality which are both fast even with big params, but speed might matter if it is used for other scoring rules like STV/IRV in the future.