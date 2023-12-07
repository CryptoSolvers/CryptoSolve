"""
Experiment with Kim on 12/05/2023
Two-Stage with flat terms and rules
"""

from copy import deepcopy
from collections import defaultdict
from functools import lru_cache
from typing import List, Set, Optional, Tuple, Dict

import itertools

from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, SubstituteTerm, unravel, Constant
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
	def __init__(self, data: Set[Equation], ruleList):
		self.id = None
		self.c = None
		self.a1 = None
		self.a2 = None
		self.rc = None
		self.lc = None
		self.mc = None
		self.data = data
		self.var_count = None
		self.ruleList = ruleList
	def __str__(self):
		return f"MutateNode(data={self.data})"

# Helper function to retrieve a set of variables from a set of equations
def helper_gvs(U: Set[Equation]) -> Set[Variable]:
	# V = set()
	V = OrderedSet()
	for e in U:
		V = V.union(get_vars_uo(e.left_side))
		V = V.union(get_vars_uo(e.right_side))
	return(V)


def trace_check(v1: Variable, v2: Variable, equations: Set[Equation]) -> bool:
	"""
	Check to see if there is a cycle of
	equality between two variables
	"""
	assert isinstance(v1, Variable) and isinstance(v2, Variable)
	if v1 == v2:
		return True

	Q: List[Tuple[Set[Equation], List[Term]]] = []

	for equation in equations:
		# Ignore trivial equalities
		if equation.left_side == equation.right_side:
			continue

		if equation.left_side == v1:
			Q.append((
				equations - {equation},
				[equation.right_side]
			))
		elif equation.right_side == v1:
			Q.append((
				equations - {equation},
				[equation.left_side]
			))


	while len(Q) > 0:
		c_equations, c_path = Q.pop(0)

		last_term = c_path[-1]
		if last_term == v2:
			return True

		for ce in c_equations:
			# Ignore trivial equalities
			if ce.left_side == ce.right_side:
				continue

			if ce.left_side == last_term:
				Q.append((c_equations - {ce}, c_path + [ce.right_side]))
			elif ce.right_side == last_term:
				Q.append((c_equations - {ce}, c_path + [ce.left_side]))

	return False


#Rules

def match_mutation(U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	for e1, e2 in itertools.product(U, U):
		# Skip if e1 and e2 are the same
		if e1 == e2:
			continue

		# # TODO: Enforce some ordering...
		# if poe(e1) > poe(e2):
		# 	continue

		# Variables on lhs are the same and right side are FuncTerms
		lhs1 = e1.left_side; rhs1 = e1.right_side
		lhs2 = e2.left_side; rhs2 = e2.right_side
		if isinstance(lhs1, Variable) and lhs1 == lhs2:
			if isinstance(rhs1, FuncTerm) and isinstance(rhs2, FuncTerm):
				return (e1, e2)

	return None
#Mutation Rule ID
def match_mutation_rule1(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	return e

def mutation_rule1(U: Set[Equation], es: Tuple[Equation, Equation],  var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]

	# print("Applied ID")

	#Create the mutations
	U = U - {e2}

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y1, z1))
	m1.add(Equation(y2, z2))
	U = U.union(m1)

	return U

#Mutation Rule C
def match_mutation_rule2(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	return e

def mutation_rule2(U: Set[Equation], es: Tuple[Equation, Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]

	# print("Applied C")

	#Create the 7 possible mutations
	U = U - {e2}

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y1, z2))
	m1.add(Equation(y2, z1))
	U = U.union(m1)

	return U

