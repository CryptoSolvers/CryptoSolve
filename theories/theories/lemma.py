"""
Lemma is responsible for holding a proof type
problem. Currently it is only able to solve
and show steps for proofs that only use
reductive rewrites.
"""
from copy import deepcopy
from typing import List, Optional, Set, Tuple, Type, Union
from algebra import get_vars_or_constants, Sort, Term
from rewrite import converse, narrow, normal, RewriteRule, RewriteSystem
from .inductive import TheorySystem, system_from_sort

__all__ = ['Lemma']

# TODO: Have recursion create subgoals
# TODO: Create ExistenceLemma which succeeds if unifiers are found

class Lemma:
    """
    Holds an implication proof and provides
    utilities to automate it.
    """
    def __init__(self, premise, conclusion):
        self.premise = premise
        self.steps: List[Tuple[RewriteRule, int]] = list()
        self.current_step = deepcopy(premise)
        self.conclusion = conclusion
        self.subgoals: List['ForAllLemma'] = list()
        self.hypotheses = RewriteSystem(set())
        self._auto_load_systems()

    def add_hypotheses(self, r: Union[RewriteRule, RewriteSystem, Type[TheorySystem]]):
        """Add hypotheses via rewrite rules, systems, or theory systems."""
        if isinstance(r, RewriteRule):
            self.hypotheses.append(r)
        elif isinstance(r, RewriteSystem):
            self.hypotheses.extend(r)
        elif issubclass(r, TheorySystem):
            self.hypotheses.extend(r.rules)
        else:
            raise ValueError(
                "simplify must be passed either\
                 a RewriteRule, RewriteSystem, or TheorySystem."
            )

    @property
    def proven(self):
        """
        Return whether the current ground term matches the
        conclusion ground term syntactically.
        """
        return self.current_step == self.conclusion \
               and all((g.proven for g in self.subgoals))

    def apply(self, r: RewriteRule):
        """Apply a rewrite rule to the current step."""
        if not isinstance(r, RewriteRule):
            raise ValueError("apply must be given a RewriteRule")
        x_new = r.apply(self.premise)
        if x_new is None:
            return
        self.current_step = x_new
        self.steps.append(r)
        return x_new

    def simplify(self, bound: int = -1):
        """Attempt to simplify the current state."""
        new_steps = narrow(self.current_step, self.conclusion, self.hypotheses, bound)
        if new_steps is None:
            return
        self.current_step = self.conclusion
        self.steps.extend(new_steps)
        return self.conclusion

    def auto(self, bound: int = -1):
        """
        Automate the proof by rewriting the
        current step into normal form, and applying
        the opposite steps that it takes to get
        the conclusion into normal form.
        """
        for subgoal in self.subgoals:
            subgoal.auto(self.hypotheses, bound)
        self._process_subgoals()

        # TODO: This is in need of optimization...
        # Find normal form of current step and goal term
        current_normal = normal(self.current_step, self.hypotheses, bound)
        goal_normal = normal(self.conclusion, self.hypotheses, bound)
        if current_normal != goal_normal:
            print("Auto: Normal Term Mismatch.")
            return

        # Calculate steps to get to normal forms
        steps = narrow(self.current_step, current_normal, self.hypotheses, bound)
        if steps is None:
            print("Auto: Cannot rewrite current step into normal form.")
            return
        goal_normal_steps = narrow(self.conclusion, goal_normal, self.hypotheses, bound)
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

    def _auto_load_systems(self):
        """
        Based on the sorts of constants and variables in the Lemma,
        auto load those TheorySystems.
        """
        terms = get_vars_or_constants(self.premise, True) | \
            get_vars_or_constants(self.conclusion, True)

        sorts = set((v for v in terms))
        for sort in sorts:
            tsystem: Optional[TheorySystem] = system_from_sort(sort)
            if tsystem is not None:
                self.add_hypotheses(tsystem)

    def _process_subgoals(self):
        """
        Go through all subgoals and see if they're proven.
        If so, add to hypotheses list.
        """
        subgoals_to_remove: List[int] = list()
        for i, subgoal in enumerate(self.subgoals):
            # Add proven subgoals to internal hypotheses list
            if subgoal.proven:
                new_rule = RewriteRule(subgoal.premise, subgoal.conclusion)
                self.hypotheses.append(new_rule)
                subgoals_to_remove.append(i)

        # Remove proven subgoals
        for index in reversed(subgoals_to_remove):
            subgoals_to_remove.pop(index)

    def __repr__(self):
        question_str = "?" if not self.proven else ""
        return f"{self.premise} →{question_str} {self.conclusion}"
