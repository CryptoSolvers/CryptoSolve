from .rewrite import *


def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int, subs : List[RewriteRule] = []) -> Union[Literal[False], List[RewriteRule]]:
    if term == goal_term:
        return substition
    if bound < 1:
        return False
    for rule in rules:
        new_term = rule.apply(term)
        result = narrow(new_term, goal_term, rules, bound - 1, substitions + [rule])
        if result is not False:
            return result
    return False


class VariantsFromRule:
    def __init__(self, term : Term, rule : RewriteRule, subs : List[RewriteRule] = []):
        self.current_term = term
        self.rule = rule
        self.substitution = substitution
    def __iter__(self):
        return self
    def __next__(self):
        sub, new_term = self.rule.apply(self.current_term)
        return VariantsFromRule(new_term, self.rule, self.substitution + [sub])
