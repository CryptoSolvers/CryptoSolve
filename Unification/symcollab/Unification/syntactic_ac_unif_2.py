"""
Work in progress implementation of
Syntactic AC Unification
by Cornell, Marshall, and Rozek
"""
from copy import deepcopy
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from typing import List, Set, Optional, Tuple

import itertools

from symcollab.algebra import (
	Equation, Variable, FuncTerm,
	Term, SubstituteTerm, unravel
)
from symcollab.Unification.common import occurs_check
from symcollab.Unification.flat import flat

##########################################################
############# Experiment Helpers          ################
##########################################################

RECORD_TIMING = False
TIME_START = None
SOLUTION_TIMES = []

def enable_recording():
	global RECORD_TIMING
	RECORD_TIMING = True

def disable_recording():
	global RECORD_TIMING
	RECORD_TIMING = False

def start_recording():
	global TIME_START, SOLUTION_TIMES
	TIME_START = datetime.now()
	SOLUTION_TIMES = []

def add_timing():
	global SOLUTION_TIMES, TIME_START
	if TIME_START is not None:
		SOLUTION_TIMES.append(datetime.now() - TIME_START)

def get_timings():
	global SOLUTION_TIMES
	return SOLUTION_TIMES

VERBOSE = True
def set_verbose(b):
	global VERBOSE
	VERBOSE = b

##########################################################
############# Helpers                     ################
##########################################################

@lru_cache(maxsize=1024)
def get_vars_uo(t: Term):
	"""Recursively get unique and ordered variables"""
	if isinstance(t, Variable):
		return {t}

	l = set()
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l |= get_vars_uo(i)

	return l

def fresh_var(var_count: List[int]) -> Variable:
	"""Given the current variable number count, create
	a fresh variable."""
	name = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	return Variable(name)

# Node in search space
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

	def add_node(self, ruleName: str, data: Set[Equation], var_count: List[int]):
		newNode = MutateNode(data, self.ruleList + [ruleName])
		newNode.var_count = var_count
		if   ruleName == "ID":      self.id = newNode
		elif ruleName == "C":       self.c = newNode
		elif ruleName == "A_RIGHT": self.a1 = newNode
		elif ruleName == "A_LEFT":  self.a2 = newNode
		elif ruleName == "RC":      self.rc = newNode
		elif ruleName == "LC":      self.lc = newNode
		elif ruleName == "MC":      self.mc = newNode
		else:
			raise Exception("Unrecognized Mutate Rule")

		return newNode

	def __str__(self):
		return f"MutateNode(data={self.data})"

def helper_gvs(U: Set[Equation]) -> Set[Variable]:
	"""Retrieves the set of variables from a set of equations"""
	V = set()
	for e in U:
		V = V.union(get_vars_uo(e.left_side))
		V = V.union(get_vars_uo(e.right_side))
	return V

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


##########################################################
############# Mutation Rules              ################
##########################################################

