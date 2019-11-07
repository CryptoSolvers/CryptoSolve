from .rewrite import *

def recurse_rule_apply(term : Term, rule = RewriteRule):
    new_term = rule.apply(term)
    # If the term didn't change, try recursing down to change...
    if new_term == term and isinstance(term, FuncTerm):
        args : List[Term] = []
        for arg in new_term.arguments:
            args.append(recurse_rule_apply(arg, rule))
        new_term.set_arguments(args)
    return new_term

def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int, subs : List[RewriteRule] = []) -> Union[Literal[False], List[RewriteRule]]:
    if term == goal_term:
        return subs
    if bound < 1:
        return False
    for rule in rules:
        # new_term = rule.apply(term)
        new_term = recurse_rule_apply(term, rule)
        if new_term == term:
            continue # Rule didn't change anything, so continue
        result = narrow(new_term, goal_term, rules, bound - 1, subs + [rule])
        if result is not False:
            return result
    return False



class VariantsFromRule:
    def __init__(self, term : Term, rule : RewriteRule, subs : List[RewriteRule] = []):
        self.term = term
        self.rule = rule
        self.subs = subs
    def __iter__(self):
        return self
    def __next__(self):
        new_term = self.rule.apply(self.term)
        if new_term == self.term:
            raise StopIteration
        self.term = new_term
        self.subs += [self.rule]
        return new_term
