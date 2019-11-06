from .rewrite import *


def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int, substition : SubstituteTerm = SubstituteTerm()) -> Union[Literal[False], SubstituteTerm]:
    if term == goal_term:
        return substition
    if bound < 1:
        return False
    for rule in rules:
        sub, new_term = rule.apply(term)
        result = narrow(new_term, goal_term, rules, bound - 1, substition * sub)
        if result is not False:
            return result
    return False


class VariantsFromRule:
    def __init__(self, term : Term, rule : RewriteRule, substitution : SubstituteTerm = SubstituteTerm()):
        self.current_term = term
        self.rule = rule
        self.substitution = substitution
    def __iter__(self):
        return self
    def __next__(self):
        sub, new_term = self.rule.apply(self.current_term)
        return VariantsFromRule(new_term, self.rule, self.substitution * sub)