def match_mutation(U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
	for e1, e2 in itertools.product(U, U):
		# Skip if e1 and e2 are the same
		if e1 == e2:
			continue

		# Variables on lhs are the same and right side are FuncTerms
		lhs1 = e1.left_side; rhs1 = e1.right_side
		lhs2 = e2.left_side; rhs2 = e2.right_side
		if isinstance(lhs1, Variable) and lhs1 == lhs2:
			if isinstance(rhs1, FuncTerm) and isinstance(rhs2, FuncTerm):
				return (e1, e2)

	return None

#Mutation Rule ID
def match_mutation_rule1(e: Tuple[Equation, Equation], _) -> Optional[Tuple[Equation, Equation]]:
	return e

def mutation_rule1(U: Set[Equation], es: Tuple[Equation, Equation], _) -> Set[Equation]:
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

	m1 = set()
	m1.add(Equation(y1, z1))
	m1.add(Equation(y2, z2))
	U = U.union(m1)

	return U

#Mutation Rule C
def match_mutation_rule2(e: Tuple[Equation, Equation], _) -> Optional[Tuple[Equation, Equation]]:
	return e

def mutation_rule2(U: Set[Equation], es: Tuple[Equation, Equation], _) -> Set[Equation]:
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

	m1 = set()
	m1.add(Equation(y1, z2))
	m1.add(Equation(y2, z1))
	U = U.union(m1)

	return U

#Mutation Rule A1
def match_mutation_rule3(e: Tuple[Equation, Equation], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
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

	m1 = set()
	m1.add(Equation(y1, f(z1, v1)))
	m1.add(Equation(z2, f(v1, y2)))
	U = U.union(m1)
	# print("--------------After Applying A1-------------------")
	# print(U)
	# print("--------------------------------------------------")

	return U

#Mutation Rule A2
def match_mutation_rule4(e: Tuple[Equation, Equation], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
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

	m1 = set()
	m1.add(Equation(y2, f(v1, z2)))
	m1.add(Equation(z1, f(y1, v1)))
	U = U.union(m1)

	# print("--------------After Applying A2-------------------")
	# print(U)
	# print("--------------------------------------------------")
	return U

#Mutation Rule RC
def match_mutation_rule5(e: Tuple[Equation, Equation], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
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

	m1 = set()
	m1.add(Equation(y1, f(v1, z2)))
	m1.add(Equation(z1, f(v1, y2)))
	U = U.union(m1)

	# print("----------After applying RC--------------")
	# print(U)
	# print("-----------------------------------------")

	return U

#Mutation Rule LC
def match_mutation_rule6(e: Tuple[Equation, Equation], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
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

	m1 = set()
	m1.add(Equation(y2, f(z1, v1)))
	m1.add(Equation(z2, f(y1, v1)))
	U = U.union(m1)

	# print("---------After applying LC---------------")
	# print(U)
	# print("-----------------------------------------")
	return U

#Mutation Rule MC
def match_mutation_rule7(e: Tuple[Equation, Equation], U: Set[Equation]) -> Optional[Tuple[Equation, Equation]]:
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

	m1 = set()
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
	new_equations = set()

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

	if matched_equation is None:
		return equations

	return equations - {matched_equation}

def delete_trivial(equations) -> Set[Equation]:
	new_equations = set()
	for e in equations:
		if e.left_side != e.right_side:
			new_equations.add(e)
	return new_equations

def s_rules(U: Set[Equation], VS1: Set[Variable]):
	"""
	S Rules
	"""
	# print("Before S Rules:", U)
	Utemp = set()
	while Utemp != U:
		Utemp = U
		if occurs_check(U):
			return set()
		U = variable_replacement(U)
		U = eqe(U, VS1)
		U = delete_trivial(U)

		# For slow debugging
		# print(U)
		# import time
		# time.sleep(1)

	# print("After S Rules:", U)
	return U

##########################################################
############# Core Algorithm              ################
##########################################################

mutation_rules = [
	dict(name="ID", match=match_mutation_rule1, apply=mutation_rule1),
	dict(name="C", match=match_mutation_rule2, apply=mutation_rule2),
	dict(name="A_RIGHT", match=match_mutation_rule3, apply=mutation_rule3),
	dict(name="A_LEFT", match=match_mutation_rule4, apply=mutation_rule4),
	dict(name="RC", match=match_mutation_rule5, apply=mutation_rule5),
	dict(name="LC", match=match_mutation_rule6, apply=mutation_rule6),
	dict(name="MC", match=match_mutation_rule7, apply=mutation_rule7)
]

def apply_mutation_rules(
		cn: MutateNode,
		Q: List[MutateNode], Tree: List[List[MutateNode]], level: int):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[Tuple[MutateNode, int]] = []

	dcopy = deepcopy(cn.data)
	mutate_eq = match_mutation(dcopy)

	if mutate_eq is None:
		return

	for mutation in mutation_rules:
		# Call corresponding match rule to see
		# if the rule is applicable
		e = mutation['match'](mutate_eq, cn.data)
		if e is not None:
			# Apply the applicable mutate rule
			dcopy = deepcopy(cn.data)
			var_count = deepcopy(cn.var_count)
			new_eqs = mutation['apply'](dcopy, e, var_count)

			# If not already existent, add to search space
			if not look_for_duplicates(Tree, new_eqs):
				newNode = cn.add_node(mutation['name'], new_eqs, var_count)
				nextBranch.append((newNode, level + 1))

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

def build_tree(root: MutateNode, ES1, num_solutions: int):
	NODE_BOUND = -1
	LEVEL_BOUND = -1

	Sol = list()
	Q = [(root, 0)]
	Tree = defaultdict(list)
	Tree[0] = [root]
	current_level = 0
	nodes_considered = 0

	while 0 < len(Q):
		cn, level = Q.pop(0)
		nodes_considered += 1

		if NODE_BOUND > 0 and nodes_considered > NODE_BOUND:
			print(f"[WARNING] Stopping after considering {NODE_BOUND} nodes")
			return Sol

		if level > current_level:
			# Find non-empty branches
			new_last_branch = []
			for node in Tree[current_level]:
				if len(node.data) > 0:
					new_last_branch.append(node)
			occurs_check_nodes = len(Tree[current_level]) - len(new_last_branch)
			# Prune empty branches
			Tree[current_level] = new_last_branch

			if VERBOSE:
				print("=" * 5)
				print("Layer", current_level)
				print("Occurs check on layer:", occurs_check_nodes)
				print("Remaining nodes on layer:", len(Tree[current_level]))
				print("Current number of solutions:", len(Sol))
				print("Total Nodes Considered:", nodes_considered)
				last_node = Tree[current_level][-1]
				print("Last Node:", last_node.data)
				print("Length of last node:", len(last_node.data))
				print("Rules for last node:", last_node.ruleList)
				print("=" * 5)

			current_level = level

			if LEVEL_BOUND > 0 and current_level > LEVEL_BOUND:
				print(f"[WARNING] Stopping after level {LEVEL_BOUND}")
				return Sol

		#Apply S rules - mutate
		cn.data = s_rules(cn.data, ES1)

		if len(cn.data) > 0:
			if solved_form(cn.data):
				Sol.append(cn.data)
				if RECORD_TIMING:
					add_timing()

				if num_solutions > 0 and len(Sol) >= num_solutions:
					if VERBOSE:
						print("Total Layers Computed:", current_level)
					return Sol

			else:
				apply_mutation_rules(cn, Q, Tree, level)

	if VERBOSE:
		print("Total Layers Computed:", current_level)

	return Sol

def synt_ac_unif2(U: Set[Equation], num_solutions: int = 1):
	"""
	Syntactic AC Algorithm.
	Set num_solutions to -1 for all solutions.
	"""
	if RECORD_TIMING:
		start_recording()

	var_count = [0]
	VS1 = helper_gvs(U)

	# Flatten Terms within Equations
	U, var_count[0] = flat(U, var_count[0])

	# Setup initial search space node
	N1 = MutateNode(U, [])
	N1.var_count = var_count

	# Search for the set of solutions
	res = build_tree(N1, VS1, num_solutions)

	# print("Final set of equations")
	# print(res)

	# Build substitution
	final_sol = set()
	for solve in res:
		delta = SubstituteTerm()
		# Convert equations to a substitution
		for e in solve:
			try:
				delta.add(e.left_side, e.right_side)
			except:
				print("-" * 5)
				for e in solve:
					print(e)
				print("-" * 5)
				raise Exception(
					"[Syntactic AC] Error: Can not add to substitution. " +\
					"Equations are likely not in solved form."
				)
		final_sol.add(delta)

	return final_sol
