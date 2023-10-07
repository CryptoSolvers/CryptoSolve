from copy import deepcopy
from collections import defaultdict
from functools import lru_cache
from typing import List, Set, Optional, Tuple

import itertools

from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, SubstituteTerm, unravel
)
from symcollab.Unification.common import (
    occurs_check, function_clash
)
from symcollab.Unification.flat import flat

# OrderedSet makes it so that the outputs are deterministic
# this is at a great expense of execution speed.
# Leave in when testing, remove when done.
from symcollab.Unification.orderedset import OrderedSet
OrderedSet = set

@lru_cache(maxsize=1024)
def get_vars_uo(t: Term):
	"""Recursively get unique and ordered variables"""
	if isinstance(t, Variable):
		return OrderedSet([t])

	l = OrderedSet()
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l |= get_vars_uo(i)

	return l

def fresh_var(var_count: List[int]) -> Variable:
	name = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	return Variable(name)

#Tree
class MutateNode:
	def __init__(self, data: Set[Equation]):
		self.id = None
		self.c = None
		self.a1 = None
		self.a2 = None
		self.rc = None
		self.lc = None
		self.mc = None
		self.data = data
		self.var_count = None
	def __str__(self):
		return f"MutateNode(data={self.data})"

#helper function to check for linear term
def linear(t: Term) -> bool:
	V = get_vars_uo(t)
	# False if there are duplicate variables within a term
	return len(V) == len(set(V))

# Helper function to retrieve a set of variables from a set of equations
def helper_gvs(U: Set[Equation]) -> Set[Variable]:
	# V = set()
	V = OrderedSet()
	for e in U:
		V = V.union(get_vars_uo(e.left_side))
		V = V.union(get_vars_uo(e.right_side))
	return(V)


#Rules