#Mutation Rule A1
def match_mutation_rule3(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	if e is None:
		return None
	e1, e2 = e
	rhs1 = e1.right_side; rhs2 = e2.right_side
	y1 = rhs1.arguments[0]; z2 = rhs2.arguments[1]
	if not trace_check(y1, z2, U):
		return e
	return None


def mutation_rule3(U: Set[Equation], es: Tuple[Equation, Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]
	assert y1 != z2

	# print("+++++++++Applying A1++++++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e2}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	f = e1.right_side.function

	# m1 =  set()
	m1 = OrderedSet()
	m1.add(Equation(y1, f(z1, v1)))
	m1.add(Equation(z2, f(v1, y2)))
	U = U.union(m1)
	# print("--------------After Applying A1-------------------")
	# print(U)
	# print("--------------------------------------------------")

	return U

#Mutation Rule A2
def match_mutation_rule4(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	if e is None:
		return None
	e1, e2 = e
	rhs1 = e1.right_side; rhs2 = e2.right_side
	y2 = rhs1.arguments[1]; z1 = rhs2.arguments[0]
	if not trace_check(y2, z1, U):
		return e
	return None


def mutation_rule4(U: Set[Equation], es: Tuple[Equation, Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]
	assert y2 != z1

	# print("+++++++++Applying A2++++++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++++")


	#Create the 7 possible mutations
	U = U - {e1}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	f = e1.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y2, f(v1, z2)))
	m1.add(Equation(z1, f(y1, v1)))
	U = U.union(m1)

	# print("--------------After Applying A2-------------------")
	# print(U)
	# print("--------------------------------------------------")
	return U

#Mutation Rule RC

def match_mutation_rule5(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	if e is None:
		return None
	e1, e2 = e
	rhs1 = e1.right_side
	rhs2 = e2.right_side
	y1 = rhs1.arguments[0]; z1 = rhs2.arguments[0]
	if not trace_check(y1, z1, U):
		return e

	return None

def mutation_rule5(U: Set[Equation], es: Tuple[Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]
	assert y1 != z1

	# print("++++++++++++Applying RC++++++++++")
	# print(e)
	# print(U)
	# print("+++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e2}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	f = e1.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y1, f(v1, z2)))
	m1.add(Equation(z1, f(v1, y2)))
	U = U.union(m1)

	# print("----------After applying RC--------------")
	# print(U)
	# print("-----------------------------------------")

	return U

#Mutation Rule LC
def match_mutation_rule6(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	if e is None:
		return None
	e1, e2 = e
	rhs1 = e1.right_side; rhs2 = e2.right_side
	y2 = rhs1.arguments[1]; z2 = rhs2.arguments[1]
	if not trace_check(y2, z2, U):
		return (e1, e2)

	return None

def mutation_rule6(U: Set[Equation], es: Tuple[Equation, Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]
	assert y2 != z2

	# print("++++++++++Applying LC+++++++++++++")
	# print(e)
	# print(U)
	# print("+++++++++++++++++++++++++++++++++")


	#Create the 7 possible mutations
	U = U - {e2}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	f = e1.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y2, f(z1, v1)))
	m1.add(Equation(z2, f(y1, v1)))
	U = U.union(m1)

	# print("---------After applying LC---------------")
	# print(U)
	# print("-----------------------------------------")
	return U

#Mutation Rule MC
def match_mutation_rule7(e: Optional[Tuple[Equation, Equation]], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	if e is None:
		return None
	e1, e2 = e
	rhs1 = e1.right_side; rhs2 = e2.right_side
	to_check = [
		(rhs1.arguments[0], rhs1.arguments[1]),
		(rhs2.arguments[0], rhs2.arguments[1]),
		(rhs1.arguments[0], rhs2.arguments[0]),
		(rhs1.arguments[0], rhs2.arguments[1]),
		(rhs1.arguments[1], rhs2.arguments[0]),
		(rhs1.arguments[1], rhs2.arguments[1])
	]
	# NOTE: Temporary condition until conditions are worked out
	if not any(v1 == v2 for v1, v2 in to_check):
	# if not any(trace_check(v1, v2, U) for v1, v2 in to_check):
		return e
	return None


def mutation_rule7(U: Set[Equation], es: Tuple[Equation, Equation], var_count: List[int]) -> Set[Equation]:
	e1, e2 = es
	assert e1 in U and e2 in U
	assert isinstance(e1.left_side, Variable) and e1.left_side == e2.left_side
	assert isinstance(e1.right_side, FuncTerm) and isinstance(e2.right_side, FuncTerm)
	y1 = e1.right_side.arguments[0]
	y2 = e1.right_side.arguments[1]
	z1 = e2.right_side.arguments[0]
	z2 = e2.right_side.arguments[1]
	assert len(get_vars_uo(e1.right_side) | get_vars_uo(e2.right_side)) == 4

	# print("++++++++++Applying MC+++++++++++++")
	# print(e)
	# print(U)
	# print("++++++++++++++++++++++++++++++++++")

	#Create the 7 possible mutations
	U = U - {e2}

	# Generate fresh variables
	v1 = fresh_var(var_count)
	v2 = fresh_var(var_count)
	v3 = fresh_var(var_count)
	v4 = fresh_var(var_count)
	f = e1.right_side.function

	# m1 = set()
	m1 = OrderedSet()
	m1.add(Equation(y1, f(v1, v2)))
	m1.add(Equation(y2, f(v3, v4)))
	m1.add(Equation(z1, f(v1, v3)))
	m1.add(Equation(z2, f(v2, v4)))
	U = U.union(m1)

	# print("--------After applying MC------------")
	# print(U)
	# print("-------------------------------------")

	return U


##########################################################
############# S Rules                     ################
##########################################################


def poe(equation: Equation) -> int:
	"""
	Returns the number of the subscript of the
	lateset fresh variable
	"""
	V = helper_gvs({equation})
	max_num = 0
	for v in V:
		if v.symbol.startswith("v_"):
			num = int(v.symbol.split("_")[1])
			max_num = max(max_num, num)
	return max_num


def variable_replacement(equations) -> Set[Equation]:
	"""
	{x = t} U P => {x = t} U P{x -> t}
	if x and t are variables, x \ne t and x \in Vars(P)
	"""
	matched_equation: Optional[Equation] = None

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		if isinstance(lhs, Variable) and isinstance(rhs, Variable) and lhs != rhs:
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
		if isinstance(lhs, Variable) and lhs not in VS1 and lhs not in get_vars_uo(rhs):
			other_variables = helper_gvs(equations - {equation})
			if lhs not in other_variables:
				matched_equation = equation
				break
				# V = get_vars_uo(rhs)
				# if all(v not in other_variables for v in V ):
				# 	matched_equation = equation
				# 	break

	if matched_equation is None:
		return equations

	return equations - {matched_equation}

def s_rules(U: Set[Equation], VS1: Set[Variable]):
	"""
	S Rules
	"""
	# print("Before S Rules:", U)
	# Utemp = set()
	Utemp = OrderedSet()
	while (Utemp != U):
		Utemp = U
		if occurs_check(U):
			return set()
		U = variable_replacement(U)

		U = eqe(U, VS1)
		U = delete_trivial(U)
		# if occurs_check(U):
		# 	return set()
		# U = eqe(U, VS1)

		# For slow debugging
		# print(U)
		# import time
		# time.sleep(1)

	# print("After S Rules:", U)
	return U

#helper function to check for linear term
def linear(t: Term) -> bool:
	V = get_vars(t)
	# False if there are duplicate variables within a term
	return len(V) == len(set(V))

def prune(equations: Set[Equation], VS1: Set[Variable], ignore_vars: Set[Variable]) -> bool:
	VS2 = helper_gvs(equations)
	VS2 = VS2.difference(VS1)
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in ignore_vars and e.left_side in VS2:
				if not linear(e.right_side):
					return True
	return False

def delete_trivial(equations) -> Set[Equation]:
	new_equations = set()
	for e in equations:
		if e.left_side != e.right_side:
			new_equations.add(e)
	return new_equations

def s_rules_with_prune(U: Set[Equation], VS1: Set[Variable]):
	"""
	S Rules
	"""
	# print("Before S Rules:", U)
	# Utemp = set()
	Utemp = OrderedSet()
	while (Utemp != U):
		Utemp = U
		if prune(U, VS1, set()):
			# print("[Stage 3] Prune rule applied")
			return set()
		
		if occurs_check(U):
			return set()
		
		U = variable_replacement(U)
		U = eqe(U, VS1)
		U = delete_trivial(U)


		# if occurs_check(U):
		# 	return set()
		# U = eqe(U, VS1)

		# For slow debugging
		# print(U)
		# import time
		# time.sleep(1)

	# print("After S Rules:", U)
	return U


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
	mutate_eq = match_mutation(dcopy)

	e = match_mutation_rule1(mutate_eq, cn.data)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		# print("Applying ID")
		dcopy = deepcopy(cn.data)
		new_eqs = mutation_rule1(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.id = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["ID"])
			cn.id.var_count = var_count
			nextBranch.append((cn.id, level + 1))

	e = match_mutation_rule2(mutate_eq, cn.data)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		# print("Applying C")
		dcopy = deepcopy(cn.data)
		new_eqs = mutation_rule2(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.c = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["C"])
			cn.c.var_count = var_count
			nextBranch.append((cn.c, level + 1))

	e = match_mutation_rule3(mutate_eq, cn.data)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		dcopy = deepcopy(cn.data)
		new_eqs = mutation_rule3(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.a1 = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["A_RIGHT"])
			cn.a1.var_count = var_count
			nextBranch.append((cn.a1, level + 1))

	e = match_mutation_rule4(mutate_eq, cn.data)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		dcopy = deepcopy(cn.data)
		new_eqs = mutation_rule4(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.a2 = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["A_LEFT"])
			cn.a2.var_count = var_count
			nextBranch.append((cn.a2, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule5(mutate_eq, dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule5(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.rc = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["RC"])
			cn.rc.var_count = var_count
			nextBranch.append((cn.rc, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule6(mutate_eq, dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule6(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.lc = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["LC"])
			cn.lc.var_count = var_count
			nextBranch.append((cn.lc, level + 1))

	dcopy = deepcopy(cn.data)
	e = match_mutation_rule7(mutate_eq, dcopy)
	var_count = deepcopy(cn.var_count)
	if e is not None:
		new_eqs = mutation_rule7(dcopy, e, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			cn.mc = MutateNode(new_eqs, deepcopy(cn.ruleList) + ["MC"])
			cn.mc.var_count = var_count
			nextBranch.append((cn.mc, level + 1))

	Tree[level + 1].extend([c for c, _ in nextBranch])
	Q.extend(nextBranch)


def solved_form(U: Set[Equation]) -> bool:
	V: List[Variable] = []
	# Make sure every equation starts with a variable
	# on the left side.
	for e in U:
		if not isinstance(e.left_side, Variable):
			return False
		V.append(e.left_side)

	# Check for duplicate assignments
	if len(V) != len(set(V)):
		return False

	if occurs_check(U):
		return False

	return True

Tree = None

def build_tree(U: Set[Equation], var_count: List[int], single_sol: bool):
	global Tree

	################ Step 0.5 #####################
	# Translate the problem to one where there are no duplicate variables
	original_variables = helper_gvs(U)
	# New Var -> Old Var
	dedup_var_map: Dict[Variable, Variable] = {}
	def dedup_fresh_var(basename: str):
		"""Create new variable not in original variables or dedup_var_map"""
		within_dedup_map = lambda x : any((x == v.symbol for v in dedup_var_map.keys()))
		while basename in original_variables or within_dedup_map(basename):
			basename = basename + "_1"
		return Variable(basename)
	def dedup_term(t: Term):
		"""Make each variable in the term a fresh variable"""
		if isinstance(t, Constant):
			return deepcopy(t)

		if isinstance(t, Variable):
			new_t = dedup_fresh_var(t.symbol)
			dedup_var_map[new_t] = t
			return new_t

		# Assume FuncTerm
		new_args = []
		for arg in t.arguments:
			new_args.append(dedup_term(arg))
		return t.function(*new_args)
	def dedup(U: Set[Equation]):
		"""Make every variable within the set of equations a fresh variable"""
		new_U = set()
		for equation in U:
			new_left_side = dedup_term(equation.left_side)
			new_right_side = dedup_term(equation.right_side)
			new_U.add(Equation(new_left_side, new_right_side))
		return new_U

	distinct_u = dedup(U)
	original_variables_distinct = helper_gvs(distinct_u)


	############### Step 1 ####################
	root = MutateNode(distinct_u, [])
	root.var_count = var_count
	step_1_solutions: List[Set[Equation]] = []
	step_1_varcounts = []
	Q = [(root, 0)]
	Tree = defaultdict(list)
	Tree[0] = [root]
	current_level = 0

	while 0 < len(Q):
		cn, level = Q.pop(0)

		if level > current_level:
			print("=" * 5)
			print("Layer", current_level)
			# Remove dead branches
			new_last_branch = []
			occurs_check_nodes = 0
			for node in Tree[current_level]:
				if len(node.data) > 0:
					new_last_branch.append(node)
				else:
					occurs_check_nodes += 1
			Tree[current_level] = new_last_branch
			print("Occurs check on layer:", occurs_check_nodes)
			print("Remaining nodes on layer:", len(Tree[current_level]))

			last_node = Tree[current_level][-1]
			print("Last Node:", last_node.data)
			print("Length of last node:", len(last_node.data))
			print("Rules for last node:", last_node.ruleList)
			print("=" * 5)
			current_level = level

		#Apply S rules - mutate
		cn.data = s_rules(cn.data, original_variables_distinct)
		if len(cn.data) > 0:
			if solved_form(cn.data):
				step_1_solutions.append(cn.data)
				step_1_varcounts.append(cn.var_count)
			else:
				apply_mutation_rules(cn, Q, Tree, level)


	print("====================")
	print("STAGE 1 COMPLETE")
	print("Number of Stage 1 Psuedo-Solutions:", len(step_1_solutions))
	print("===================")

	############## Step 1.5 #####################
	# Undo deduplication
	def undo_dedup_term(t: Term):
		"""Make each variable in the term a fresh variable"""
		if isinstance(t, Constant):
			return deepcopy(t)

		if isinstance(t, Variable):
			if t not in dedup_var_map:
				# This is when its a fresh variable
				return deepcopy(t)
			# Otherwise reverse dedup
			return deepcopy(dedup_var_map[t])

		# Assume FuncTerm
		new_args = []
		for arg in t.arguments:
			new_args.append(undo_dedup_term(arg))
		return t.function(*new_args)
	def undo_dedup(U: Set[Equation]):
		"""Make every variable within the set of equations a fresh variable"""
		new_U = set()
		for equation in U:
			new_left_side = undo_dedup_term(equation.left_side)
			new_right_side = undo_dedup_term(equation.right_side)
			new_U.add(Equation(new_left_side, new_right_side))
		return new_U
	step_1_5_solutions = [undo_dedup(equation) for equation in step_1_solutions]

	# ################### Step 2 ###################
	# Apply S rules on converted equations
	Sol: List[Set[Equation]] = []
	# print("# Equations after Stage 1.5 =", len(step_1_5_solutions))
	for i, s in enumerate(step_1_5_solutions):
		root = MutateNode(s, [])
		root.var_count = step_1_varcounts[i]
		Q = [(root, 0)]
		Tree = defaultdict(list)
		Tree[0] = [root]
		current_level = 0
		while len(Q) > 0:

			cn, level = Q.pop(0)

			if level > current_level:
				print("=" * 5)
				print("Layer", current_level)
				# Remove dead branches
				new_last_branch = []
				occurs_check_nodes = 0
				for node in Tree[current_level]:
					if len(node.data) > 0:
						new_last_branch.append(node)
					else:
						occurs_check_nodes += 1
				Tree[current_level] = new_last_branch
				print("Occurs check on layer:", occurs_check_nodes)
				print("Remaining nodes on layer:", len(Tree[current_level]))

				last_node = Tree[current_level][-1]
				print("Last Node:", last_node.data)
				print("Length of last node:", len(last_node.data))
				print("Rules for last node:", last_node.ruleList)
				print("=" * 5)
				current_level = level


			#Apply S rules - mutate
			cn.data = s_rules_with_prune(cn.data, original_variables)
			if len(cn.data) > 0:
				if solved_form(cn.data):
					Sol.append(cn.data)
					if single_sol:
						print("Total Layers Computed:", current_level)
						return Sol
				else:
					apply_mutation_rules(cn, Q, Tree, level)

		print("Total Layers Computed:", current_level)
				

	return Sol

def synt_ac_unif3(U: Set[Equation], single_sol: bool = True):
	var_count = [0]
	# VS1 = helper_gvs(U)
	U, var_count[0] = flat(U, var_count[0])
	# N1 = MutateNode(U, [])
	# N1.var_count = var_count
	res = build_tree(U, var_count, single_sol)
	# res = build_tree(N1, VS1, single_sol)
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
