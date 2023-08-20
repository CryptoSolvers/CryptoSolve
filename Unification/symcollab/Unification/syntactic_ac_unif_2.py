from copy import deepcopy
from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, depth, get_vars_or_constants,
	SubstituteTerm
)
from symcollab.Unification.common import (
    delete_trivial, occurs_check, function_clash
)
from symcollab.Unification.unif import unif as syntactic_unification
from symcollab.Unification.flat import flat
from symcollab.Unification.registry import Unification_Algorithms
from typing import Set


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
			if (Equation(e1.right_side, e2.right_side) not in add_equations) and (Equation(e2.right_side, e1.right_side) not in add_equations):
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



def s_rules(U: Set[Equation], VS1: Set[Variable]):
	"""
	S Rules
	"""
	print("in S rules\n")
	print(U)
	U = orient(U)
	Utemp = set()
	V = helper_gvs(U)
	while (Utemp != U):
		Utemp = U
		U = variable_replacement(U, VS1, set())
		print("U after var replace of s_ rules")
		print(U)
		U = merge(U, set())
		print("U after merge replace of s_ rules")
		print(U)
		#U = replacement(U, VS1, set())
		#print("U after replace of s_ rules")
		#print(U)
		U = orient(U)
		print("U after orient of s_ rules")
		print(U)
		if solved_form(U, V, set()):
			print("U is in solved form in S rules, returning\n")
			return U
		U = eqe(U, VS1, set())
		print("U after eqe of s_ rules")
		print(U)
		# Fail early case, not needed
		# for completeness
		if occurs_check_full(U):
			print("Found an occurs check in S rules")
			return set()

	print("U before return of s_ rules")
	print(U)
	return U




def build_tree(root: MutateNode, var_count, VS1, single_sol):

	# NOTE: I like to imagine that there are sets of equations within
	# EQS and EQS2 that are equivalent modulo renaming.
	# It would greatly reduce the search tree if we can identify and remove those

	print("In build Tree\n")
	Sol = list()
	Q = list()
	Q.append(root)
	while Q != list() and len(Q) <= 100:
		cn = Q.pop(0)
		#Apply S rules - mutate
		Max = 50
		count =0
		Utemp = list()
		cn.data = s_rules(cn.data, VS1)
		if cn.data != list():
			solved = True
			if not solved_form(cn.data, VS1, set()):
				solved = False
			if solved != True:
				dcopy = list()
				dcopy = deepcopy(cn.data) 
				cn.id = MutateNode(mutation_rule1(dcopy, var_count))
				Q.append(cn.id)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.c = MutateNode(mutation_rule2(dcopy, var_count))
				Q.append(cn.c)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
				Q.append(cn.a1)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
				Q.append(cn.a2)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
				Q.append(cn.rc)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
				Q.append(cn.lc)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
				Q.append(cn.mc)
			else:
				print("Solved True")
				return(cn.data)
				Sol.append(cn.data)

	return Sol

def synt_ac_unif2(U: Set[Equation], single_sol: bool = True):
	var_count = [0] 
	#flatten equations:
	U, var_count[0] = flat(U, 0)
	print(U)
	VS1 = helper_gvs(U)
	N1 = MutateNode(U)
	res = build_tree(N1, var_count, VS1, single_sol)
	print("Final set of equations")
	print(res)
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
