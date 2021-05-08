from typing import Tuple, Dict, List, Optional, Set
from term import *
from symcollab.rewrite import RewriteRule
from anytree import AnyNode, RenderTree

"""
	A forest data structure that contains trees of terms 
	spawned from a list of equations. Recursively 
	builds trees from each unique term in the list
	of equations, without repeating any terms.

	Parameters
	----------
	seed : List[Equation]
		The list of equations to build a forest out of
	max_height : int
		The maximum height of each tree in the forest

	Notes
	-----
	Because a term could be expanded forever, a max_height
	is required in order to guarantee termination.

	Examples
	--------
	>>> from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
	>>> from symcollab.algebra import Term_Forest
	>>> f = Function("f", 1)
	>>> g = Function("g", 1)
	>>> x = Variable("x")
	>>> y = Variable("y")
	>>> z = Variable("z")
	>>> c = Constant("c")
	
	>>> eq1 = Equation(f(x), y)
	>>> eq2 = Equation(y, g(z))
	>>> eq3 = Equation(z, c)

	>>> forest = Term_Forest([eq1, eq2, eq3], 5)
	>>> print(forest)
	f(x)
	|
	+__y
	   |
	   +__g(z)
	      |
	      +__g(c)
	z
	|
	+__c
"""
class Term_Forest:

	def __init__(self, seed: List[Equation], max_height: int):
		self.seed = seed
		self.max_height = max_height
		self.history = list()
		self.forest = list()
		self.__init_terms()
		self.tree_heights = [0] * len(self.terms)
		self.__build_forest()
	
	# Gets unique terms from the list of equations
	def __init_terms(self):
		self.terms = list()
		for eq in self.seed:
			if eq.left_side not in self.terms:
				self.terms.append(eq.left_side)
			if eq.right_side not in self.terms:
				self.terms.append(eq.right_side)

	# For every unique term, recursively build a tree
	def __build_forest(self):
		self.index = 0
		for term in self.terms:
			if term not in self.history:
				self.history.append(term)
				node = AnyNode(term=term)
				self.forest.append(node)
				self.__build_tree(node)
			self.index = self.index + 1

	# Recursively generate possible list of terms to add
	# Will not add any terms that already exist in the forest
	def __build_tree(self, node):
		nt = node.term
		children = self.__generate_terms(nt)
		for t in children:
			if t not in self.history:
				if self.tree_heights[self.index] < self.max_height:
					self.history.append(t)
					n = AnyNode(term=t, parent=node)
					if n.depth+1 > self.tree_heights[self.index]:
						self.tree_heights[self.index] = n.depth + 1
					self.__build_tree(n)

	# Recursively generate every possible way to rewrite a term
	def __generate_terms(self, nt: Term) -> List[Term]:
		children = list()
		for eq in self.seed:
			left = eq.left_side
			right = eq.right_side
			other = None
			if nt == left:
				other = right
			elif nt == right:
				other = left
			if other != None:
				children.append(other)
		if isinstance(nt, FuncTerm):
			f = nt.function
			args = nt.arguments
			for t in args:
				t_children = self.__generate_terms(t)
				for _o in t_children:
					new_args = [_o if i==t else i for i in args]
					rw = FuncTerm(f, new_args)
					children.append(rw)

		return children

	# display each tree in the forest
	def __str__(self):
		forest_str = ""
		for n in self.forest:
			for pre, _, node in RenderTree(n):
				forest_str += ("%s%s" % (pre, node.term)) + "\n"

		return forest_str

	# Print out a descritpion of the attributes of the forest 
	def describe(self) -> str:
		description = "There are " + str(len(self.terms)) + " unique terms in the seed that spawned the forest:\n"
		description = description + str(self.terms) + "\n\n"
		description = description + "The forest contains " + str(len(self.forest)) + " root terms:\n"
		_terms = list()
		for node in self.forest:
			_terms.append(str(node.term))
		description = description + str(_terms) + "\n\n"
		description = description + "The forest contains " + str(len(self.history)) + " unique terms:\n"
		description = description + str(self.history) + "\n"
		return description