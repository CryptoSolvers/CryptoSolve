import sys
sys.path.append("..")

from algebra import *
from Unification import unif

class RewriteRule:
    def __init__(self, hypothesis : Term, conclusion : Term):
        self.hypothesis = hypothesis
        self.conclusion = conclusion
    # Applies term if possible otherwise return unchanged
    def apply(self, term : Term):
        # Change common variables in RewriteRule if they exist
        overlaping_vars = self._getOverlapVars(term)
        while overlaping_vars:
            self._changeVars(overlaping_vars)
            overlaping_vars = self._getOverlapVars(term)
        # Perform matching and substitution
        sigma = unif(self.hypothesis, term)
        return self.conclusion * sigma if sigma else term
    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)
    def _getOverlapVars(self, term):
        rewrite_vars = get_vars(self.hypothesis, unique = True) | get_vars(self.conclusion, unique = True)
        term_vars = get_vars(term, unique = True)
        return rewrite_vars & term_vars
    def _changeVars(self, overlaping_vars):
        new_vars = map(lambda v: Variable(v.symbol + "_1"), overlaping_vars)
        s = SubstituteTerm()
        for old_v, new_v in zip(overlaping_vars, new_vars):
            s.add(old_v, new_v)
        self.hypothesis *= s
        self.conclusion *= s
        