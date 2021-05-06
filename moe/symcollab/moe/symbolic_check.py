"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Tuple, Dict, List, Optional, Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symcollab.xor import xor
from symcollab.xor.structure import Zero, is_zero
from copy import deepcopy
from anytree import AnyNode, RenderTree

f = Function("f", 1)
zero = Zero()

#def moo_symbolic_check():

"""
Given a set of equations, remove any in the form of f(t) = 0, returning
the new list
"""
def elim_f(top_f_terms: Set[Equation]) -> Set[Equation]:
	elim_f_set = deepcopy(top_f_terms)
	for eq in top_f_terms:
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == f and is_zero(eq.right_side):
				elim_f_set.remove(eq)
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == f and is_zero(eq.left_side):
				elim_f_set.remove(eq)

	return elim_f_set

"""
Given a set of equations, remove those in the form of 
C_{p,i-a} xor C_{q, j-a} = 0, where i!=j
"""
def elim_c(top_f_terms: Set[Equation]) -> Set[Equation]:
	elim_c_set = deepcopy(top_f_terms)
	c = Function("C", 3)
	p = Constant('p')
	q = Constant('q')
	i = Constant('i')
	j = Constant('j')
	for eq in top_f_terms:
		args = None
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == xor and is_zero(eq.right_side):
				args = eq.left_side._arguments
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == xor and is_zero(eq.left_side):
				args = eq.right_side._arguments
		if args!= None and len(args) == 2:
			t1 = args[0]
			t2 = args[1]
			t1_is_c = False
			t2_is_c = False
			a1 = None
			a2 = None
			if t1.function == c and t2.function == c:
				cargs1 = t1._arguments
				cargs2 = t2._arguments
				if len(cargs1) == 3 and len(cargs2) == 3:
					a1 = cargs1[2]
					a2 = cargs2[2]
					if cargs1[0] == p and cargs1[1] == i:
						t1_is_c = True
						if cargs2[0] == q and cargs2[1] == j:
							t2_is_c = True
					elif cargs1[0] == q and cargs1[1] == j:
						t1_is_c = True
						if cargs2[0] == p and cargs2[1] == i:
							t2_is_c = True
			if a1 == a2:
				elim_c_set.remove(eq)
	return elim_c_set

root_node = None

def occurs_check(equations: Set[Equation], max_depth: int) -> bool:
	cycle = False
	terms : Set[Term] = set()
	for eq in equations:
		left = eq.left_side
		right = eq.right_side
		terms.add(left)
		terms.add(right)

	for term in terms:
		print("building tree for ", term)
		root_node = AnyNode(term=term, parent=None)
		depth = build_tree(root_node, term, equations, 1) + 1
		print(RenderTree(root_node))
		print(depth)

	return False
#
def build_tree(node: AnyNode, term: Term, equations: Set[Equation], depth: int) -> int:
	build_tree.depth = depth
	cur = node
	for eq in equations:
		left = eq.left_side
		right = eq.right_side
		if (cur.term == left or cur.term == right) and \
		 (cur.parent == None or cur.parent != None and cur.parent.term != left and cur.parent.term != right):
			if cur.term == left:
				other = right
			else:
				other = left
			node = AnyNode(term=other, parent=cur)
			#print("n_d: ", node.depth, " d ", depth)
			if node.depth > build_tree.depth:
			#	print("eeee")
				build_tree.depth = node.depth
				#print(depth)
			#print(depth)
			build_tree(node, other, equations, build_tree.depth)
	return build_tree.depth


"""
def pick_f():

def pick_c():

def pick_fail():
"""