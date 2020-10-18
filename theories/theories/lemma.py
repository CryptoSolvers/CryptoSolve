from copy import deepcopy
from rewrite import RewriteRule, RewriteSystem, normal
from .inductive import TheorySystem

__all__ = ['Lemma']

# TODO: Capture the steps performed to get from premise to conclusion

class Lemma:
    """Holds a proof state."""
    def __init__(self, premise, conclusion):
        self.premise = premise
        self.step = deepcopy(premise)
        self.conclusion = conclusion

    @property
    def proven(self):
        return self.step == self.conclusion

    def simplify(self, x, bound: int = -1):
        """
        Simplify the premise based on either
        a RewriteRule, RewriteSystem, or a TheorySystem.
        """
        x_new = None
        if isinstance(x, RewriteRule):
            x_new = x.apply(self.premise)
        elif isinstance(x, RewriteSystem):
            x_new = normal(self.premise, x, bound)
        elif issubclass(x, TheorySystem):
            x_new = x.simplify(self.premise, bound)
        self.step = x_new
        return deepcopy(x_new)

    def __repr__(self):
        question_str = "?" if not self.proven else ""
        return f"{self.premise} →{question_str} {self.conclusion}"
