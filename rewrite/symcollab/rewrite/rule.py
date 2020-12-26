"""
The rewrite module is responsible for maintaining
definitions of rewrite rules, as well as performing
some useful operations with them.
"""
from typing import overload, List, Optional, Union, Dict
from copy import deepcopy
from symcollab.algebra import Variable, Constant, Term, Function, \
    FuncTerm, get_vars, SortMismatch, SubstituteTerm
from symcollab.Unification.unif import unif

__all__ = ['freeze', 'converse', 'RewriteRule', 'Position']

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
    """
    Converts all the variables inside a term into constants.

    Parameters
    ----------
    term : Term
      The term in which to turn the variables into constants.

    Examples
    --------
    >>> from symcollab.algebra import Function, Variable
    >>> from symcollab.rewrite import freeze
    >>> f = Function("f", 1)
    >>> x = Variable("x")
    >>> freeze(f(x))
    f(x)
    """
    if isinstance(term, Variable):
        return Constant(term.symbol, term.sort)
    elif isinstance(term, FuncTerm):
        arguments = list(term.arguments)
        for i, t in enumerate(arguments):
            arguments[i] = freeze(t)
        term.arguments = arguments
    return term

def _getOverlapVars(term: Term, hypothesis: Term, conclusion: Term) -> List[Variable]:
    """Return a list of variables that are overlapping with two terms hypothesis and conclusion"""
    rewrite_vars = get_vars(hypothesis, unique=True) | get_vars(conclusion, unique=True)
    term_vars = get_vars(term, unique=True)
    return list(rewrite_vars & term_vars)

def _changeVars(overlaping_vars: List[Variable], term: Term, hypothesis: Term, conclusion: Term):
    """Change variable names in hypothesis & conclusion to not overlap with overlapping_vars"""
    hypothesis = deepcopy(hypothesis)
    conclusion = deepcopy(conclusion)
    all_vars = get_vars(term, unique=True) | \
        get_vars(hypothesis, unique=True) | \
        get_vars(conclusion, unique=True)
    new_vars: List[Variable] = []
    # Go through all the variables that share the same symbol between the term and rewrite rule
    # and change the variables in the rewrite rule
    for v in overlaping_vars:
        new_var = v
        # Keep renaming variable in rewrite rule until it is not an already existing variable
        while new_var in all_vars:
            new_var = Variable(new_var.symbol + "_1", new_var.sort)
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
    """
    Represents a single rewrite rule.
    Takes a hypothesis and a conclusion and
    applies them to a term when given.
    """
    def __init__(self, hypothesis: Term, conclusion: Term, unif_algo=unif):
        self.hypothesis = hypothesis
        self.conclusion = conclusion
        self.unif_algo = unif_algo

    def apply(self, term: Term, pos: Optional[Position] = None) \
    -> Optional[Union[Dict[Position, Term], Term]]:
        """
        Applies a rewrite rule to
        either a position within a term
        or all subterms.

        Parameters
        ----------
        term : Term
          The term in which to apply the RewriteRule
        pos : str, optional
          The position inside the term to rewrite.
          If no position is given then all possible subterms are rewritten.
          See notes for details.

        Notes
        -----
        Positions are given as a string sequence, with each
        character indicating the argument to consider in the FuncTerm.
        For example, '121' indicates the first argument from the
        root term. Then, the second argument from that term, and lastly
        the third argument of that term.
        f(f(a, f(b, c)),d) | '121' = b

        Examples
        --------
        >>> from symcollab.algebra import Constant, Function
        >>> from symcollab.rewrite import RewriteRule
        >>> f = Function("f", 1)
        >>> a = Constant("a")
        >>> b = Constant("b")
        >>> r = RewriteRule(f(a), f(b))
        >>> r.apply(f(f(a)))
        {'1': f(f(b))}
        """
        if pos is None:
            result = self._apply_all(term, '', term, dict())
            return result if len(result) != 0 else None
        return self._apply_pos(term, pos)


    def _match(self, term: Term) -> Term:
        """Attempts to rewrite the root term with the rewrite rule. Returns the same term if rewriting is not possible"""
        # Change common variables in RewriteRule if they exist
        overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        while overlaping_vars:
            self.hypothesis, self.conclusion = _changeVars(
                overlaping_vars, term, self.hypothesis, self.conclusion)
            overlaping_vars = _getOverlapVars(term, self.hypothesis, self.conclusion)
        # Perform matching and substitution
        frozen_term = freeze(term)
        sigma = self.unif_algo(self.hypothesis, frozen_term)
        return self.conclusion * sigma if sigma is not False else None

    def _apply_pos(self, term: Term, pos: Position) -> Optional[Term]:
        if pos == '':
            return self._match(term)

        # Recurse down to appropriate position
        term = deepcopy(term)
        if isinstance(term, Constant) or isinstance(term, Variable):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))
        index = int(pos[0])
        if index > len(term.arguments):
            raise ValueError("Position " + pos + " is not valid for term " + str(term))

        term_arguments = list(term.arguments)
        new_argument = self._apply_pos(term_arguments[index - 1], pos[1:])
        if new_argument is None:
            return None
        term_arguments[index - 1] = new_argument
        term.arguments = tuple(term_arguments)
        return term

    def _apply_all(self, term: Term, pos: Position,
                   subterm: Term, result: Dict[Position, Term]) -> Dict[Position, Term]:
        """Applies the rewrite rule to every subterm"""
        # If the current position is rewritable, add it to result dictionary
        r: Optional[Term] = None
        try:
            r = self._apply_pos(term, pos)
        except SortMismatch:
            pass
        if r is not None:
            result[pos] = r

        # Recurse down arguments
        if isinstance(subterm, FuncTerm):
            for i, t in enumerate(subterm.arguments):
                self._apply_all(term, pos + str(i + 1), t, result)

        return result

    def __repr__(self):
        return str(self.hypothesis) + " → " + str(self.conclusion)

    def __hash__(self):
        return hash((self.hypothesis, self.conclusion))

    def __eq__(self, other):
        return self.hypothesis == other.hypothesis and self.conclusion == other.conclusion

    def __deepcopy__(self, memo):
        return RewriteRule(
            deepcopy(self.hypothesis),
            deepcopy(self.conclusion),
            self.unif_algo
        )

def converse(rule: RewriteRule) -> RewriteRule:
    """
    Returns the converse of a rewrite rule.

    This means that the hypothesis and conclusion of the rewrite rule gets flipped.

    Examples
    --------
    >>> from symcollab.algebra import Constant, Function
    >>> from symcollab.rewrite import converse, RewriteRule
    >>> f = Function("f", 2)
    >>> a = Constant("a")
    >>> b = Constant("b")
    >>> r = RewriteRule(f(a,b), f(b,a))
    >>> converse(r)
    f(b, a) -> f(a, b)
    """
    new_rule = deepcopy(rule)
    # Flip Hypothesis and Conclusion
    temp = new_rule.hypothesis
    new_rule.hypothesis = new_rule.conclusion
    new_rule.conclusion = temp
    return new_rule
