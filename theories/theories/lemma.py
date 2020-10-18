"""
Lemma is responsible for holding a proof type
problem. Currently it is only able to solve
and show steps for proofs that only use
reductive rewrites.
"""
from copy import deepcopy
from typing import List, Tuple, Type, Union
from rewrite import converse, narrow, normal, RewriteRule, RewriteSystem
from .inductive import TheorySystem

__all__ = ['Lemma']

class Lemma:
    """Holds a proof state."""
    def __init__(self, premise, conclusion):
        self.premise = premise
        self.steps: List[Tuple[RewriteRule, int]] = list()
        self.current_step = deepcopy(premise)
        self.conclusion = conclusion

    @property
    def proven(self):
        """
        Return whether the current ground term matches the
        conclusion ground term syntactically.
        """
        return self.current_step == self.conclusion

    def apply(self, r: RewriteRule):
        if not isinstance(r, RewriteRule):
            raise ValueError("apply must be given a RewriteRule")
        x_new = r.apply(self.premise)
        if x_new is None:
            return
        self.current_step = x_new
        self.steps.append(r)
        return x_new

    def simplify(self, r: Union[RewriteSystem, Type[TheorySystem]], bound: int = -1):
        """
        Simplify the current state based on either
        a RewriteSystem or a TheorySystem.
        """
        if not isinstance(r, RewriteSystem) and not issubclass(r, TheorySystem):
            raise ValueError(
                "simplify must be passed either\
                 a RewriteRule, RewriteSystem, or TheorySystem."
            )
        rules = r.rules if issubclass(r, TheorySystem) else r
        new_steps = narrow(self.current_step, self.conclusion, rules, bound)
        if new_steps is None:
            return
        self.current_step = self.conclusion
        self.steps.extend(new_steps)
        return self.conclusion

    def auto(self, r: Union[RewriteSystem, Type[TheorySystem]], bound: int = -1):
        """
        Automate the proof by rewriting the
        current step into normal form, and applying
        the opposite steps that it takes to get
        the conclusion into normal form.
        """
        if not isinstance(r, RewriteSystem) and not issubclass(r, TheorySystem):
            raise ValueError(
                "simplify must be passed either\
                 a RewriteRule, RewriteSystem, or TheorySystem."
            )
        # TODO: This is in need of optimization...
        rules = r.rules if issubclass(r, TheorySystem) else r

        # Find normal form of current step and goal term
        current_normal = normal(self.current_step, rules, bound)
        goal_normal = normal(self.conclusion, rules, bound)
        if current_normal != goal_normal:
            print("Auto: Normal Term Mismatch.")
            return

        # Calculate steps to get to normal forms
        steps = narrow(self.current_step, current_normal, rules, bound)
        if steps is None:
            print("Auto: Cannot rewrite current step into normal form.")
            return
        goal_normal_steps = narrow(self.conclusion, goal_normal, rules, bound)
        if goal_normal_steps is None:
            print("Auto: Cannot rewrite goal term into normal form.")
            return

        # Reverse goal_normal_rules and add to steps list
        steps.extend([
            (converse(rule), pos) for rule, pos in goal_normal_steps[::-1]
        ])

        self.current_step = self.conclusion
        self.steps.extend(steps)
        return self.conclusion

    def undo(self):
        """Undo the last rewrite rule."""
        if len(self.steps) == 0:
            print("No steps to undo")
            return
        last_rule, last_pos = self.steps[-1]
        converse_rule = converse(last_rule)
        old_term = converse_rule.apply(self.current_step, last_pos)
        self.current_step = old_term
        del self.steps[-1]

    def __repr__(self):
        question_str = "?" if not self.proven else ""
        return f"{self.premise} →{question_str} {self.conclusion}"
