"""
Lemma is responsible for holding a proof type
problem. Currently it is only able to solve
and show steps for proofs that only use
reductive rewrites.
"""
from copy import deepcopy
from inspect import isclass
from typing import List, Optional, Tuple, Type, Union
from symcollab.algebra import get_vars_or_constants, Term
from symcollab.rewrite import converse, narrow, normal, RewriteRule, RewriteSystem
from .inductive import TheorySystem, system_from_sort
from .boolean import Boolean

__all__ = ['Lemma']

# TODO: Have recursion create subgoals
# TODO: Figure out how to quantify variables
# TODO: Create ExistenceLemma which succeeds if unifiers are found

class Lemma:
    """
    Holds an implication proof and provides
    utilities to automate it.
    """
    def __init__(self, premise: Term, conclusion: Optional[Term] = None):
        self.premise = premise
        self.steps: List[Tuple[RewriteRule, int]] = list()
        self.current_step = deepcopy(premise)
        self.conclusion = conclusion if conclusion is not None else Boolean.trueb
        self.unproven_subgoals: List['Lemma'] = list()
        self.proven_subgoals: List['Lemma'] = list()
        self.hypotheses = RewriteSystem(set())
        self._auto_load_systems()

    def add_hypotheses(self, r: Union[RewriteRule, RewriteSystem, Type[TheorySystem]]):
        """Add hypotheses via rewrite rules, systems, or theory systems."""
        if isinstance(r, RewriteRule):
            self.hypotheses.append(r)
        elif isinstance(r, RewriteSystem):
            self.hypotheses.extend(r)
        elif isclass(r) and issubclass(r, TheorySystem):
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
               and len(self.unproven_subgoals) == 0

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
        for subgoal in self.unproven_subgoals:
            subgoal.auto(self.hypotheses, bound)
        self._process_subgoals()

        # Find normal form of current step and goal term
        current_normal, steps = normal(self.current_step, self.hypotheses, bound)
        goal_normal, goal_normal_steps = normal(self.conclusion, self.hypotheses, bound)
        if current_normal != goal_normal:
            print("Auto: Normal Term Mismatch.")
            return

        # Reverse goal_normal_rules and add to steps list
        steps.extend([
            (converse(rule), pos) for rule, pos in goal_normal_steps[::-1]
        ])

        self.current_step = self.conclusion
        self.steps.extend(steps)
        return self.conclusion

    def undo(self):
        # TODO: Not sure how this function will behave with subgoals
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

        sorts = set((v.sort for v in terms))
        for sort in sorts:
            tsystem: Optional[TheorySystem] = system_from_sort(sort)
            if tsystem is not None:
                self.add_hypotheses(tsystem)

    def _process_subgoals(self):
        """
        Go through all subgoals,
        if proven then remove subgoal and
        add to hypothesis list.
        """
        for i, subgoal in reversed(list(enumerate(self.unproven_subgoals))):
            # Add proven subgoals to internal hypotheses list
            if subgoal.proven:
                new_rule = RewriteRule(subgoal.premise, subgoal.conclusion)
                self.hypotheses.append(new_rule)
                self.unproven_subgoals.pop(i)
                self.proven_subgoals.append(subgoal)

    def __repr__(self):
        question_str = "?" if not self.proven else ""
        return f"{self.premise} →{question_str} {self.conclusion}"


def simplify(x: Term, bound: int = -1):
    """Load in theory systems needed to normalize a term."""
    hypotheses = RewriteSystem({})
    sorts = set((v.sort for v in get_vars_or_constants(x, True)))
    for sort in sorts:
        tsystem: Optional[TheorySystem] = system_from_sort(sort)
        if tsystem is not None:
            print(tsystem.rules)
            hypotheses.extend(tsystem.rules)
    return normal(x, hypotheses, bound)
