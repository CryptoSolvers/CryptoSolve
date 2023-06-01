from copy import deepcopy
from typing import List, Set, Optional, Tuple

import itertools

from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, SubstituteTerm
)

from .common import orient


def occurs_check_variable(equations: Set[Equation], v: Variable) -> bool:
	Q: List[Tuple[Set[Equation], List[Term]]] = []

	for equation in equations:
		# Ignore trivial equalities
		if equation.left_side == equation.right_side:
			continue

		if equation.left_side == v:
			Q.append((
				equations - {equation},
				[equation.right_side]
			))
		elif equation.right_side == v:
			Q.append((
				equations - {equation},
				[equation.left_side]
			))


	while len(Q) > 0:
		c_equations, c_path = Q.pop(0)

		last_term = c_path[-1]
		last_term_vars = get_vars(last_term)

		if v in last_term_vars:
			return True
		
		for lv in last_term_vars:
			for ce in c_equations:
				# Ignore trivial equalities
				if ce.left_side == ce.right_side:
					continue

				if ce.left_side == lv:
					Q.append((c_equations - {ce}, c_path + [ce.right_side]))
				elif ce.right_side == lv:
					Q.append((c_equations - {ce}, c_path + [ce.left_side]))

	return False

def occurs_check_full(equations: Set[Equation]) -> bool:
	# Find all x = ... or ... = x
	variables_to_check: Set[Variable] = set()
	for equation in equations:
		if isinstance(equation.left_side, Variable):
			variables_to_check.add(equation.left_side)
		elif isinstance(equation.right_side, Variable):
			variables_to_check.add(equation.right_side)

	# Look for cycles for each variable
	return any((
		occurs_check_variable(equations, v) for v in variables_to_check
	))

def apply_substitution_on_equations(delta: SubstituteTerm, U: Set[Equation]) -> Set[Equation]:
	U_temp = set()
	# Keep applying substition until it can't be	
	# applied anymore
	while U_temp != U:
		U_temp = U
		add_equations = set()
		remove_equations = set()
		for e in U:
			remove_equations.add(e)
			add_equations.add(Equation(
				e.left_side * delta,
				e.right_side * delta
			))
		U = (U - remove_equations).union(add_equations)

	return U
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
	def __str__(self):
		return f"MutateNode(data={self.data})"

def already_explored(m: MutateNode, Tree: List[List[MutateNode]]) -> bool:
	# TODO: Check for equilvalence modulo renaming
	for branch in Tree:
		for q in branch:
			if m.data == q.data:
				return True
	return False

#helper function for solved forms
def solved_form(U: Set[Equation], allowed_vars: Set[Variable], ignore_vars: Set[Variable]) -> bool:
	V: List[Variable] = []
	# Make sure every equation starts with a variable
	# on the left side.
	for e in U:
		if not isinstance(e.left_side, Variable):
			return False
		if e.left_side not in allowed_vars:
			return False
		if e.left_side not in ignore_vars:
			V.append(e.left_side)
	
	# Check for duplicate assignments
	if len(V) != len(set(V)):
		return False

	if occurs_check_full(U):
		return False

	return True

#helper function to check for linear term
def linear(t: Term) -> bool:
	V = get_vars(t)
	# False if there are duplicate variables within a term
	return len(V) == len(set(V))

# Helper function to retrieve a set of variables from a set of equations
def helper_gvs(U: Set[Equation]) -> Set[Variable]:
	V = set()
	for e in U:
		V = V.union(get_vars(e.left_side))
		V = V.union(get_vars(e.right_side))
	return(V)


#Rules

#Mutation Rule ID
def mutation_rule1(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] += 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] += 1
	var2 = Variable(var2)

	m1 = set()
	m1.add(Equation(matched_equation.left_side.arguments[0], var1))
	m1.add(Equation(matched_equation.right_side.arguments[0], var1))
	m1.add(Equation(matched_equation.left_side.arguments[1], var2))
	m1.add(Equation(matched_equation.right_side.arguments[1], var2))
	U = U.union(m1)

	return(U)

