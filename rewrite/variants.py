from .rewrite import *
class Variants:
    """Construct variants of a term from a set of rewrite rules"""
    def __init__(self, term : Term, rules : Set[RewriteRule]):
        # Each index represents the depth of the tree
        # Then at each depth of a tree we have a dictionary of terms mapped to what substitutions led to it
        self.tree : List[Dict[Term, List[Tuple[RewriteRule, Position]]]] = [{term : []}]
        self.branch_iter = iter(self.tree[0]) # Where we are at the branch
        self.rules : Set[RewriteRule] = rules
    
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
        """Compute the new branch of terms in the variant tree"""
        branch : Dict[Term, List[RewriteRule]] = {}
        last_branch_index = len(self.tree) - 1
        # Apply each rewrite rule to the terms in the last branch
        for rule in self.rules:
            for t in self.tree[last_branch_index].keys():
                new_terms = rule.apply(t)
                if new_terms is not None:
                    for pos, new_t in new_terms.items():
                        # Check that the result is not already in the tree
                        # If new, then set what rewrite rules at what positions produced the term in the branch
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

def is_finite(v : Variants, bound : int) -> bool:
    """Check the variants structure to see if it's finite. Returns true if it is or if the bound is reached on the number of rules applied. Set bound to -1 if you want to try infinitely."""
    iteration = 1
    for variant in v:
        if bound != -1 and iteration > bound:
            return False
        iteration += 1
    return True

def narrow(term : Term, goal_term : Term, rules : Set[RewriteRule], bound : int) -> Optional[List[Tuple[RewriteRule, Position]]]:
    """Narrow one term to another term through a set of rewrite rules. If the term cannot be rewritten it'll return None, otherwise it'll return a list of rewrite rules in the order that they need to be applied to produce the new term. Set bound to -1 if you want it to try infinitely"""
    variants = Variants(term, rules)
    attempt = 1
    for variant in variants:
        if bound != -1 and attempt > bound:
            break
        if variant == goal_term:
            return variants.tree[-1][variant]
        attempt += 1
    return None

def normal(element : Term, rewrite_rules : Set[RewriteRule]):
    """Returns the normal form of an element given a set of convergent term rewrite rules"""
    element = deepcopy(element)
    element_changed = True
    # We keep on going until the element stops changing
    while element_changed:
        element_changed = False
        for rule in rewrite_rules:
            new_elements = rule.apply(element)
            if new_elements is not None:
                # Replace element with any rewritten term
                element = next(iter(new_elements.values()))
                element_changed = True
                break
    return element
