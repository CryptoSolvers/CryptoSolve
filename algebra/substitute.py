from .term import *
from .dag import TermDAG

class SubstituteTerm:
    def __init__(self):
        self.subs = set() # Tuple of (Variable, Term)
    
    def add(self, variable : Variable, term : Term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            # If we're adding something that's already in the set then we'll just ignore it
            if variable in v and term != t[v.index(variable)]:
                raise ValueError("'%s' already exists in the substitution set" % (variable))
        self.subs.add((variable, term))
    
    def remove(self, variable : Variable):
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            term = t[v.index(variable)]
            x = set()
            x.add((variable, term))
            self.subs = self.subs - x
    
    def replace(self, variable : Variable, term : Term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        self.remove(variable)
        self.subs.add((variable, term))
    
    def domain(self) -> List[Variable]:
        if len(self.subs) > 0:
            v, _ = zip(*self.subs)
            return v
        else:
            return list()
    
    def range(self) -> List[Term]:
        if len(self.subs) > 0:
            _, t = zip(*self.subs)
            return t
        else:
            return list()

    def __len__(self):
        return len(self.subs)
    
    def __str__(self):
        if len(self.subs) == 0:
            return "{}"
        if len(self.subs) == 1:
            variable, term = self.subs.pop()
            self.subs.add((variable, term))
            return "{ %s ↦ %s }" % (str(variable), str(term))
        str_repr = "{\n"
        i = 1
        sorted_subs = sorted(self.subs, key = lambda k: k[0].symbol)
        for variable, term in sorted_subs:
            str_repr += "  " + str(variable) + "↦" + str(term)
            str_repr += ",\n" if i < len(self.subs) else ""
            i += 1
        str_repr += "\n}"
        return str_repr

    def _applysub(self, term : Term) -> Term:
        assert isinstance(term, (Constant, Variable, FuncTerm))
        new_term = deepcopy(term)
        new_term = self._termSubstituteHelper(new_term)
        return new_term

    def __rmul__(self, term):
        return self._applysub(term)
    # TODO: Create a signature referencing: https://stackoverflow.com/questions/44640479/mypy-annotation-for-classmethod-returning-instance
    # Franz Baader and Wayne Snyder. Unification Theory. Handbook of Automated Reasoning, 2001.
    def __mul__(self, theta):
        if not isinstance(theta, SubstituteTerm):
            raise ValueError("Expected a substitution to the right of *, perhaps you meant to apply substitution on a term? If so, swap the arguments.")
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            # Apply theta to every term in its range
            t = tuple(map(theta, t))
            sigma1 = SubstituteTerm()
            sigma1.subs = set(zip(v, t)) 

            # Remove any binding x->t where x in Dom(sigma)
            theta1 = deepcopy(theta)
            theta_dom = theta1.domain()
            for vt in v:
                if vt in theta_dom:
                    theta1.remove(vt)

            # Remove trival bindings
            for vt, tt in zip(v, t):
                if vt == tt:
                    sigma1.remove(vt)
            
            # Union the two substitution sets
            result = SubstituteTerm()
            result.subs = sigma1.subs | theta1.subs
            return result
        else:
            return theta
    
    def __call__(self, term):
        return self._applysub(term)
    
    def _termSubstituteHelper(self, term : Term) -> Term:
        return_value = term
        if len(self.subs) > 0:
            sub_vars, sub_terms = zip(*self.subs)
            if term in sub_vars:
                return_value = sub_terms[sub_vars.index(term)]
            elif isinstance(term, FuncTerm):
                arguments = list(term.arguments)
                for i, t in enumerate(arguments):
                    arguments[i] = self._termSubstituteHelper(t)
                term.set_arguments(arguments)
                return_value = term
            else:
                return_value = term
        return return_value


# Below is legacy code to support termDAGSubstitute until a new DagSubstitute class is written

def termSubstituteHelper(term, variable, replacement_term):
    return_value = None
    if term == variable:
        return_value = replacement_term
    elif isinstance(term, FuncTerm):
        arguments = list(term.arguments)
        for i, t in enumerate(arguments):
            arguments[i] = termSubstituteHelper(t, variable, replacement_term)
            term.set_arguments(arguments)
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