#Mutation Rule C
def mutation_rule2(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation : Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	m1 = set()
	m1.add(Equation(matched_equation.left_side.arguments[0], var1))
	m1.add(Equation(matched_equation.right_side.arguments[0], var2))
	m1.add(Equation(matched_equation.left_side.arguments[1], var2))
	m1.add(Equation(matched_equation.right_side.arguments[1], var1))
	U = U.union(m1)

	return U

#Mutation Rule A1
def mutation_rule3(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	m1 =  set()
	t1 = FuncTerm(matched_equation.right_side.function, [var1, var2])
	t2 = FuncTerm(matched_equation.right_side.function, [var2, var3])
	m1.add(Equation(matched_equation.left_side.arguments[0], t1))
	m1.add(Equation(matched_equation.left_side.arguments[1], var3))
	m1.add(Equation(matched_equation.right_side.arguments[0], var1))
	m1.add(Equation(matched_equation.right_side.arguments[1], t2))
	U = U.union(m1)

	return U

#Mutation Rule A2
def mutation_rule4(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	m1 = set()
	t1 = FuncTerm(matched_equation.right_side.function, [var1, var2])
	t2 = FuncTerm(matched_equation.right_side.function, [var2, var3])
	m1.add(Equation(matched_equation.left_side.arguments[0], var1))
	m1.add(Equation(matched_equation.left_side.arguments[1], t2))
	m1.add(Equation(matched_equation.right_side.arguments[0], t1))
	m1.add(Equation(matched_equation.right_side.arguments[1], var3))
	U = U.union(m1)

	return U

#Mutation Rule RC
def mutation_rule5(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	m1 = set()
	t1 = FuncTerm(matched_equation.right_side.function, [var1, var2])
	t2 = FuncTerm(matched_equation.right_side.function, [var1, var3])
	m1.add(Equation(matched_equation.left_side.arguments[0], t1))
	m1.add(Equation(matched_equation.left_side.arguments[1], var3))
	m1.add(Equation(matched_equation.right_side.arguments[0], t2))
	m1.add(Equation(matched_equation.right_side.arguments[1], var2))
	U = U.union(m1)

	return U

#Mutation Rule LC
def mutation_rule6(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U


	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	m1 = set()
	t1 = FuncTerm(matched_equation.right_side.function, [var2, var3])
	t2 = FuncTerm(matched_equation.right_side.function, [var1, var3])
	m1.add(Equation(matched_equation.left_side.arguments[0], var1))
	m1.add(Equation(matched_equation.left_side.arguments[1], t1))
	m1.add(Equation(matched_equation.right_side.arguments[0], var2))
	m1.add(Equation(matched_equation.right_side.arguments[1], t2))
	U = U.union(m1)

	return U

#Mutation Rule MC
def mutation_rule7(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	var4 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var4 = Variable(var4)

	m1 = set()
	t1 = FuncTerm(matched_equation.right_side.function, [var1, var2])
	t2 = FuncTerm(matched_equation.right_side.function, [var3, var4])
	t3 = FuncTerm(matched_equation.right_side.function, [var1, var3])
	t4 = FuncTerm(matched_equation.right_side.function, [var2, var4])
	m1.add(Equation(matched_equation.left_side.arguments[0], t1))
	m1.add(Equation(matched_equation.left_side.arguments[1], t2))
	m1.add(Equation(matched_equation.right_side.arguments[0], t3))
	m1.add(Equation(matched_equation.right_side.arguments[1], t4))
	U = U.union(m1)

	return U


##########################################################
############# S Rules                     ################
##########################################################

def merge(equations: Set[Equation], restricted_vars: Set[Variable]) -> Set[Equation]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x is a variable and s and t are not variables
	"""
	remove_equations = set()
	add_equations = set()
	for e1, e2 in itertools.product(equations, equations):
		# Skip if the two equations are the same
		if e1 == e2:
			continue

		# Conditions for merge
		matching_left_variable = e1.left_side == e2.left_side and isinstance(e1.left_side, Variable)
		right_side_not_variable = not isinstance(e1.right_side, Variable) and not isinstance(e2.right_side, Variable)
		not_restricted = e1.left_side not in restricted_vars

		if matching_left_variable and right_side_not_variable and not_restricted:
			remove_equations.add(e2)
			add_equations.add(Equation(
				e1.right_side,
				e2.right_side
			))

	return (equations - remove_equations).union(add_equations)

def create_substitution_from_equations(equations: Set[Equation], VS1: Set[Variable]) -> SubstituteTerm:
	delta = SubstituteTerm()
	for e in equations:
		if not isinstance(e.left_side, Variable):
			raise Exception("create_substitution_from_equations require var-left equations")
		delta.add(e.left_side, e.right_side)
	return delta

def variable_replacement(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	# Look for candidate equations to variable replace
	candidate_equation = None
	for e in equations:
		# Conditions
		both_sides_variables = isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable)
		variables_in_P = helper_gvs(equations - {e})
		exists_within_p = e.left_side in variables_in_P and e.right_side in variables_in_P
		# NOTE: The only free variables are from the original problem, bound variables are created by mutation
		not_restricted = e.left_side not in restricted_vars and e.right_side not in restricted_vars
		
		left_bound_or_right_free = e.left_side not in VS1 or e.right_side in VS1
		condition1 = both_sides_variables and exists_within_p and not_restricted and left_bound_or_right_free
		if condition1:
			candidate_equation = e
			delta = SubstituteTerm()
			delta.add(e.left_side, e.right_side)
			break


		# NOTE: This does not work for some reason
		# left_free_or_right_bound = e.left_side in VS1 or e.right_side not in VS1
		# condition2 = both_sides_variables and exists_within_p and not_restricted and left_free_or_right_bound
		# if condition2:
		# 	candidate_equation = e
		# 	delta = SubstituteTerm()
		# 	delta.add(e.right_side, e.left_side)
		# 	break

	if candidate_equation is None:
		return equations

	# Create and apply substitution
	# NOTE: Can have cycles in substitutions one call to the method will only perform this rule once
	substituted_equations = apply_substitution_on_equations(delta, equations - {candidate_equation})
	equations = substituted_equations.union({candidate_equation})
	
	return equations

def replacement(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	candidate_equation = None
	for e in equations:
		# Conditions for Option 1
		variable_left_side = isinstance(e.left_side, Variable)
		variables_in_P = helper_gvs(equations - {e})
		left_side_within_P = e.left_side in variables_in_P
		nonvariable_right_side = not isinstance(e.right_side, Variable)
		left_not_within_right = e.left_side not in get_vars(e.right_side)
		not_restricted1 = e.left_side not in restricted_vars
		condition1 = variable_left_side and left_side_within_P and nonvariable_right_side and left_not_within_right and not_restricted1

		# Conditions for Option 2
		variable_right_side = isinstance(e.right_side, Variable)
		not_equiv = e.left_side != e.right_side
		right_side_within_P = e.right_side in variables_in_P
		not_restricted2 = e.left_side not in restricted_vars and e.right_side not in restricted_vars
		condition2 = variable_right_side and not_equiv and variable_left_side and left_side_within_P and right_side_within_P and not_restricted2

		if condition1 or condition2:
			candidate_equation = e
			break

	if candidate_equation is None:
		return equations

	# Create and apply substitution
	# NOTE: Can have cycles in substitutions one call to the method will only perform this rule once
	delta = create_substitution_from_equations({candidate_equation}, VS1)
	substituted_equations = apply_substitution_on_equations(delta, equations - {candidate_equation})
	equations = substituted_equations.union({candidate_equation})
	
	return equations

def eqe(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	equations_to_remove = set()
	for e in equations:
		# Conditions
		variable_left_side = isinstance(e.left_side, Variable)
		# Bound variables are fresh ones not from the original problem
		left_side_bound = e.left_side not in VS1
		variables_in_right_side = set(get_vars(e.right_side))
		variables_in_P = helper_gvs(equations - {e})
		not_in_SP = e.left_side not in variables_in_right_side.union(variables_in_P)
		not_restricted = e.left_side not in restricted_vars

		if variable_left_side and left_side_bound and not_in_SP and not_restricted:
			equations_to_remove.add(e)

	return (equations - equations_to_remove)

def prune(equations: Set[Equation], VS1: Set[Variable], ignore_vars: Set[Variable]) -> bool:
	VS2 = helper_gvs(equations)
	VS2 = VS2.difference(VS1)
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in ignore_vars and e.left_side in VS2:
				if not linear(e.right_side):
					return True
	return False


def stage1(U: Set[Equation], VS1: Set[Variable]):
	"""
	Corresponds to step 1 of syntactic AC
	where we saturate the set of equations
	with the s rules without the mutation rule.

	Step 1 treats variables as distinct meaning
	that it only looks at the newly introduced
	fresh variables. 
	"""
	U = orient(U)

	Utemp = set()
	V = helper_gvs(U)
	while (Utemp != U):
		Utemp = U
		U = variable_replacement(U, VS1, VS1)
		if solved_form(U, V, VS1):
			return U

		U = merge(U, VS1)

		U = replacement(U, VS1, VS1)
		U = orient(U)
		if solved_form(U, V, VS1):
			return U

		U = eqe(U, VS1, VS1)
		
		# Fail early case, not needed
		# for completeness
		if occurs_check_full(U):
			return set()
	
	# Can't apply anymore rules,
	# return current set of equations
	return U



def stage2(U: Set[Equation], VS1: Set[Equation]):
	"""
	Steps 2 and 3 in the Syntactic AC Paper

	Keep trying to perform variable replacement
	until it cannot be applied and then perform
	one merge.
	"""
	U = orient(U)
	# NOTE: This saturation step is necessary
	# in order to pass our second test case
	U_temp = set()
	while U_temp != U:
		U_temp = U
		U = variable_replacement(U, VS1, set())


	# NOTE: Can only merge on variables of V(s) and V(t) from the original problem
	# s =? t so that means we cannot merge on the other variables in our set of equations
	merge_restricted_vars = helper_gvs(U) - VS1
	U = merge(U, merge_restricted_vars)

	if occurs_check_full(U):
		return set()
	
	# NOTE: No mention of EQE in stage 2
	U = eqe(U, VS1, set())

	if prune(U, VS1, VS1):
		# print("[Stage 2] Prune rule applied")
		return set()

	return U



def stage3(U: Set[Equation], VS1: Set[Equation]):
	"""
	Steps 3 and 4 in the Syntactic AC Paper
	"""
	U = orient(U)
	U = replacement(U, VS1, set())
	U = orient(U)

	# U_temp = set()
	# while U_temp != U:
		# U_temp = U
		# U = merge(U, VS1)

	U = merge(U, VS1)

	# NOTE: No mention of EQE in stage 3 but without it
	# we cannot reached solved form as there are useless variables
	U = eqe(U, VS1, set())

	if occurs_check_full(U):
		return set()

	# U = prune(U, VS1, set())
	# Prune rule
	if prune(U, VS1, set()):
		# print("[Stage 3] Prune rule applied")
		return set()

	return U


def apply_mutation_rules(
		cn: MutateNode, var_count: int,
		Q: List[MutateNode], Tree: List[List[MutateNode]]):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[MutateNode] = []
	dcopy = deepcopy(cn.data)

	cn.id = MutateNode(mutation_rule1(dcopy, var_count))
	if not already_explored(cn.id, Tree):
		nextBranch.append(cn.id)

	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count))
	if not already_explored(cn.c, Tree):
		nextBranch.append(cn.c)

	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
	if not already_explored(cn.a1, Tree):
		nextBranch.append(cn.a1)

	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
	if not already_explored(cn.a2, Tree):
		nextBranch.append(cn.a2)

	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
	if not already_explored(cn.rc, Tree):
		Q.append(cn.rc)
		nextBranch.append(cn.rc)

	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
	if not already_explored(cn.lc, Tree):
		nextBranch.append(cn.lc)

	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
	if not already_explored(cn.mc, Tree):
		nextBranch.append(cn.mc)
	
	Tree.append(nextBranch)
	Q.extend(nextBranch)


def build_tree(root: MutateNode, var_count, VS1, single_sol):

	# NOTE: I like to imagine that there are sets of equations within
	# EQS and EQS2 that are equivalent modulo renaming.
	# It would greatly reduce the search tree if we can identify and remove those

	EQS: List[Equation] = []
	Sol: List[Equation] = []
	Q: List[MutateNode] = [root]
	Tree: List[List[MutateNode]] = [[root]]
	################### Step 1 #########################
	# NOTE: I think we're somehow misinterpreting distinct variables
	# here. I think we're supposed to somehow treat duplicated
	# variables in the original problem as distinct but I'm not sure
	# how that works.
	while 0 < len(Q):
		cn = Q.pop(0)
		# Saturate first with S rules without mutate
		cn.data = stage1(cn.data, VS1)

		V = helper_gvs(cn.data)
		quasi_solved_form = solved_form(cn.data, V, VS1)
		
		if quasi_solved_form:
			EQS.append(cn.data)
		else:
			apply_mutation_rules(cn, var_count, Q, Tree)


	################### Step 2, 3 ###################
	EQS2 = []
	print("# Equations after Stage 1 = ", len(EQS))
	for s in EQS:
		Tree = [[MutateNode(s)]]
		Q = [MutateNode(s)]
		while 0 < len(Q):
			
			# Depth of search tree corresponds to the number of times
			# the mutation rules are applied
			# NOTE: Currently have an upper bound until algorithm improves
			if len(Tree) > 10:
				break

			# print("Len(Q) =", len(Q))
			cn = Q.pop(0)
			
			# Algorithm description says to first apply as
			# many variable replacements as possible.
			# Then merge, then solve the resulting merged
			# equation.

			# I interpret solve as apply mutation rules

			# This means we should only apply one merge,
			# and then immediately apply the mutation rules
			U_temp = set()
			while U_temp != cn.data:
				U_temp = cn.data
				cn.data = stage2(cn.data, VS1)
			if len(cn.data) > 0:
				V = helper_gvs(cn.data)
				quasi_solved_form = solved_form(cn.data, V, VS1)
				if quasi_solved_form:
					EQS2.append(cn.data)
				else:
					apply_mutation_rules(cn, var_count, Q, Tree)
	
	################### Step 3, 4 ###################
	print("# Equations after Stage 2 =", len(EQS2))
	for s in EQS2:
		Tree = [[MutateNode(s)]]
		Q = [MutateNode(s)]
		while 0 < len(Q):

			# Depth of search tree corresponds to the number of times
			# the mutation rules are applied
			# NOTE: Currently have an upper bound until algorithm improves
			if len(Tree) > 10:
				break

			cn = Q.pop(0)

			U_temp = set()
			while U_temp != cn.data:
				U_temp = cn.data
				cn.data = stage3(cn.data, VS1)
				if solved_form(cn.data, VS1, set()):
					break
			if len(cn.data) > 0:
				V = helper_gvs(cn.data)
				if solved_form(cn.data, VS1, set()):
					Sol.append(cn.data)
					if single_sol:
						return Sol
				else:
					apply_mutation_rules(cn, var_count, Q, Tree)

	return Sol

def synt_ac_unif(U: Set[Equation], single_sol: bool = True):
	var_count = [0] # Seems to be a global variable hack
	#get the intial set of vars
	VS1 = helper_gvs(U)
	N1 = MutateNode(U)
	res = build_tree(N1, var_count, VS1, single_sol)

	final_sol = set()
	for solve in res:
		delta = SubstituteTerm()
		# Convert equations to a substitution
		for e in solve:
			try:
				delta.add(e.left_side, e.right_side)
			except:
				print("error adding substitution")
		final_sol.add(delta)

	return(final_sol)
