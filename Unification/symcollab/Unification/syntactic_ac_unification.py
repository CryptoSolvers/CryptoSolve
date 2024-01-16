"""
Implementation of
"Syntactic" AC Unification
by Boudet and Contejean 1994
"""
from copy import deepcopy
from collections import defaultdict
from functools import lru_cache
from typing import List, Set, Optional, Dict

import itertools

from symcollab.algebra import (
	Equation, Variable, FuncTerm,
	Term, SubstituteTerm, Constant,
	unravel
)

from .common import orient, occurs_check

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
def is_binary_function(t: Term):
	return isinstance(t, FuncTerm) and t.function.arity == 2

def match_mutation(U: Set[Equation]) -> Optional[Equation]:
	for e in U:
		if is_binary_function(e.left_side) and is_binary_function(e.right_side):
			return e
	return None

#Mutation Rule ID
def mutation_rule1(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]

	m1 = set()
	m1.add(Equation(s1, var1))
	m1.add(Equation(s2, var2))
	m1.add(Equation(t1, var1))
	m1.add(Equation(t2, var2))

	U = U.union(m1)

	return U

#Mutation Rule C
def mutation_rule2(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]

	m1 = set()
	m1.add(Equation(s1, var1))
	m1.add(Equation(s2, var2))
	m1.add(Equation(t1, var2))
	m1.add(Equation(t2, var1))

	U = U.union(m1)

	return U

#Mutation Rule A1
def mutation_rule3(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)
	var3 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	f = e.left_side.function

	m1 =  set()
	m1.add(Equation(s1, f(var1, var2)))
	m1.add(Equation(s2, var3))
	m1.add(Equation(t1, var1))
	m1.add(Equation(t2, f(var2, var3)))

	U = U.union(m1)

	return U

#Mutation Rule A2
def mutation_rule4(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)
	var3 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	f = e.left_side.function


	m1 = set()
	m1.add(Equation(s1, var1))
	m1.add(Equation(s2, f(var2, var3)))
	m1.add(Equation(t1, f(var1, var2)))
	m1.add(Equation(t2, var3))

	U = U.union(m1)

	return U

#Mutation Rule RC
def mutation_rule5(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)
	var3 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	f = e.left_side.function


	m1 = set()
	m1.add(Equation(s1, f(var1, var2)))
	m1.add(Equation(s2, var3))
	m1.add(Equation(t1, f(var1, var3)))
	m1.add(Equation(t2, var2))

	U = U.union(m1)

	return U

#Mutation Rule LC
def mutation_rule6(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the 7 possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)
	var3 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	f = e.left_side.function


	m1 = set()
	m1.add(Equation(s1, var1))
	m1.add(Equation(s2, f(var2, var3)))
	m1.add(Equation(t1, var2))
	m1.add(Equation(t2, f(var1, var3)))

	U = U.union(m1)

	return U

#Mutation Rule MC
def mutation_rule7(U: Set[Equation], e: Equation, var_count: List[int]) -> Set[Equation]:
	assert e in U
	assert isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm)

	#Create the possible mutations
	U = U - {e}

	# Generate fresh variables
	var1 = fresh_var(var_count)
	var2 = fresh_var(var_count)
	var3 = fresh_var(var_count)
	var4 = fresh_var(var_count)

	# s1 + s2 = t1 + t2
	s1 = e.left_side.arguments[0]
	s2 = e.left_side.arguments[1]
	t1 = e.right_side.arguments[0]
	t2 = e.right_side.arguments[1]
	f = e.left_side.function

	m1 = set()
	# s1 = v1 + v2
	m1.add(Equation(s1, f(var1, var2)))
	# s2 = v3 + v4
	m1.add(Equation(s2, f(var3, var4)))
	# t1 = v1 + v3
	m1.add(Equation(t1, f(var1, var3)))
	# t2 = v2 + v4
	m1.add(Equation(t2, f(var2, var4)))

	U = U.union(m1)

	return U

##########################################################
############# S Rules                     ################
##########################################################

