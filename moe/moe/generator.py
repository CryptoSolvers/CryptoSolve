"""
Generates modes of operations that can be later used in a MOOProgram.
"""
from typing import Iterator, List
from algebra import Constant, Function, Term, Variable
from xor.xor import xor

# TODO: Possibly introduce nonces as an additional argument of MOOGenerator where you can
# pass it a fixed arbitrary number of nonces that the generator can use.

__all__ = ['MOOGenerator']

class MOOGenerator:
    """Class that iteratively constructs modes of operation."""
    def __init__(self, max_history: int = 2):
        """
        Create a MOO Generator that procedurally generates different modes of
        operation.

        Parameters
        ==========
        max_history: int
          The maximum number of past cipher blocks to consider for
          constructing a mode of operation.
        """
        self.f = Function("f", 1)
        self.r = Constant("r") # Only one nounce currently
        self.P = lambda x: Variable("P_{i-" + str(x) +"}") if x > 0 else Variable("P_{i}")
        self.C = lambda x: Variable("C_{i-" + str(x) +"}")
        self.max_history = max_history
        self.tree: List[List[Term]] = [[self.f(self.P(0)), xor(self.r, self.P(0))]]
        self.branch_iter: Iterator[Term] = iter(self.tree[0]) # Where we are at the branch

    def __iter__(self):
        return self

    # This function will only show for what is currently computed but it is helpful
    # for preventing repeats of the same calculations
    def __contains__(self, x):
        for branch in self.tree:
            if x in branch:
                return True
        return False

    def _create_next_branch(self):
        """Create mode of operations of the next depth size."""
        branch: List[Term] = []
        for m in self.tree[-1]:
            temp: List[Term] = []
            temp.append(self.f(m))
            temp.append(xor(m, self.r))
            temp.append(xor(m, self.P(0)))
            # Iterate through previous blocks
            for i in range(min(len(self.tree), self.max_history)):
                temp.append(xor(m, self.P(i + 1)))
                temp.append(xor(m, self.C(i + 1)))
            # Filter out terms that are already generated or
            # have a depth of less than one.
            temp = filter(lambda x:
                          x not in self and \
                          not isinstance(x, Variable) and \
                          not isinstance(x, Constant),
                          temp)
            branch.extend(temp)
        return branch

    def __next__(self):
        """Returns the next mode of operation term."""
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
