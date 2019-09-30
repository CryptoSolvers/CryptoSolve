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
        sigma = unif(self.hypothesis, term)
        return self.conclusion * sigma if sigma else term
    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)