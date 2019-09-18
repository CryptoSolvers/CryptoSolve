from .term import *
from .dag import TermDAG

class SubstituteTerm:
    def __init__(self):
        self.subs = [] # Tuple of (Variable, Term)

    def add_substitution(self, variable, term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        self.subs.append((variable, term))

    def __rmul__(self, term):
        new_term = deepcopy(term)
        new_term = self._termSubstituteHelper(term)
        return new_term
    
    def _termSubstituteHelper(self, term):
        return_value = None
        sub_vars, sub_terms = zip(*self.subs)
        if term in sub_vars:
            return_value = sub_terms[sub_vars.index(term)]
        elif isinstance(term, FuncTerm):
            term.arguments = list(term.arguments)
            for i, t in enumerate(term.arguments):
                term.arguments[i] = self._termSubstituteHelper(t)
            term.arguments = tuple(term.arguments)
            return_value = term
        else:
            return_value = term
        return return_value


def termSubstituteHelper(term, variable, replacement_term):
    return_value = None
    if term == variable:
        return_value = replacement_term
    elif isinstance(term, FuncTerm):
        term.arguments = list(term.arguments)
        for i, t in enumerate(term.arguments):
            term.arguments[i] = termSubstituteHelper(t, variable, replacement_term)
            term.arguments = tuple(term.arguments)
            return_value = term
    else:
        return_value = term
    return return_value

def termSubstitute(term, variable, replacement_term):
    new_term = deepcopy(term)
    new_term = termSubstituteHelper(term, variable, replacement_term)
    return new_term

def termDAGSubstitute(dag, variable, replacement_term):
    root = list(dag.dag.node)[0]
    new_root = termSubstitute(root, variable, replacement_term)
    return TermDAG(new_root)
