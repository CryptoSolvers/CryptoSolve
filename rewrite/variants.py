from .rewrite import *


def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int, substitions : List[SubstituteTerm] = []) -> List[SubstituteTerm]:
    if term == goal_term:
        return substitions
    if bound < 1:
        return False
    for rule in rules:
        sub, new_term = rule.apply(term)
        result = narrow(new_term, goal_term, rules, bound - 1, substitions + [sub])
        if result is not False:
            return result
    return False


class VariantsFromRule:
    def __init__(self, term : Term, rule : RewriteRule):
        self.current_term = term
        self.rule = rule
    def __iter__(self):
        return self
    def __next__(self):
        return VariantsFromRule(self.rule.apply(self.current_term), self.rule)