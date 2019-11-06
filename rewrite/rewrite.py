import sys
sys.path.append("..")

from algebra import *
from Unification import unif
from copy import deepcopy

# Turn Variables into Constants
@overload
def freeze(term: Variable) -> Constant:
    """"""
@overload
def freeze(term: Constant) -> Constant:
    """"""
@overload
def freeze(term: Function) -> Function:
    """"""
@overload
def freeze(term: FuncTerm) -> FuncTerm:
    """"""

def freeze(term):
    term = deepcopy(term)
    if isinstance(term, Variable):
        return Constant(term.symbol)
    elif isinstance(term, FuncTerm):
        arguments = list(term.arguments)
        for i,t in enumerate(arguments):
            arguments[i] = freeze(t)
        term.set_arguments(arguments)
    return term

class RewriteRule:
    def __init__(self, hypothesis : Term, conclusion : Term):
        self.hypothesis = hypothesis
        self.conclusion = conclusion
    
    # Applies term if possible otherwise return unchanged
    def apply(self, term : Term) -> Term:
        # Change common variables in RewriteRule if they exist
        overlaping_vars = self._getOverlapVars(term)
        while overlaping_vars:
            self._changeVars(overlaping_vars, term)
            overlaping_vars = self._getOverlapVars(term)
        # Perform matching and substitution
        frozen_term = freeze(term)
        sigma = unif(self.hypothesis, frozen_term)
        if sigma:
            return sigma, self.conclusion * sigma
        else:
            return SubstituteTerm(), deepcopy(term)
        return self.conclusion * sigma if sigma else deepcopy(term)
        
    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)
    
    def _getOverlapVars(self, term) -> List[Variable]:
        rewrite_vars = get_vars(self.hypothesis, unique = True) | get_vars(self.conclusion, unique = True)
        term_vars = get_vars(term, unique = True)
        return list(rewrite_vars & term_vars)
    
    def _changeVars(self, overlaping_vars : List[Variable], term : Term):
        all_vars = get_vars(term, unique = True) | get_vars(self.hypothesis, unique = True) | get_vars(self.conclusion, unique = True)
        new_vars : List[Variable] = []
        # Go through all the variables that share the same symbol between the term and rewrite rule
        # and change the variables in the rewrite rule
        for v in overlaping_vars:
            new_var = v
            # Keep renaming variable in rewrite rule until it is not an already existing variable
            while new_var in all_vars:
                new_var = Variable(new_var.symbol + "_1")
            new_vars.append(new_var)
        # Create substitution between the old and new variable names and apply them
        s = SubstituteTerm()
        for old_v, new_v in zip(overlaping_vars, new_vars):
            s.add(old_v, new_v)
        self.hypothesis *= s
        self.conclusion *= s

def converse(rule : RewriteRule) -> RewriteRule:
    new_rule = deepcopy(rule)
    # Flip Hypothesis and Conclusion
    temp = new_rule.hypothesis
    new_rule.hypothesis = new_rule.conclusion
    new_rule.conclusion = temp
    return new_rule