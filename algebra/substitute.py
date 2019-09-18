from .term import *
from .dag import TermDAG

class SubstituteTerm:
    def __init__(self):
        self.subs = set() # Tuple of (Variable, Term)

    def add(self, variable, term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            # If we're adding something that's already in the set then we'll just ignore it
            if variable in v and term != t[v.index(variable)]:
                raise ValueError("'%s' already exists in the substitution set" % (variable))
        self.subs.add((variable, term))
    
    def remove(self, variable):
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            term = t[v.index(variable)]
            x = set()
            x.add((variable, term))
            self.subs = self.subs - x
    
    def replace(self, variable, term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        self.remove(variable)
        self.subs.add((variable, term))

    def __str__(self):
        if len(self.subs) == 0:
            return "{}"
        if len(self.subs) == 1:
            variable, term = self.subs.pop()
            self.subs.add((variable, term))
            return "{ %s ↦ %s }" % (str(variable), str(term))
        str_repr = "{\n"
        i = 1
        for variable, term in self.subs:
            str_repr += "  " + str(variable) + "↦" + str(term)
            if i < len(self.subs):
                str_repr += ",\n"
            i += 1
        str_repr += "\n}"
        return str_repr


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
