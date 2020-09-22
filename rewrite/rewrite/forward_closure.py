"""
DO NOT USE.
Module to contain code for forward closure by Daniel Kemp
in case Brandon ever gets back to integrating it into
the RewriteSystem module.
"""
from typing import Set
from .rewrite import RewriteRule

class RewriteSystem:
    """
    A set of rewrite rules.
    Used primarily to hold properties of a rewrite system.
    """
    def __init__(self, rules: Set[RewriteRule]):
        self.rules = rules
        # self.forward_closure_complete = False

    def append(self, rule):
        """Add a single rule to the rewrite system"""
        self.rules.append(rule)

    # TODO: Does this affect the foward closure member variable?
    def extend(self, system):
        """Add a list of rules to a rewrite system"""
        self.rules.extend(system.rules)

    def __iter__(self):
        return iter(self.rules)

    # TODO: Write the machinary needed for the below method to work
    # # By Daniel Kemp
    # def forward_closure(self, bound = 1):
    #     """Run the forward closure on a rewrite system with a limit set on the number of interations. Defaults to 1 iteration"""
    #     # Don't execute again if already completed
    #     if self.forward_closure_complete:
    #         return self

    #     initial_rules = self.rules # R2 from the paper
    #     current_new_rules = deepcopy(self) # R1 from the paper
    #     # Start with FC0 := R, this will eventually be R3 from the paper
    #     current_fc = deepcopy(self)

    #     iteration = 0
    #     for iteration in range(0, bound):
    #         # Start FOV
    #         new_rules = RewriteSystem({})
    #         for rule in current_new_rules.rules:
    #             for initial_rule in initial_rules:
    #                 for position in rule.right.fpos():
    #                     overlap = rule.overlap(initial_rule, initial_rules, position)
    #                     if overlap is not False:
    #                         if not overlap.check_redundancy(initial_rules) and not overlap.check_redundancy(new_rules.rules):
    #                             new_rules.append(overlap)
    #             if len(new_rules.rules) == 0:
    #                 self.forward_closure_complete = True
    #                 self.rules = current_fc.rules
    #                 self.clean_variable_names()
    #                 return self

    #             print("Non-redundant rules: \n", new_rules)

    #             current_new_rules = deepcopy(new_rules)
    #             new_rules = None
    #             current_fc.extend(current_new_rules)

    #         print("Bound of {} reached but no forward closure" % (bound))
    #         self.rules = current_fc.rules
    #         self.clean_variable_names()
    #         self.forward_closure_complete = False
    #         return self

    def __repr__(self):
        if len(self.rules) == 0:
            return "{}"
        if len(self.rules) == 1:
            return "{ %s }" % (str(self.rules[0]))
        str_repr = "{\n"
        i = 1
        for i, rule in enumerate(self.rules):
            str_repr += "  " + str(rule)
            str_repr += ",\n" if i < len(self.rules) else ""
            i += 1
        str_repr += "\n}"
        return str_repr
