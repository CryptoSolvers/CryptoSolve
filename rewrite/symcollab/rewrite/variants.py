"""
The variants module is responsible for computing variants
and identifying some properties about them.
"""
from typing import List, Dict, Tuple, Optional
from symcollab.algebra import Term, SortMismatch
from .rule import RewriteRule, Position
from .system import RewriteSystem

__all__ = ['Variants', 'is_finite', 'narrow']

class Variants:
    """
    Construct variants of a term given a rewrite system.

    Parameters
    ----------
    term : Term
       The term to compute the variants from.
    rules : RewriteSystem
       The rules from which to compute the variants from.

    Notes
    -----
    A variant of a term $t$ is a term that can be obtained by applying
    a sequence of rewrite rules to $t$.

    Examples
    --------
    >>> from symcollab.algebra import Constant, Function, Variable
    >>> from symcollab.rewrite import RewriteRule, RewriteSystem, Variants
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> b = Constant("b")
    >>> r1 = RewriteRule(f(x, x), x)
    >>> r2 = RewriteRule(f(a, x), b)
    >>> term = f(a, f(b, b))
    >>> vt = Variants(term, RewriteSystem({r1, r2}))
    >>> list(vt)
    [f(a, f(b, b)), b, f(a, b)]
    """
    def __init__(self, term: Term, rules: RewriteSystem):
        # Each index represents the depth of the tree
        # Then at each depth of a tree we have a dictionary of terms
        # mapped to what substitutions led to it.
        self.tree: List[Dict[Term, List[Tuple[RewriteRule, Position]]]] = [{term : []}]
        self.branch_iter = iter(self.tree[0]) # Where we are at the branch
        self.rules: RewriteSystem = rules

    def __iter__(self):
        return self

    # This function will only show for what is currently computed but it is helpful
    # for preventing repeats of the same calculations
    def __contains__(self, x: Term):
        for branch in self.tree:
            if x in branch:
                return True
        return False

    def _create_next_branch(self):
        """Compute the new branch of terms in the variant tree"""
        branch: Dict[Term, List[RewriteRule]] = {}
        last_branch_index = len(self.tree) - 1
        # Apply each rewrite rule to the terms in the last branch
        for rule in self.rules:
            for t in self.tree[last_branch_index].keys():
                try:
                    new_terms = rule.apply(t)
                except SortMismatch:
                    continue
                if new_terms is None:
                    continue
                for pos, new_t in new_terms.items():
                    # Check that the result is not already in the tree
                    # If new, then save the sequence of rewrite rules
                    # used to produce the term.
                    if new_t not in self:
                        branch[new_t] = self.tree[last_branch_index][t] + [(rule, pos)]
        return branch

    def __next__(self):
        try:
            next_node = next(self.branch_iter)
        except StopIteration:
            branch = self._create_next_branch()
            if len(branch) == 0:
                raise StopIteration
            self.tree.append(branch)
            self.branch_iter = iter(self.tree[-1])
            next_node = next(self.branch_iter)
        return next_node

def is_finite(v: Variants, bound: int = -1) -> bool:
    """
    Check to see if there are a finite number of variants.

    Returns false if the variants are infinite or the bound is reached.

    Parameters
    ----------
    v : Variants
      The variants in which to check if it's finite.
    bound : int
      The bound at which to stop checking for variants.
      More specifically, the bound represents the maximum number of rewrite rules
      that the program is checking for. An infinite bound can be specified with -1.
    """
    iteration = 1
    for _ in v:
        if bound != -1 and iteration > bound:
            return False
        iteration += 1
    return True

def narrow(term: Term, goal_term: Term, rules: RewriteSystem, bound: int = -1) \
    -> Optional[List[Tuple[RewriteRule, Position]]]:
    """
    Returns the sequence of rewrite rules necessary to rewrite one term to a goal term.
    If the term cannot be rewritten, this function will return None.
    A bound greater than -1 will set the function to stop
    attempting to reach the goal after a certain number of steps.

    Parameters
    ----------
    term : Term
      The term to start from.
    goal_term : Term
      The term to attempt to rewrite to.
    rules : RewriteSystem
      The rules from which to rewrite from.
    bound : int
      The maximum number of times to attempt rewriting.
      -1 indicates an infinite bound.

    Examples
    --------
    >>> from symcollab.algebra import Constant, Function, Variable
    >>> from symcollab.rewrite import RewriteRule, RewriteSystem, narrow
    >>> f = Function("f", 2)
    >>> x = Variable("x")
    >>> a = Constant("a")
    >>> b = Constant("b")
    >>> r1 = RewriteRule(f(x, x), x)
    >>> r2 = RewriteRule(f(a, x), b)
    >>> term = f(a, f(b, b))
    >>> narrow(term, f(a,b), RewriteSystem({r1, r2}), -1)
    [(f(x, x) → x, '2')]
    """
    variants = Variants(term, rules)
    attempt = 1
    for variant in variants:
        if bound != -1 and attempt > bound:
            break
        if variant == goal_term:
            return variants.tree[-1][variant]
        attempt += 1
    return None
