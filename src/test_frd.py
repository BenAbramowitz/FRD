import unittest
import numpy as np

import frd.helper as helper
import frd.profiles as profiles
import frd.m02_election_rules as rules
import frd.m03_delegative_voting as d_voting
import frd.m05_simulate as simulate
import frd.m04_save_data as save_data
import frd.m06_analysis as analysis

class Test_m00_helper(unittest.TestCase):
    
    def test_create_tiebreakers(self):
        result = helper.create_tiebreakers(3, seed=1, dtype=int)
        np.testing.assert_array_equal(result, np.asarray([0,2,1]))
        np.testing.assert_array_equal(result, [0,2,1])
        
    def test_array1D_to_sorted(self):
        result = helper.array1D_to_sorted([0,2,1], seed=1, tiebreakers=None)
        np.testing.assert_array_equal(result, [[0, 0, 0],[1, 1, 2],[2, 2, 1]])
        
        tiebreakers = helper.create_tiebreakers(3, seed=1, dtype=int)
        result = helper.array1D_to_sorted([0,2,1], seed=50, tiebreakers=tiebreakers) #seed should be ignored
        np.testing.assert_array_equal(result, [[0, 0, 0],[1, 1, 2],[2, 2, 1]])

    def test_normalize1D(self):
        arr = [1,2,3,4]
        result = helper.normalize1D(arr)
        np.testing.assert_array_equal(result, [0.1, 0.2, 0.3, 0.4])
        arr = [0,0,0,0]
        result = helper.normalize1D(arr) #implicitly keep_zeros=True
        np.testing.assert_array_equal(result, arr)
        result = helper.normalize1D(arr, keep_zeros=False) #implicitly keep_zeros=True
        np.testing.assert_array_equal(result, [0.25, 0.25, 0.25, 0.25])

    def test_normalize_rows_2D(self):
        arr = [[1,2,3,4],[4,5,6,5]]
        result = helper.normalize_rows_2D(arr)
        np.testing.assert_array_equal(result, [[0.1, 0.2, 0.3, 0.4],[0.2, 0.25, 0.3, 0.25]])
        arr = [[1,2,3,4],[0,0,0,0]]
        result = helper.normalize_rows_2D(arr)
        np.testing.assert_array_equal(result, [[0.1, 0.2, 0.3, 0.4],[0,0,0,0]])

    def test_subset_to_indicator(self):
        pass

    def test_params_dict_to_tuples(self):
        pass

    def test_merge_dicts(self):
        pass

class Test_m01_profiles(unittest.TestCase):
    
    def test_create_issue_prefs(self):
        np.random.seed(1)
        n_voters, n_cands, n_issues = 2, 2, 2
        voters_p, cands_p = 0.5, 0.5
        prof = profiles.Profile(n_voters, n_cands, n_issues, voters_p, cands_p, (n_cands, 0.5))
        prof.create_issue_prefs()
        v_prefs, c_prefs = prof.get_issue_prefs()
        np.testing.assert_array_equal(v_prefs, [[0,1],[0,0]])
        np.testing.assert_array_equal(c_prefs, [[0,0],[0,0]])
    
    def test_issues_to_distances(self):
        pass
    
    def test_all_derivatives(self):
        pass

# class Test_m02_election_rules(unittest.TestCase):
    
#     def test_random_winners(self):
#         pass

#     def test_score_orders(self):
#         pass
    
#     def test_plurality(self):
#         pass

#     def test_borda(self):
#         pass
    
#     # def test_stv(self):
#     #     pass
    
#     def test_max_approval(self):
#         pass
    
#     def test_rav(self):
#         pass
    
#     def test_max_score(self):
#         pass

#     # def test_chamberlain_courant(self):
#     #     pass

#     # def test_k_median(self):
#     #     pass

# class Test_m03_delegative_voting(unittest.TestCase):
    
#     pass

if __name__ == '__main__':
    unittest.main()