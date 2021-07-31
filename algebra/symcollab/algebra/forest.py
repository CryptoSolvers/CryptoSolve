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
	In some cases, a term could be expanded forever, 
	thereforea max_height is required in order to 
	guarantee termination.

	Examples
	--------
	>>> from symcollab.algebra import *
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
from copy import deepcopy
from functools import partial
from typing import Tuple, Dict, List, Optional, Set
from anytree import AnyNode, RenderTree
from .term import Equation, Term, FuncTerm

class Term_Forest:

	def __init__(self, seed: List[Equation], max_height: int):
		self.seed = seed
		self.max_height = max_height
		self.__history = list()
		self.forest = list()
		self.__init_terms()
		self.__tree_heights = [0] * len(self.terms)
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
		self.__index = 0
		for term in self.terms:
			if term not in self.__history:
				self.__history.append(term)
				node = AnyNode(term=term)
				self.forest.append(node)
				self.__build_tree(node)
			self.__index += 1

	# Recursively generate possible list of terms to add
	# Will not add any terms that already exist in the forest
	def __build_tree(self, node):
		nt = node.term
		children = self.__generate_terms(nt)
		for t in children:
			if t not in self.__history:
				if self.__tree_heights[self.__index] < self.max_height:
					self.__history.append(t)
					n = AnyNode(term=t, parent=node)
					if n.depth+1 > self.__tree_heights[self.__index]:
						self.__tree_heights[self.__index] = n.depth + 1
					self.__build_tree(n)
				else:
					self.__tree_heights[self.__index] = self.max_height

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
					# replace the argument t with the term it is equal to
					new_args = [_o if i==t else i for i in args]
					rw = FuncTerm(f, new_args)
					children.append(rw)

		return children

	# display each node in each tree in the forest
	def __repr__(self):
		forest_str = ""
		index = 0
		for n in self.forest:
			index += 1
			for pre, _, node in RenderTree(n):
				forest_str += ("%s%s" % (pre, node)) + "\n"
			forest_str += "height: " + str(self.get_height(n)) + "\n"

		return forest_str

	# display each term in each tree in the forest
	def __str__(self):
		forest_str = ""
		index = 0
		for n in self.forest:
			index += 1
			for pre, _, node in RenderTree(n):
				forest_str += ("%s%s" % (pre, node.term)) + "\n"
			forest_str += "height: " + str(self.get_height(n)) + "\n"

		return forest_str

	def __deepcopy__(self, memo):
		new_forest =  Term_Forest(deepcopy(self.seed), deepcopy(self.max_height))
		memo[id(self)] = new_forest
		dcopy = partial(deepcopy, memo=memo)
		return new_forest


	# Can compare forests via length, <, <=, >, >=, ==, !=
	def __lt__(self, other):
		return len(self.forest) < len(other.forest)

	def __le__(self, other):
		return self == other or self < other

	def __gt__(self, other):
		return len(self.forest) > len(other.forest)

	def __ge__(self, other):
		return self == other or self > other

	# determines if two forests are the same if each contain the same trees
	def __eq__(self, other):
		trees = len(self.forest)
		if trees != len(other.forest):
			return False
		matches = 0
		for _t in self.forest:
			for _o in other.forest:
				res = Term_Forest.tree_compare(_t, _o)
				if res == 0:
					matches += 1
		return matches == trees

	def __ne__(self, other):
		return not self == other

	def __contains__(self, term):
		return term in self.__history

	def __hash__(self):
		_str = str(self.max_height)
		for eq in self.seed:
			_str += str(eq)
		return hash(_str)

	# given one of the root terms in the forest and return the height of that tree
	def get_height(self, root: AnyNode) -> int:
		index = 0
		for t in self.terms:
			if root.term == t:
				return self.__tree_heights[index]
			index += 1

	# returns 0 if both trees contain the same nodes
	# returns -1 if the length of root1 is less than the length of root2
	# returns 1 if the length of root1 is more than the length of root2
	@staticmethod
	def tree_compare(root1, root2) -> int:
		nodes = Term_Forest.get_tree(root1)
		_nodes = Term_Forest.get_tree(root2)
		if set(nodes) == set(_nodes):
			return 0
		return -1 if len(nodes) < len(_nodes) else 1

	# return a list of all of the nodes in a given tree
	@staticmethod
	def get_tree(root: AnyNode) -> List[Term]:
		tree = list()
		for pre, _, node in RenderTree(root):
			tree.append(node.term)
		return tree

	# Print out a description of the attributes of the forest 
	def describe(self) -> str:
		description = "There are " + str(len(self.terms)) + " unique terms in the seed that spawned the forest:\n"
		description += str(self.terms) + "\n\n"
		description += "The forest contains " + str(len(self.forest)) + " root terms:\n"
		_terms = list()
		for node in self.forest:
			_terms.append(str(node.term))
		description += str(_terms) + "\n\n"
		description += "The forest contains " + str(len(self.__history)) + " unique terms:\n"
		description += str(self.__history) + "\n"
		return description
