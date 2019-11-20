from .rewrite import *

def recurse_rule_apply(term : Term, rule = RewriteRule):
    """Reply the rewrite rule to subterms"""
    new_term = rule.apply(term)
    # If the term didn't change, try recursing down to change...
    if new_term == term and isinstance(term, FuncTerm):
        args : List[Term] = []
        for arg in new_term.arguments:
            args.append(recurse_rule_apply(arg, rule))
        new_term.set_arguments(args)
    return new_term

class VariantsFromRule:
    """Construct variants from a rule and a term"""
    def __init__(self, term : Term, rule : RewriteRule):
        self.term = term
        self.rule = rule
        self.subs = []
    def __iter__(self):
        return self
    def __next__(self):
        new_term = recurse_rule_apply(term, rule)
        if new_term == self.term:
            raise StopIteration
        self.term = new_term
        self.subs += [self.rule]
        return new_term

class Variants:
    """Construct variants of a term from a set of rewrite rules"""
    def __init__(self, term : Term, rules : Set[RewriteRule]):
        # Each index represents the depth of the tree
        # We then have a dictionary that represents a variant and what substitutions led to it
        self.tree = [{term : []}]
        self.branch_iter = iter(self.tree[0]) # Where we are at the branch
        self.rules = rules
    def __iter__(self):
        return self
    def __contains__(self, x : Term):
        for branch in self.tree:
            if x in branch:
                return True
        return False # Only shows for what is currently computed
    def _create_next_branch(self):
        branch : Dict[Term, List[RewriteRule]] = {}
        last_branch_index = len(self.tree) - 1
        for rule in self.rules:
            for t in self.tree[last_branch_index].keys():
                new_t = recurse_rule_apply(t, rule)
                if new_t not in self:
                    branch[new_t] = self.tree[last_branch_index][t] + [rule]
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

def is_finite(v : Variants, bound : int):
    """Check the variants structure to see if it's finite. Returns true if it is or if the bound is reached on the number of rules applied."""
    iteration = 1
    for variant in v:
        if iteration > bound:
            return False
        iteration += 1
    return True

def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int) -> Union[Literal[False], List[RewriteRule]]:
    """Narrow one term to another term through a set of rewrite rules. If the term cannot be rewritten it'll return false, otherwise it'll return a list of rewrite rules in the order that they need to be applied to produce the new term."""
    variants = Variants(term, rules)
    attempt = 1
    for variant in variants:
        if attempt > bound:
            break
        if variant == goal_term:
            return variants.tree[-1][variant]
        attempt += 1
    return False
