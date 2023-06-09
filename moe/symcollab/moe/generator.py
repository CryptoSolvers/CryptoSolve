"""
Generates modes of operations that can be later used in a MOOProgram, but only generates those that satisfy parameters.
"""

from typing import Iterator, List
from symcollab.algebra import Constant, Function, Term, Variable, FuncTerm
from symcollab.xor.xor import xor

__all__ = ['MOOGenerator']

# TODO: Possibly introduce nonces as an additional argument of MOOGenerator where you can
# pass it a fixed arbitrary number of nonces that the generator can use

class MOOGenerator():
	"""
	Only generates modes of operations that satisfy these parameters:

	Parameters
	----------
	max_history: int
		The mximum number of past cipher blocks to consider for
		constructing a mode of operation.
	max_f_depth: int
		The maximum amount of nested encryption applications.

	Example
	-------
	>>> g = MOOGenerator()
	>>> # Generate the 17th term
	>>> t = [next(g) for i in range(17)][-1]
	>>> # Register the custom MOO
	>>> tm = CustomMOO(t)
	>>> # Check the mode of operation
	>>> moo_check(tm.name, 'every', p_unif, 5)
	>>> # We can also generate more random MOOs if we'd like
	>>> # The next 5 random MOO
	>>> for _ in range(5):
    >>>	    print(next(g))
	"""
	def __init__(self, max_history: int = 2, max_f_depth: int = 3):
		self.max_history = max_history
		self.max_f_depth = max_f_depth

		self.f = Function("f", 1)
		self.r = Constant("r") # Only one nonce currently
		self.tree: List[List[Term]] = [[self.f(MOOGenerator._P(0)), xor(self.r, MOOGenerator._P(0))]]
		self.branch_iter: Iterator[Term] = iter(self.tree[0]) # Where we are at the branch

	def __iter__(self):
		return self

	@staticmethod
	def _P(j: int) -> Term:
		return Variable(f"P[i-{j}]") if j > 0 else Variable("P[i]")

	@staticmethod
	def _C(j: int) -> Term:
		return Variable(f"C[i-{j}]") if j > 0 else Variable("C[i]")

	# This function will only show for what is currently computedbut it is helpful
	# for preventing repeats of the same calculations
	def __contains__(self, x):
		for branch in self.tree:
			if x in branch:
				return True
		return False

	def _create_next_branch(self):
		branch: List[Term] = []
		for m in self.tree[-1]:
			temp: List[Term] = []
			#check f_depth before appending new f
			if(_check_f_depth(m) < self.max_f_depth):
				temp.append(self.f(m))
			temp.append(xor(m, self.r))
			temp.append(xor(m, MOOGenerator._P(0)))
			# Iterate through previous blocks
			for i in range(min(len(self.tree), self.max_history)):
				temp.append(xor(m, MOOGenerator._P(i + 1)))
				temp.append(xor(m, MOOGenerator._C(i + 1)))
			# Filter out terms that are already generated or
			# have a depth of less than one
			temp = filter(lambda x:
						  x not in self and \
						  not isinstance(x, Variable) and \
						  not isinstance(x, Constant),
						  temp)
			branch.extend(temp)
		return branch

	def __next__(self):
		"""Returns next mode of operation term."""
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

def _check_f_depth(term: Term) -> int:
	if isinstance(term, FuncTerm) and term.function.arity > 0:
		if term.function == Function("f", 1):
			return 1 + _check_f_depth(term.arguments[0])
		return max((_check_f_depth(t) for t in term.arguments))
	return 0
