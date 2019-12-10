import sys
sys.path.append("..")

from algebra import *
from Unification import unif
from copy import deepcopy

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
    """Turns all the variables into constants"""
    term = deepcopy(term)
    if isinstance(term, Variable):
        return Constant(term.symbol)
    elif isinstance(term, FuncTerm):
        arguments = list(term.arguments)
        for i,t in enumerate(arguments):
            arguments[i] = freeze(t)
        term.set_arguments(arguments)
    return term

def _getOverlapVars(term : Term, hypothesis : Term, conclusion : Term) -> List[Variable]:
    """Return a list of variables that are overlapping with two terms hypothesis and conclusion"""
    rewrite_vars = get_vars(hypothesis, unique = True) | get_vars(conclusion, unique = True)
    term_vars = get_vars(term, unique = True)
    return list(rewrite_vars & term_vars)

def _changeVars(overlaping_vars : List[Variable], term : Term, hypothesis: Term, conclusion: Term):
    """Change variable names in hypothesis & conclusion to not overlap with overlapping_vars"""
    hypothesis = deepcopy(hypothesis)
    conclusion = deepcopy(conclusion)
    all_vars = get_vars(term, unique = True) | get_vars(hypothesis, unique = True) | get_vars(conclusion, unique = True)
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
    return hypothesis * s, conclusion * s


## How does positions work?
# Ex: '121' means From the root term, look at the first argument, then
# the second argument of that term, and then the first argument of that term
# f(f(a, f(b, c)),d) | '121' = b
# f(a, b) | '' = f(a, b)

# New Type for better annotations
Position = str 

class RewriteRule:
    def __init__(self, hypothesis : Term, conclusion : Term):
        self.hypothesis = hypothesis
        self.conclusion = conclusion
    
    def apply(self, term : Term, pos : Optional[Position] = None) -> Union[Dict[Position, Term], Optional[Term]]:
        """Applies the rewrite rule to a certain subterm or all subterms if not specified."""
        if pos is None:
            return self._apply_all(term, '', term, dict())
        return self._apply_pos(term, pos)

    
    def _match(self, term : Term) -> Optional[Term]:
        """Attempts to rewrite the root term with the rewrite rule. Returns False if not possible"""
        # Change common variables in RewriteRule if they exist
        overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        while overlaping_vars:
            self.hypothesis, self.conclusion = _changeVars(overlaping_vars, term, self.hypothesis, self.conclusion)
            overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        # Perform matching and substitution
        frozen_term = freeze(term)
        sigma = unif(self.hypothesis, frozen_term)
        return self.conclusion * sigma if sigma else None

    def _apply_pos(self, term : Term, pos : Position) -> Optional[Term]:
        term = deepcopy(term)
        if pos == '':
            return self._match(term)
        
        # Recurse down to appropriate position
        if isinstance(term, Constant) or isinstance(term, Variable):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))
        index = int(pos[0])
        if index > len(term.arguments):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))
        
        term.arguments = list(term.arguments)
        new_argument = self._apply_pos(term.arguments[index - 1], pos[1:])
        if new_argument is None:
            return None
        term.arguments[index - 1] = new_argument
        term.arguments = tuple(term.arguments)
        return term
    
    def _apply_all(self, term : Term, pos : Position, subterm : Term, result : Dict[Position, Term]) -> Dict[Position, Term]:
        """Applies the rewrite rule to every subterm"""
        if isinstance(subterm, Constant) or isinstance(subterm, Variable):
            return result
        
        # If the current position is rewritable, add it to result dictionary
        r = self._apply_pos(term, pos)
        if r is not None:
            result[pos] = r
        
        # Recurse down arguments
        for i, t in enumerate(subterm.arguments):
            self._apply_all(term, pos + str(i + 1), t, result)
        
        return result
    
    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)


def converse(rule : RewriteRule) -> RewriteRule:
    """Take the converse of a rewrite rule, meaning flip the hypothesis and conclusion"""
    new_rule = deepcopy(rule)
    # Flip Hypothesis and Conclusion
    temp = new_rule.hypothesis
    new_rule.hypothesis = new_rule.conclusion
    new_rule.conclusion = temp
    return new_rule