"""
This module is responsible for describing substitutions
which are mappings between variables and terms, as well
as the application of them.
"""
from typing import List, Set, Tuple
from copy import deepcopy
from .term import Variable, Constant, FuncTerm, Term

__all__ = ['SortMismatch', 'SubstituteTerm']

class SortMismatch(Exception):
    """Raise when there is a sort mismatch."""

class SubstituteTerm:
    """
    Represents a substitution from variables to terms.

    Examples
    --------
    >>> from symcollab.algebra import *
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> sigma = SubstituteTerm()
    >>> sigma.add(x, a)
    >>> x * sigma
    a
    """
    def __init__(self):
        self.subs: Set[Tuple[Variable, Term]] = set()

    def add(self, variable: Variable, term: Term):
        """
        Adds a mapping from a variable to a term

        Parameters
        ----------
        variable : Variable
            The variable to replace
        term : Term
            The term to replace the variable with.

        Examples
        --------
        >>> from symcollab.algebra import *
        >>> x = Variable("x")
        >>> a = Constant("a")
        >>> sigma = SubstituteTerm()
        >>> sigma.add(x, a)
        >>> print(sigma)
        { x -> a }
        """
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or \
            isinstance(term, FuncTerm) or \
            isinstance(term, Variable)

        if variable.sort != term.sort:
            raise SortMismatch("Substitution must preserve sorts.")

        # Check to see if what we're adding already exists in the substitution set
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            if variable in v and term != t[v.index(variable)]:
                raise ValueError("'%s' already exists in the substitution set" % (variable))
        self.subs.add((variable, term))

    def remove(self, variable: Variable):
        """Removes a mapping from a variable"""
        # The removal technique consists of creating a set that contains what you want to remove
        # and then do set subtraction
        if len(self.subs) > 0:
            v, t = zip(*self.subs)
            term = t[v.index(variable)]
            x = set()
            x.add((variable, term))
            self.subs = self.subs - x

    def replace(self, variable: Variable, term: Term):
        """Replaces a mapping from a variable with another term"""
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or \
            isinstance(term, FuncTerm) or \
            isinstance(term, Variable)
        self.remove(variable)
        # We don't have to call self.add as we already ensured that the item is removed
        self.subs.add((variable, term))

    def domain(self) -> List[Variable]:
        """
        Grabs the domain (the left side) of the substitutions.

        Warning: Do not pair this call with range as ordering is not guarenteed.
        """
        if len(self.subs) > 0:
            v, _ = zip(*self.subs)
            return list(v)
        else:
            return list()

    def range(self) -> List[Term]:
        """
        Grabs the range (the right side) of the substitutions.

        Warning: Do not pair this call with domain as ordering is not guarenteed.
        """
        if len(self.subs) > 0:
            _, t = zip(*self.subs)
            return list(t)
        else:
            return list()

    def __len__(self):
        return len(self.subs)

    def __deepcopy__(self, memo):
        subs = set()
        for variable, term in self.subs:
            new_variable = deepcopy(variable)
            new_term = deepcopy(term)
            subs.add((new_variable, new_term))
        subterm = SubstituteTerm()
        subterm.subs = subs
        return subterm

    def __str__(self):
        if len(self.subs) == 0:
            return "{}"
        if len(self.subs) == 1:
            variable, term = self.subs.pop()
            self.subs.add((variable, term))
            return "{ %s ↦ %s }" % (str(variable), str(term))
        str_repr = "{\n"
        i = 1
        sorted_subs = sorted(self.subs, key=lambda k: k[0].symbol)
        for variable, term in sorted_subs:
            str_repr += "  " + str(variable) + "↦" + str(term)
            str_repr += ",\n" if i < len(self.subs) else ""
            i += 1
        str_repr += "\n}"
        return str_repr

    def _applysub(self, term: Term) -> Term:
        """Apply a substitution to a term"""
        assert isinstance(term, (Constant, Variable, FuncTerm))
        new_term = deepcopy(term)
        new_term = self._termSubstituteHelper(new_term)
        return new_term

    def __rmul__(self, term: Term) -> Term:
        return self._applysub(term)

    # Franz Baader and Wayne Snyder. Unification Theory. Handbook of Automated Reasoning, 2001.
    def __mul__(self, theta):
        if not isinstance(theta, SubstituteTerm):
            raise ValueError(
                "Expected a substitution to the right of *, \
                perhaps you meant to apply substitution on a term? \
                If so, swap the arguments."
            )
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

    def __call__(self, term: Term) -> Term:
        """Apply substitution to term."""
        return self._applysub(term)

    def _termSubstituteHelper(self, term: Term) -> Term:
        return_value = term
        # If there is nothing in the substitution set, return the same term
        if len(self.subs) > 0:
            sub_vars, sub_terms = zip(*self.subs)
            # If the term matches something in the substitution set, return the mapping
            if term in sub_vars:
                return_value = sub_terms[sub_vars.index(term)]
            # Otherwise, if the term is a function, recurse down
            elif isinstance(term, FuncTerm):
                arguments = list(term.arguments)
                for i, t in enumerate(arguments):
                    arguments[i] = self._termSubstituteHelper(t)
                term.arguments = arguments
                return_value = term
        return return_value