def variable_replacement(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	# Look for candidate equations to variable replace
	candidate_equation = None
	for e in equations:
		# Conditions
		variables_in_P = helper_gvs(equations - {e})
		within_p = e.left_side in variables_in_P and e.right_side in variables_in_P

		# Condition 1
		if within_p and e.left_side not in VS1 and e.left_side not in restricted_vars:
			candidate_equation = e
			delta = SubstituteTerm()
			delta.add(e.left_side, e.right_side)
			break

		# Condition 2
		if within_p and e.right_side in VS1 and e.left_side not in restricted_vars:
			candidate_equation = e
			delta = SubstituteTerm()
			delta.add(e.left_side, e.right_side)
			break

	if candidate_equation is None:
		return equations

	# Apply the new substitution to the set of equations
	new_equations = set()

	for equation in equations - {candidate_equation}:
		new_equations.add(Equation(
			unravel(equation.left_side, delta),
			unravel(equation.right_side, delta)
        ))

    # Add the matched equation to the result
	new_equations.add(candidate_equation)

	return equations

def replacement(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	candidate_equation = None
	for e in equations:
		variables_in_P = helper_gvs(equations - {e})
		# x \in V(P)
		left_within_p = e.left_side in variables_in_P
		# x \not\in V(s)
		left_not_within_right = e.left_side not in get_vars_uo(e.right_side)
		# x, s \in V(P)
		within_p = left_within_p and e.right_side in variables_in_P

		# Condition 1
		if left_within_p and not isinstance(e.right_side, Variable) and left_not_within_right and e.left_side not in restricted_vars:
			candidate_equation = e
			break

		# Condition 2
		if isinstance(e.right_side, Variable) and e.left_side != e.right_side and within_p and e.left_side not in restricted_vars:
			candidate_equation = e
			break

	if candidate_equation is None:
		return equations

	# Create and apply substitution
	delta = SubstituteTerm()
	delta.add(candidate_equation.left_side, candidate_equation.right_side)

	new_equations = set()

	for equation in equations - {candidate_equation}:
		new_equations.add(Equation(
			unravel(equation.left_side, delta),
			unravel(equation.right_side, delta)
        ))

    # Add the matched equation to the result
	new_equations.add(candidate_equation)

	return new_equations

def eqe(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	equation_to_remove: Optional[Equation] = None
	for e in equations:
		# Conditions

		# Bound variables are fresh ones not from the original problem
		left_side_bound = isinstance(e.left_side, Variable) and e.left_side not in VS1

		# x \not\in V(s) \cup V(P)
		variables_in_right_side = set(get_vars_uo(e.right_side))
		variables_in_P = helper_gvs(equations - {e})
		not_in_SP = e.left_side not in variables_in_right_side.union(variables_in_P)

		if left_side_bound and not_in_SP and e.left_side not in restricted_vars:
			equation_to_remove = e
			break # NOTE: REQUIRED

	return (equations - {equation_to_remove})

def merge(equations: Set[Equation], restricted_vars: Set[Variable]) -> Set[Equation]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x is a variable and s and t are not variables
	"""
	remove_equation: Optional[Equation] = None
	add_equation: Optional[Equation] = None

	for e1, e2 in itertools.product(equations, equations):
		# Skip if the two equations are the same
		if e1 == e2:
			continue

		# Conditions for merge
		matching_left_variable = e1.left_side == e2.left_side and isinstance(e1.left_side, Variable)
		right_side_not_variable = not isinstance(e1.right_side, Variable) and not isinstance(e2.right_side, Variable)
		not_restricted = e1.left_side not in restricted_vars

		if matching_left_variable and right_side_not_variable and not_restricted:
			remove_equation = e2
			add_equation = Equation(
				e1.right_side,
				e2.right_side
			)
			break

	# No relevant equation pair found
	if remove_equation is None or add_equation is None:
		return equations

	return (equations - {remove_equation}).union({add_equation})

def prune(equations: Set[Equation], VS1: Set[Variable], ignore_vars: Set[Variable]) -> bool:
	VS2 = helper_gvs(equations)
	VS2 = VS2.difference(VS1)
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in ignore_vars and e.left_side in VS2:
				if not linear(e.right_side):
					return True
	return False

#helper function to check for linear term
def linear(t: Term) -> bool:
	V = get_vars_uo(t)
	# False if there are duplicate variables within a term
	return len(V) == len(set(V))

def s_rules_no_mutate(U: Set[Equation], VS1: Set[Variable]):
	"""
	Apply S rules on set of equations with no restrictions
	"""
	Utemp = set()
	while Utemp != U:
		Utemp = U
		if occurs_check(U):
			return set()
		U = orient(U)
		U = merge(U, set())
		U = variable_replacement(U, VS1, set())
		U = replacement(U, VS1, set())
		U = eqe(U, VS1, set())

	return U

def s_rules_no_mutate_og_vars(U: set[Equation], VS1: Set[Variable]):
	"""
	Apply S rules only on the variables from the original equations
	"""
	new_V = helper_gvs(U) - VS1

	Utemp = set()
	while Utemp != U:
		Utemp = U
		if occurs_check(U):
			return set()
		if prune(U, VS1, VS1):
			# print("[Stage 2] Prune rule applied")
			return set()
		U = orient(U)
		U = merge(U, new_V)
		U = variable_replacement(U, VS1, new_V)
		U = replacement(U, VS1, new_V)
		U = eqe(U, VS1, new_V)

	return U

def s_rules_no_mutate_new_vars(U: set[Equation], VS1: Set[Variable]):
	"""
	Apply S rules only on variables not from the original equations
	"""
	nVST = helper_gvs(U) - VS1
	Utemp = set()
	while Utemp != U:
		Utemp = U
		if occurs_check(U):
			return set()
		if prune(U, VS1, nVST):
			# print("[Stage 3] Prune rule applied")
			return set()
		U = orient(U)
		U = merge(U, nVST)
		U = variable_replacement(U, VS1, nVST)
		U = replacement(U, VS1, nVST)
		U = eqe(U, VS1, nVST)

	return U

##########################################################
############# Core Algorithm              ################
##########################################################

mutation_rules = [
	dict(name="ID",      apply=mutation_rule1),
	dict(name="C",       apply=mutation_rule2),
	dict(name="A_RIGHT", apply=mutation_rule3),
	dict(name="A_LEFT",  apply=mutation_rule4),
	dict(name="RC",      apply=mutation_rule5),
	dict(name="LC",      apply=mutation_rule6),
	dict(name="MC",      apply=mutation_rule7)
]

def apply_mutation_rules(
		cn: MutateNode,
		Q: List[MutateNode], Tree: List[List[MutateNode]], level: int):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[MutateNode] = []

	dcopy = deepcopy(cn.data)
	mutate_eq = match_mutation(dcopy)

	if mutate_eq is None:
		return

	for mutation in mutation_rules:
		dcopy = deepcopy(cn.data)
		var_count = deepcopy(cn.var_count)
		new_eqs = mutation['apply'](dcopy, mutate_eq, var_count)
		if not look_for_duplicates(Tree, new_eqs):
			newNode = cn.add_node(mutation['name'], new_eqs, var_count)
			nextBranch.append((newNode, level + 1))

	Tree[level + 1].extend(c for c, _ in nextBranch)
	Q.extend(nextBranch)
	return len(nextBranch) > 0

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

def build_tree(U: Set[Equation], num_solutions: int):

	NODE_BOUND = 500
	LEVEL_BOUND = 20

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

	# NOTE: DEBUG
	# print("Distinct Check")
	# for eq in distinct_u:
	# 	print(eq)
	# print("")

	################### Step 1 #########################
	# Apply rules of S for as long as possible except
	# each distinct occurance of a variable is treated
	# as a distinct variable

	root = MutateNode(distinct_u, [])
	root.var_count = [0]
	step_1_solutions: List[Set[Equation]] = []
	Q = [(root, 0)]
	Tree = defaultdict(list)
	Tree[0] = [root]
	max_var_count = 0
	nodes_considered = 0
	current_level = 0
	while len(Q) > 0:
		cn, level = Q.pop(0)
		nodes_considered += 1

		if NODE_BOUND > 0 and nodes_considered > NODE_BOUND:
			print("[WARNING] Stopping after considering {nodes_considered} nodes at stage 1.")
			break

		if level > current_level:
			# Find non-empty branches
			new_last_branch = []
			for node in Tree[current_level]:
				if len(node.data) > 0:
					new_last_branch.append(node)
			# occurs_check_nodes = len(Tree[current_level]) - len(new_last_branch)
			# Prune empty branches
			Tree[current_level] = new_last_branch

			current_level = level
			if LEVEL_BOUND > 0 and current_level > LEVEL_BOUND:
				print(f"[WARNING] Stopping after level {LEVEL_BOUND} at stage 1.")
				return Sol

		# Saturate S rules without mutate
		cn.data = s_rules_no_mutate(cn.data, original_variables_distinct)

		# If we can't apply anymore rules,
		# then append to step 1 solution list
		if not apply_mutation_rules(cn, Q, Tree, level):
			if len(cn.data) > 0:
				step_1_solutions.append(cn.data)
				max_var_count = max(max_var_count, cn.var_count[0])

	# print("---- Step 1 solutions --------")
	# for eq in step_1_solutions:
	# 	print(eq)

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

	# print("------- Step 1.5 solutions ---------")
	# for eq in step_1_5_solutions:
	# 	print(eq)

	################### Step 2, 3 ###################
	# Apply S rules only on the variables
	# from the original problem
	step_2_solutions: List[Set[Equation]] = []
	print("# Equations after Stage 1 = ", len(step_1_5_solutions))
	for s in step_1_5_solutions:
		root = MutateNode(s, [])
		root.var_count = [max_var_count]
		Tree = defaultdict(list)
		Tree[0] = [root]
		Q = [(root, 0)]
		nodes_considered = 0
		current_level = 0
		while len(Q) > 0:
			cn, level = Q.pop(0)
			nodes_considered += 1

			if NODE_BOUND > 0 and nodes_considered > NODE_BOUND:
				print(f"[WARNING] Stopping after considering {NODE_BOUND} nodes at stage 2")
				break

			if level > current_level:
				# Find non-empty branches
				new_last_branch = []
				for node in Tree[current_level]:
					if len(node.data) > 0:
						new_last_branch.append(node)
				# occurs_check_nodes = len(Tree[current_level]) - len(new_last_branch)
				# Prune empty branches
				Tree[current_level] = new_last_branch

				current_level = level

				if LEVEL_BOUND > 0 and current_level > LEVEL_BOUND:
					print(f"[WARNING] Stopping after level {LEVEL_BOUND} at stage 2")
					break

			# Saturate S Rules
			cn.data = s_rules_no_mutate_og_vars(cn.data, original_variables)

			# If we can't apply anymore rules,
			# then append to step 2 solution list
			if not apply_mutation_rules(cn, Q, Tree, level):
				if len(cn.data) > 0:
					step_2_solutions.append(cn.data)
					max_var_count = max(max_var_count, cn.var_count[0])

	# ################### Step 3, 4 ###################
	Sol: List[Set[Equation]] = []
	print("# Equations after Stage 2 =", len(step_2_solutions))
	for s in step_2_solutions:
		root = MutateNode(s, [])
		root.var_count = [max_var_count]
		Tree = defaultdict(list)
		Tree[0] = [root]
		Q = [(root, 0)]
		nodes_considered = 0
		current_level = 0
		while len(Q) > 0:
			cn, level = Q.pop(0)
			nodes_considered += 1

			if NODE_BOUND > 0 and nodes_considered > NODE_BOUND:
				print(f"[WARNING] Stopping after considering {NODE_BOUND} nodes at stage 3")
				break

			if level > current_level:
				# Find non-empty branches
				new_last_branch = []
				for node in Tree[current_level]:
					if len(node.data) > 0:
						new_last_branch.append(node)
				# occurs_check_nodes = len(Tree[current_level]) - len(new_last_branch)
				# Prune empty branches
				Tree[current_level] = new_last_branch
				current_level = level
				if LEVEL_BOUND > 0 and current_level > LEVEL_BOUND:
					print(f"[WARNING] Stopping after level {LEVEL_BOUND} at stage 3")
					break

			# Saturate S Rules
			cn.data = s_rules_no_mutate_new_vars(cn.data, original_variables)

			# If we can't apply anymore rules,
			# then append to solution list
			if not apply_mutation_rules(cn, Q, Tree, level):
				if len(cn.data) > 0:
					if solved_form(cn.data):
						Sol.append(cn.data)
						if num_solutions > 0 and len(Sol) >= num_solutions:
							return Sol

	return Sol

def synt_ac_unif(U: Set[Equation], num_solutions: int = 1):

	# This algorithm assumes that the same variable
	# doesn't appear on both sides.
	for equation in U:
		left_side_vars = get_vars_uo(equation.left_side)
		right_side_vars = get_vars_uo(equation.right_side)
		if len(left_side_vars.intersection(right_side_vars)) > 0:
			raise Exception(
				"[Syntactic AC] This algorithm only works for " +\
				"equations without shared variables on both sides"
			)


	res = build_tree(U, num_solutions)

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
