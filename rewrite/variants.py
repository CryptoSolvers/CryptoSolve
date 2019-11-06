from .rewrite import *


def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int, substitions : SubstituteTerm = []) -> List[RewriteRule]:
    if term == goal_term:
        return substitions
    if bound < 1:
        return False
    for rule in rules:
        new_term = rule.apply(term)
        result = narrow(new_term, goal_term, rules, bound - 1, substitions + [rule])
        if result is not False:
            return result
    return False