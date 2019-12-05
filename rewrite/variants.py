from .rewrite import *

def recurse_rule_apply(term : Term, rule : RewriteRule):
    """Apply rewrite rule to subterms if term is unchanged"""
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
        self.subs : List[RewriteRule] = []
    def __iter__(self):
        return self
    def __next__(self):
        new_term = recurse_rule_apply(self.term, self.rule)
        if new_term == self.term:
            raise StopIteration
        self.term = new_term
        self.subs += [self.rule]
        return new_term

class Variants:
    """Construct variants of a term from a set of rewrite rules"""
    def __init__(self, term : Term, rules : Set[RewriteRule]):
        # Each index represents the depth of the tree
        # Then at each depth of a tree we have a dictionary of terms mapped to what substitutions led to it
        self.tree = [{term : []}]
        self.branch_iter = iter(self.tree[0]) # Where we are at the branch
        self.rules = rules
    def __iter__(self):
        return self
    # This function will only show for what is currently computed but it is helpful
    # for preventing repeats of the same calculations
    def __contains__(self, x : Term):
        for branch in self.tree:
            if x in branch:
                return True
        return False
    def _create_next_branch(self):
        branch : Dict[Term, List[RewriteRule]] = {}
        last_branch_index = len(self.tree) - 1
        # Apply each rewrite rule to the term 
        # Add the results to the new branch of the tree if it doesn't appear elsewhere in the tree
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
    """Check the variants structure to see if it's finite. Returns true if it is or if the bound is reached on the number of rules applied. Set bound to -1 if you want to try infinitely."""
    iteration = 1
    for variant in v:
        if bound != -1 and iteration > bound:
            return False
        iteration += 1
    return True

def narrow(term : Term, goal_term : Term, rules : List[RewriteRule], bound : int) -> Union[Literal[False], List[RewriteRule]]:
    """Narrow one term to another term through a set of rewrite rules. If the term cannot be rewritten it'll return false, otherwise it'll return a list of rewrite rules in the order that they need to be applied to produce the new term. Set bound to -1 if you want it to try infinitely"""
    variants = Variants(term, rules)
    attempt = 1
    for variant in variants:
        if bound != -1 and attempt > bound:
            break
        if variant == goal_term:
            return variants.tree[-1][variant]
        attempt += 1
    return False
