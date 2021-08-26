"""
Satisfiability Algorithms Davis-Putnam
and Davis-Putnam-Logemann-Loveland
"""
from collections import Counter
from functools import reduce
from operator import itemgetter
from typing import List, Set, Tuple
from ..predicate import Predicate
from .literal import Clause, Literal, negate, is_negative

__all__ = ['davis_putnam', 'dpll']

def _unit_propogation(x: List[Clause]) -> List[Clause]:
    """
    Applies unit propogation.

    If there is a clause with one literal p then
    (1) Remove clauses containing p
    (2) Remove all instances of Not(p)
    """
    # Find all unit clauses
    single_literals = (c[0] for c in x if len(c) == 1)

    # Only focus on one this rule application as
    # [[p], [Not(p)]] is an edge case
    single_literal = next(single_literals, None)

    # If there are no unit clauses, move onto the next rule.
    if single_literal is None:
        return x

    # (1) Remove clauses containing the unit clause
    new_x = [c for c in x if all((l != single_literal for l in c))]

    # (2) Remove all instances of Not(p)
    negated_single_literal = negate(single_literal)
    new_x = [[l for l in c if l != negated_single_literal] for c in new_x]

    return new_x

def _literal_counts(x: List[Clause]) -> Counter:
    """
    Returns the counts of each of the literals in all
    the clauses.
    """
    if len(x) == 0:
        return Counter()
    return reduce(lambda a,b: a + b, [Counter(c) for c in x])

def _pos_neg_lits(lc: Counter) -> Tuple[Set[Predicate], Set[Predicate]]:
    """
    Returns the set of all positive and
    negative literals separately.
    """
    # If there are no literals, then
    # return the sets as empty
    if len(lc) == 0:
        return set(), set()

    # Populate negative and positive literal sets
    negative_literals: Set[Predicate] = set()
    positive_literals: Set[Predicate] = set()
    for l in lc.keys():
        if is_negative(l):
            negative_literals.add(l.subformula)
        else:
            positive_literals.add(l)

    # Return the computed positive
    # and negative literal sets
    return positive_literals, negative_literals

def _affirmative_negative(x: List[Clause]) -> List[Clause]:
    """
    Remove clauses containing a literal
    that only occurs positively or negatively
    """
    literal_counts = _literal_counts(x)
    positive_literals, negative_literals = _pos_neg_lits(literal_counts)

    # Collect literals that are strictly positive or negative
    # but not both
    strict_literals = positive_literals ^ negative_literals

    # Only consider one strict literal
    strict_literal = next(iter(strict_literals), None)

    # If there are no strict literals,
    # move on to the next rule
    if strict_literal is None:
        return x

    # Remove clauses that contain the strict literal
    return [c for c in x if all((l != strict_literal and negate(l) != strict_literal for l in c))]

def _dp_resolution(x: List[Clause]) -> List[Clause]:
    """
    Take a literal that occurs positvely and negatively
    and combine clauses that occur positively and
    negatively with p.
    """
    # Find literals that occur both positively and negatively
    literal_counts = _literal_counts(x)
    positive_literals, negative_literals = _pos_neg_lits(literal_counts)
    polar_literals = positive_literals & negative_literals

    # If there are no such literals, then move
    # onto the next rule.
    if len(polar_literals) == 0:
        return x

    # Count the number of occurances of each of the polar
    # literals and choose the least common literal p as
    # a heuristic.
    polar_literal_counts = dict(filter(lambda y: y[0] in polar_literals, literal_counts.items()))
    p, _ = min(polar_literal_counts.items(), key=itemgetter(1))

    # Create a list C containing clauses where p occurs
    # positively; removing p from the clause
    C = [[l for l in c if l != p] for c in x if p in c]

    # Create a list D containing clauses where p occurs
    # negatively; removing Not(p) from the clause
    D = [[l for l in c if l != negate(p)] for c in x if negate(p) in c]

    # Combine C and D
    new_x: List[Clause] = []
    for ci in C:
        for di in D:
            # Or(ci, di) removing duplicate literals
            cdi = list(set(ci + di))
            # No point in adding a clause that already exists.
            if cdi not in new_x:
                new_x.append(cdi)

    # Clauses that don't contain p or not p in it
    x0 = [c for c in x if p not in c and negate(p) not in c]

    return new_x + x0

def davis_putnam(x: List[Clause]) -> bool:
    """
    Davis-Putnam procedure for deciding
    satisfiability from CNF clauses.

    This is called recursively with the
    following rules applied from high to lowest precedance:
    Unit Progation, Affirmative-Negative, Resolution.
    """
    # Base Cases
    if len(x) == 0:
        return True
    if [] in x:
        return False

    # (1) Unit Propogation
    x_new = _unit_propogation(x)
    if x_new != x:
        return davis_putnam(x_new)

    # (2) Affirmative-Negative
    x_new = _affirmative_negative(x)
    if x_new != x:
        return davis_putnam(x_new)

    # (3) DP Resolution
    x_new = _dp_resolution(x)
    return davis_putnam(x_new)

def dpll(x: List[Clause]) -> bool:
    """
    Davis-Putnam-Logemann-Loveland procedure for
    deciding satisfiability from CNF clauses.

    This is called recursively with the
    following rules applied from high to lowest precedance:
    Unit Progation, Affirmative-Negative, Splitting.
    """
    # Base Cases
    if len(x) == 0:
        return True
    if [] in x:
        return False

    # (1) Unit Propogation
    x_new = _unit_propogation(x)
    if x_new != x:
        return dpll(x_new)

    # (2) Affirmative-Negative
    x_new = _affirmative_negative(x)
    if x_new != x:
        return dpll(x_new)

    # (3) Splitting Rule

    # First we find a literals that occurs positvely and negatively
    literal_counts = _literal_counts(x)
    positive_literals, negative_literals = _pos_neg_lits(literal_counts)
    polar_literals = positive_literals & negative_literals

    # If no such literal exists, move onto the next rule...
    if len(polar_literals) == 0:
        return dpll(x)

    # Compute the counts for each of the literals and as a heuristic
    # pick the most common p
    polar_literal_counts = dict(filter(lambda y: y[0] in polar_literals, literal_counts.items()))
    p, _ = max(polar_literal_counts.items(), key=itemgetter(1))

    # Split on p
    return dpll(x + [[p]]) or dpll(x + [[negate(p)]])
