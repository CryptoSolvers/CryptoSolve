"""
DO NOT USE.
Module to contain code for forward closure by Daniel Kemp
in case Brandon ever gets back to integrating it into
the RewriteSystem module.
"""
from copy import deepcopy
from typing import List, Optional
from symcollab.algebra import Constant, Variable, Term
from symcollab.Unification.unif import unif
from .rule import RewriteRule
from .system import RewriteSystem, normal


def fpos(term: Term):
    """
    Return a list of sub non-variable positions of a given term
    """
    return fpos_aux(term, None, None)

def fpos_aux(term, parent, index):
    """
    Main code of fpos, passes along position and index parameters
    """
    if parent is None:
        position = []
    else:
        position = parent + [index]
    if isinstance(term, Variable):
        return []
    child_positions = []
    index = 0
    for child in term.arguments:
        child_positions += fpos_aux(child, position, index)
        index += 1
    return [position] + child_positions

def get_sub_term(term, input_position):
    """ Get the term at a position, uses the format that fpos returns """
    if input_position == [] or isinstance(term, (Variable, Constant)):
        return term
    return get_sub_term(
        term.arguments[input_position[0]],
        input_position[1:]
    )

def replace(term, position, subterm):
    """Replace the term at a given position."""
    new_term = deepcopy(term)
    new_subterm = new_term
    for pos in position[:-1]:
        new_subterm = new_subterm.arguments[pos]
    new_subterm_args = list(new_subterm.arguments)
    new_subterm_args[position[-1]] = subterm
    new_subterm.arguments = tuple(new_subterm_args)
    return new_term


def overlap(rule1, rule2, rs, position):
    """
    UNFINISHED
    Overlaps a rule at a position with a second rule, then reduces the
    outcome against an initial set of rules.
    """
    rule1_copy = deepcopy(rule1)
    rule2_copy = deepcopy(rule2)

    right = get_sub_term(rule1_copy.conclusion, position)
    left = rule2_copy.hypothesis
    unifiers = unif(left, right)
    print("Left", left)
    print("Right", right)
    print(unifiers)
    if unifiers is False:
        return False


    new_left = deepcopy(rule1_copy.hypothesis)
    new_left = new_left * unifiers

    new_right = deepcopy(rule1_copy.conclusion)
    new_right = replace(new_right, position, rule2_copy.conclusion)
    new_right = new_right * unifiers
    new_right = normal(new_right, rs)[0]

    return RewriteRule(new_left, new_right)

def check_redundancy(rule: RewriteRule, redundancy_rules: List[RewriteRule]):
    """
    UNFINISHED
    Checks redundancy of a rule against a set of redundancy rules.
    """
    for redundancy_rule in redundancy_rules:
        hypothesis_unifiers = unif(redundancy_rule.hypothesis, rule.hypothesis)
        conclusion_unifiers = unif(redundancy_rule.conclusion, rule.conclusion)

        if hypothesis_unifiers is not False and conclusion_unifiers is not False:
            # If all substitutions in conclusion_unifiers present in hypothesis unifiers, return True
            if all(((var, term) in hypothesis_unifiers.subs for var, term in zip(*conclusion_unifiers.subs))):
                return True

        for position in fpos(rule.hypothesis)[1:]:
            unifiers = unif(redundancy_rule.hypothesis, get_sub_term(rule.hypothesis, position))
            if unifiers is not False:
                return True
    return False

    # # By Daniel Kemp
def forward_closure(rs: RewriteSystem, bound: int = 1) -> Optional[RewriteSystem]:
    """
    UNFINISHED
    Run the forward closure on a rewrite system
    with a limit set on the number of interations.
    Defaults to 1 iteration.
    """
    initial_rules = rs.rules # R2 from the paper
    current_new_rules = deepcopy(rs.rules) # R1 from the paper
    # Start with FC0 := R, this will eventually be R3 from the paper
    current_fc = deepcopy(rs)

    for _ in range(bound):
        # Start FOV
        new_rules = RewriteSystem(set())
        for rule, initial_rule in zip(current_new_rules, initial_rules):
            for position in fpos(rule.conclusion):
                ov = overlap(rule, initial_rule, rs, position)
                if not ov:
                    continue
                print("Overlap found")
                if not check_redundancy(ov, initial_rules) and not check_redundancy(ov, new_rules.rules):
                    new_rules.append(ov)
        if len(new_rules.rules) == 0:
            return deepcopy(current_fc)

        current_new_rules = deepcopy(new_rules.rules)
        current_fc.extend(deepcopy(new_rules))

    print("Bound of {} reached but no forward closure" % (bound))
    return None