#Mutation Rule ID
def match_mutation_rule1(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			return e
	return None

def mutation_rule1(U: Set[Equation], e: Equation,  var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]

	# print("Applied ID")

	#Create the mutations
	U = U - {e}

	# Generate Fresh Variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, v1))
	m1.add(Equation(t1, v1))
	m1.add(Equation(s2, v2))
	m1.add(Equation(t2, v2))
	U = U.union(m1)

	return U


#Mutation Rule C
def match_mutation_rule2(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			return e
	return None

def mutation_rule2(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]

	# print("Applied C")

	#Create the 7 possible mutations
	U = U - {e}

	# Generate Fresh Variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, v1))
	m1.add(Equation(t1, v2))
	m1.add(Equation(s2, v2))
	m1.add(Equation(t2, v1))
	U = U.union(m1)

	return U

#Mutation Rule A1
def match_mutation_rule3(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(lhs, FuncTerm) and isinstance(rhs, FuncTerm):
			s1 = lhs.arguments[0]; t2 = rhs.arguments[1]
			if s1 != t2:
				return e
	return None

def mutation_rule3(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	assert s1 != t2

	# print("+++++++++Applying A1++++++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	f = e.right_side.function

	# m1 =  set()
	m1 = OrderedSet()
	m1.add(Equation(s1, f(v1, v2)))
	m1.add(Equation(s2, v3))
	m1.add(Equation(t1, v1))
	m1.add(Equation(t2, f(v2, v3)))
	U = U.union(m1)
	# print("--------------After Applying A1-------------------")
	# print(U)
	# print("--------------------------------------------------")

	return U

#Mutation Rule A2
def match_mutation_rule4(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			s2 = lhs.arguments[1]; t1 = rhs.arguments[0]
			if s2 != t1:
				return e
	return None

def mutation_rule4(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	assert s2 != t1

	# print("+++++++++Applying A2++++++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++++")


	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	f = e.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, v1))
	m1.add(Equation(s2, f(v2, v3)))
	m1.add(Equation(t1, f(v1, v2)))
	m1.add(Equation(t2, v3))
	U = U.union(m1)

	# print("--------------After Applying A2-------------------")
	# print(U)
	# print("--------------------------------------------------")
	return U

#Mutation Rule RC

def match_mutation_rule5(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			s1 = lhs.arguments[0]; t1 = rhs.arguments[0]
			if s1 != t1:
				return e
	return None

def mutation_rule5(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	assert s1 != t1

	# print("++++++++++++Applying RC++++++++++")
	# print(e)
	# print(U)
	# print("+++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	f = e.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, f(v1, v2)))
	m1.add(Equation(s2, v3))
	m1.add(Equation(t1, f(v1, v3)))
	m1.add(Equation(t2, v2))
	U = U.union(m1)

	# print("----------After applying RC--------------")
	# print(U)
	# print("-----------------------------------------")

	return U

#Mutation Rule LC
def match_mutation_rule6(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			s2 = lhs.arguments[1]; t2 = rhs.arguments[1]
			if s2 != t2:
				return e

	return None

def mutation_rule6(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	assert s2 != t2

	# print("++++++++++Applying LC+++++++++++++")
	# print(e)
	# print(U)
	# print("+++++++++++++++++++++++++++++++++")


	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	f = e.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, v1))
	m1.add(Equation(s2, f(v2, v3)))
	m1.add(Equation(t1, v2))
	m1.add(Equation(t2, f(v1, v3)))
	U = U.union(m1)

	# print("---------After applying LC---------------")
	# print(U)
	# print("-----------------------------------------")
	return U

#Mutation Rule MC
def match_mutation_rule7(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			# TODO: Is this condition complete?
			# NOTE: This is a distinct variable check
			if len(get_vars_uo(e.left_side) | get_vars_uo(e.right_side)) == 4:
				return e

	return None

def mutation_rule7(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	assert len(get_vars_uo(e.right_side) | get_vars_uo(e.left_side)) == 4

	# print("++++++++++Applying MC+++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	v4 = fresh_var(var_count)
	f = e.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(s1, f(v1, v2)))
	m1.add(Equation(s2, f(v3, v4)))
	m1.add(Equation(t1, f(v1, v3)))
	m1.add(Equation(t2, f(v2, v4)))
	U = U.union(m1)

	# print("--------After applying MC------------")
	# print(U)
	# print("-------------------------------------")

	return U


##########################################################
############# S Rules                     ################
##########################################################

def match_merge(equations: Set[Equation], restricted_vars: Set[Variable]) -> Optional[Tuple[Equation, Equation]]:
	U_list = list(equations)

	for i, j in itertools.product(range(len(U_list)), range(len(U_list))):
		# Don't merge an equation with itself
		# Comparing indices, since it's expensive to compare terms
		if i == j:
			continue

		e1 = U_list[i]; e2 = U_list[j]

		# Conditions for merge
		matching_left_variable = isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
		right_sides_not_variable = not isinstance(e1.right_side, Variable) and not isinstance(e2.right_side, Variable)
		not_restricted = e1.left_side not in restricted_vars

		if matching_left_variable and right_sides_not_variable and not_restricted:
			return (e1, e2)

	return None

def merge(equations: Set[Equation], matched_equations: Tuple[Equation, Equation], restricted_vars: Set[Variable]) -> Set[Equation]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x is a variable and s and t are not variables
	Returns new set of equations and whether merge was applied
	"""
	e1, e2 = matched_equations
	matching_left_variable = isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	right_sides_not_variable = not isinstance(e1.right_side, Variable) and not isinstance(e2.right_side, Variable)
	not_restricted = e1.left_side not in restricted_vars
	assert matching_left_variable and right_sides_not_variable and not_restricted

	remove_equations = {e2}
	add_equations = {Equation(e1.right_side, e2.right_side)}
	new_equations = (equations - remove_equations).union(add_equations)
	return new_equations


def orient_andrew(equations, VS1: Set[Variable]) -> Set[Equation]:
	# new_equations = set()
	new_equations = OrderedSet()

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		# If only right side is a variable -> Flip
		if not isinstance(lhs, Variable) and isinstance(rhs, Variable):
			new_equations.add(Equation(
                  rhs, lhs
             ))
		# If both sides are variables and right_side only from og problem -> flip
		elif isinstance(lhs, Variable) and isinstance(rhs, Variable) and \
			rhs in VS1 and lhs not in VS1:
			new_equations.add(Equation(
				rhs, lhs
			))
		else:
			new_equations.add(equation)
	return new_equations


def var_rep_andrew(equations) -> Set[Equation]:
	matched_equation: Optional[Equation] = None

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		not_in_right_side = lhs not in get_vars(rhs)
		if isinstance(lhs, Variable) and not_in_right_side:
			rest_vars = helper_gvs(equations - {equation})
			if lhs in rest_vars:
				matched_equation = equation
				break

	# If no equations are found return early
	if matched_equation is None:
		return equations

	# Create the new substitution
	new_sub = SubstituteTerm()
	new_sub.add(matched_equation.left_side, matched_equation.right_side)

	# Apply the new substitution to the set of equations
	# new_equations = set()
	new_equations = OrderedSet()

	for equation in equations - {matched_equation}:
		new_equations.add(Equation(
			unravel(equation.left_side, new_sub),
			unravel(equation.right_side, new_sub)
        ))

    # Add the matched equation to the result
	new_equations.add(matched_equation)

	return new_equations

def eqe(equations, VS1: Set[Variable]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		if isinstance(lhs, Variable) and lhs not in VS1 and lhs not in get_vars(rhs):
			if lhs not in helper_gvs(equations - {equation}):
				matched_equation = equation
				break

	if matched_equation is None:
		return equations

	return equations - {matched_equation}

def s_rules(U: Set[Equation], var_count: List[int], VS1: Set[Variable]):
	"""
	S Rules
	"""
	# print("Before S Rules:", U)
	# Utemp = set()
	Utemp = OrderedSet()
	while (Utemp != U):
		Utemp = U
		U = orient_andrew(U, VS1)
		U = var_rep_andrew(U)
		U = eqe(U, VS1)
		es = match_merge(U, set())
		if es is not None:
			U = merge(U, es, set())

		# # For slow debugging
		# print(U)
		# import time
		# time.sleep(1)

		# NOTE: Can't insert flat in loop because
		# flat and var_rep undo each other

	U, var_count[0] = flat(U, var_count[0])
	U = orient_andrew(U, VS1)
	# Check for failure before possible mutation
	if occurs_check(U):
		# print("Found Occurs check in: ")
		# print(U)
		return set()

	# print("After S Rules:", U)
	return U


# NOTE: Too slow to be useful...
# import networkx as nx
# from symcollab.algebra.dag import TermDAG
# def same_structure(U1: Set[Equation], U2: Set[Equation]):
# 	if len(U1) != len(U2):
# 		return False

# 	U2_remaining = deepcopy(U2)
# 	for e1 in U1:
# 		lhs1 = TermDAG(e1.left_side).dag
# 		rhs1 = TermDAG(e1.right_side).dag
# 		matched_e2: Optional[Equation] = None
# 		for e2 in U2_remaining:
# 			lhs2 = TermDAG(e2.left_side).dag
# 			rhs2 = TermDAG(e2.right_side).dag

# 			if nx.is_isomorphic(lhs1, rhs1):
# 				if nx.is_isomorphic(lhs2, rhs2):
# 					matched_e2 = e2
# 					break

# 			if nx.is_isomorphic(lhs1, rhs2):
# 				if nx.is_isomorphic(lhs2, rhs1):
# 					matched_e2 = e2
# 					break

# 		if matched_e2 is None:
# 			return None

# 		U2_remaining -= {matched_e2}

# 	return True


def same_structure(U1: Set[Equation], U2: Set[Equation]):
	if len(U1) != len(U2):
		return False
	return U1 == U2

def look_for_duplicates(Tree: List[List[MutateNode]], U: Set[Equation]):
	for branch in Tree:
		for node in Tree[branch]:
			if same_structure(node.data, U):
				return True
	return False

def apply_mutation_rules(
		cn: MutateNode,
		Q: List[MutateNode], Tree: List[List[MutateNode]], level: int):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[Tuple[MutateNode, int]] = []

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule1(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule1(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.id = MutateNode(new_eqs)
			cn.id.var_count = var_count
			nextBranch.append((cn.id, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule2(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule2(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.c = MutateNode(new_eqs)
			cn.c.var_count = var_count
			nextBranch.append((cn.c, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule3(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule3(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.a1 = MutateNode(new_eqs)
			cn.a1.var_count = var_count
			nextBranch.append((cn.a1, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule4(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule4(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.a2 = MutateNode(new_eqs)
			cn.a2.var_count = var_count
			nextBranch.append((cn.a2, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule5(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule5(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.rc = MutateNode(new_eqs)
			cn.rc.var_count = var_count
			nextBranch.append((cn.rc, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule6(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule6(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.lc = MutateNode(new_eqs)
			cn.lc.var_count = var_count
			nextBranch.append((cn.lc, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule7(dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule7(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.mc = MutateNode(new_eqs)
			cn.mc.var_count = var_count
			nextBranch.append((cn.mc, level + 1))

	Tree[level + 1].extend([c for c, _ in nextBranch])
	Q.extend(nextBranch)


def is_linear(U: Set[Equation], original_equations: Set[Equation]):
	VS1 = helper_gvs(original_equations)
	for eq in U:
		lhs = eq.left_side
		rhs = eq.right_side
		if isinstance(lhs, Variable) and lhs not in VS1:
			# Check to see if mapping is linear
			V = get_vars(rhs)
			if len(V) != len(set(V)):
				return False
	return True


Tree = None

def build_tree(root: MutateNode, ES1, single_sol: bool):
	global Tree
	Sol = list()
	Q = list()
	Q.append((root, 0))
	Tree = defaultdict(list)
	Tree[0] = [root]
	current_level = 0
	while 0 < len(Q):
		if current_level > 5:
			print("[WARNING] Stopping after level 5")
			return Sol

		cn, level = Q.pop(0)

		if level > current_level:
			print("=" * 5)
			print("Layer", current_level)
			print("Nodes on Layer:", len(Tree[current_level]))
			last_branch = Tree[current_level]
			for node in last_branch[-1:]:
				print("Last Node:", node.data)
				print("Length of Last Node:", len(node.data))
			print("=" * 5)
			current_level = level


		#Apply S rules - mutate
		# print("Mutate rule count", mutate_rule_count)
		cn.data = s_rules(cn.data, cn.var_count, ES1)
		if len(cn.data) > 0:
			es = match_merge(cn.data, set())
			if es is None:
				# Check failure conditions
				if not occurs_check(cn.data) and not function_clash(cn.data):
					Sol.append(cn.data)
					if single_sol:
						print("Total Layers Computed:", current_level)
						return Sol
			else:
				cn.data = merge(cn.data, es, set())
				# print('-' * 5)
				# print("About to Mutate", es)
				apply_mutation_rules(cn, Q, Tree, level)
				# print('-' * 5)

	print("Total Layers Computed:", current_level)
	return Sol

def synt_ac_unif2(U: Set[Equation], single_sol: bool = True):
	var_count = [0]
	VS1 = helper_gvs(U)
	N1 = MutateNode(U)
	N1.var_count = var_count
	res = build_tree(N1, VS1, single_sol)
	# print("Final set of equations")
	# print(res)
	final_sol = set()
	for solve in res:
		delta = SubstituteTerm()
		# Convert equations to a substitution
		for e in solve:
			try:
				delta.add(e.left_side, e.right_side)
			except:
				print("error adding substitution")
				print(solve)
				raise Exception("")
		final_sol.add(delta)

	return(final_sol)
