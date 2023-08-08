from copy import deepcopy
from typing import List, Set, Optional, Tuple, Dict

import itertools

from symcollab.algebra import (
	get_vars, Equation, Variable, Function,
	FuncTerm, Term, SubstituteTerm, Constant
)

from .common import orient, function_clash, delete_trivial

def decompose(equations: Set[Equation], ac_symbol: Function) -> Set[Equation]:
    """
    Applies decomposition to an equation.
    If it is not possible, it will return None.

    f(s1,...,sn)=f(t1,...,tn) -> s1=t1,...,sn=tn

    Returns None if the rule cannot be matched.
    NOTE: Terms that have the AC symbol at its root
    """
    new_equations: Set[Equation] = set()
    matched_equation: Optional[Equation] = None

    # Find a match for the decomposition rule
    # and create the new equations if found.
    for equation in equations:
        el = equation.left_side
        er = equation.right_side
        if isinstance(el, FuncTerm) and \
           isinstance(er, FuncTerm) and \
			el.function == er.function and \
			el.function.arity > 1 and \
			el.function != ac_symbol:
            matched_equation = equation
            for i in range(el.function.arity):
                new_equations.add(Equation(
                    el.arguments[i],
                    er.arguments[i]
                ))
            break # Only match one equation

    # If the rule isn't matched, return the original input
    if matched_equation is None:
        return equations

    # Remove previous equation and add decomposed ones
    return (equations - {matched_equation}) | new_equations

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

def is_ac_symbol(t: Term, ac_symbol: Function):
	return isinstance(t, FuncTerm) \
		and t.function.arity == 2 \
		and t.function == ac_symbol

#Mutation Rule ID
def mutation_rule1(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
			# print("Matched Equation", e)
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]

	m1 = set()
	# s1 = v1
	m1.add(Equation(s1, var1))
	# s2 = v2
	m1.add(Equation(s2, var2))
	# t1 = v1
	m1.add(Equation(t1, var1))
	# t2 = v2
	m1.add(Equation(t2, var2))

	U = U.union(m1)

	return(U)

#Mutation Rule C
def mutation_rule2(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation : Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the possible mutations
	U = U - {matched_equation}
	#ID
	var1 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = f'v_{var_count[0]}'
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]

	m1 = set()
	# s1 = v1
	m1.add(Equation(s1, var1))
	# s2 = v2
	m1.add(Equation(s2, var2))
	# t1 = v2
	m1.add(Equation(t1, var2))
	# t2 = v1
	m1.add(Equation(t2, var1))

	U = U.union(m1)

	return U

#Mutation Rule A1
def mutation_rule3(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the possible mutations
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]
	f = matched_equation.left_side.function

	m1 =  set()
	# s1 = v1 + v2
	m1.add(Equation(s1, f(var1, var2)))
	# s2 = v3
	m1.add(Equation(s2, var3))
	# t1 = v1
	m1.add(Equation(t1, var1))
	# t2 = v2 + v3
	m1.add(Equation(t2, f(var2, var3)))

	U = U.union(m1)

	return U

#Mutation Rule A2
def mutation_rule4(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the possible mutations
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]
	f = matched_equation.left_side.function


	m1 = set()
	# s1 = v1
	m1.add(Equation(s1, var1))
	# s2 = v2 + v3
	m1.add(Equation(s2, f(var2, var3)))
	# t1 = v1 + v2
	m1.add(Equation(t1, f(var1, var2)))
	# t2 = v3
	m1.add(Equation(t2, var3))

	U = U.union(m1)

	return U

#Mutation Rule RC
def mutation_rule5(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]
	f = matched_equation.left_side.function


	m1 = set()
	# s1 = v1 + v2
	m1.add(Equation(s1, f(var1, var2)))
	# s2 = v3
	m1.add(Equation(s2, var3))
	# t1 = v1 + v3
	m1.add(Equation(t1, f(var1, var3)))
	# t2 = v2
	m1.add(Equation(t2, var2))

	U = U.union(m1)

	return U

#Mutation Rule LC
def mutation_rule6(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]
	f = matched_equation.left_side.function


	m1 = set()
	# s1 = v1
	m1.add(Equation(s1, var1))
	# s2 = v2 + v3
	m1.add(Equation(s2, f(var2, var3)))
	# t1 = v2
	m1.add(Equation(t1, var2))
	# t2 = v1 + v3
	m1.add(Equation(t2, f(var1, var3)))

	U = U.union(m1)

	return U

#Mutation Rule MC
def mutation_rule7(U: Set[Equation], var_count: List[int], ac_symbol: Function) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		if is_ac_symbol(e.left_side, ac_symbol) and is_ac_symbol(e.right_side, ac_symbol):
			matched_equation = e
			break

	if matched_equation is None:
		return U

	#Create the possible mutations
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

	# s1 + s2 = t1 + t2
	s1 = matched_equation.left_side.arguments[0]
	s2 = matched_equation.left_side.arguments[1]
	t1 = matched_equation.right_side.arguments[0]
	t2 = matched_equation.right_side.arguments[1]
	f = matched_equation.left_side.function

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

def variable_replacement(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	# Look for candidate equations to variable replace
	candidate_equation = None
	for e in equations:
		# Conditions
		both_sides_variables = isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable)
		variables_in_P = helper_gvs(equations - {e})
		exists_within_p = e.left_side in variables_in_P and e.right_side in variables_in_P
		not_restricted_l = e.left_side not in restricted_vars
		# NOTE: The only free variables are from the original problem, bound variables are created by mutation

		left_bound_or_right_free = e.left_side not in VS1 or e.right_side in VS1
		condition1 = both_sides_variables and exists_within_p and not_restricted_l and left_bound_or_right_free
		if condition1:
			candidate_equation = e
			delta = SubstituteTerm()
			delta.add(e.left_side, e.right_side)
			break


		left_free_or_right_bound = e.left_side in VS1 or e.right_side not in VS1
		not_restricted_r = e.right_side not in restricted_vars
		condition2 = both_sides_variables and exists_within_p and not_restricted_r and left_free_or_right_bound
		if condition2:
			candidate_equation = e
			delta = SubstituteTerm()
			delta.add(e.right_side, e.left_side)
			break

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
	delta = SubstituteTerm()
	delta.add(candidate_equation.left_side, candidate_equation.right_side)
	substituted_equations = apply_substitution_on_equations(delta, equations - {candidate_equation})
	equations = substituted_equations.union({candidate_equation})

	return equations

def eqe(equations: Set[Equation], VS1: Set[Variable], restricted_vars: Set[Variable]) -> Set[Equation]:
	equation_to_remove: Optional[Equation] = None
	for e in equations:
		# Conditions
		variable_left_side = isinstance(e.left_side, Variable)
		# Bound variables are fresh ones not from the original problem
		left_side_bound = e.left_side not in VS1
		variables_in_right_side = set(get_vars(e.right_side))
		variables_in_P = helper_gvs(equations - {e})
		not_in_SP = e.left_side not in variables_in_right_side.union(variables_in_P)
		not_restricted_l = e.left_side not in restricted_vars

		if variable_left_side and left_side_bound and not_in_SP and not_restricted_l:
			equation_to_remove = e
			break # NOTE: REQUIRED

		variable_right_side = isinstance(e.right_side, Variable)
		right_side_bound = e.right_side not in VS1
		variables_in_left_side = set(get_vars(e.left_side))
		not_in_XP = e.right_side not in variables_in_left_side.union(variables_in_P)
		not_restricted_r = e.right_side not in restricted_vars

		if variable_right_side and right_side_bound and not_in_XP and not_restricted_r:
			equation_to_remove = e
			break # NOTE: REQUIRED

	return (equations - {equation_to_remove})

def prune(equations: Set[Equation], VS1: Set[Variable], ignore_vars: Set[Variable]) -> bool:
	VS2 = helper_gvs(equations)
	VS2 = VS2.difference(VS1)
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in ignore_vars and e.left_side in VS2:
				if not linear(e.right_side):
					return True
	return False

def s_rules_no_mutate(U: Set[Equation], VS1: Set[Variable], ac_symbol):
	"""
	Apply S rules (without mutate) on set of equations with no restrictions
	"""
	U = orient(U)
	U = decompose(U, ac_symbol)
	U = merge(U, set())
	U = variable_replacement(U, VS1, set())
	U = replacement(U, VS1, set())
	U = eqe(U, VS1, set())
	U = delete_trivial(U)

	if occurs_check_full(U):
		return set()

	if function_clash(U):
		return set()

	return U

def s_rules_no_mutate_new_vars(U: set[Equation], VS1: Set[Variable], ac_symbol):
	"""
	Apply S ruless without mutate and including the merge rule
	"""
	U = orient(U)
	U = decompose(U, ac_symbol)
	U = merge(U, set())
	U = variable_replacement(U, VS1, set())
	U = replacement(U, VS1, set())
	U = eqe(U, VS1, set())
	U = delete_trivial(U)

	if occurs_check_full(U):
		return set()

	if function_clash(U):
		return set()

	if prune(U, VS1, set()):
		# print("[Stage 3] Prune rule applied")
		return set()

	return U

def can_apply_mutation_rules(
		cn: MutateNode, var_count: int,
		Tree: List[List[MutateNode]],
		ac_symbol: Function):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	dcopy = deepcopy(cn.data)

	cn.id = MutateNode(mutation_rule1(dcopy, var_count, ac_symbol))
	if not already_explored(cn.id, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count, ac_symbol))
	if not already_explored(cn.c, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count, ac_symbol))
	if not already_explored(cn.a1, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count, ac_symbol))
	if not already_explored(cn.a2, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count, ac_symbol))
	if not already_explored(cn.rc, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count, ac_symbol))
	if not already_explored(cn.lc, Tree):
		return True

	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count, ac_symbol))
	if not already_explored(cn.mc, Tree):
		return True

	return False

def apply_mutation_rules(
		cn: MutateNode, var_count: int,
		Q: List[MutateNode], Tree: List[List[MutateNode]],
		ac_symbol: Function):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[MutateNode] = []
	dcopy = deepcopy(cn.data)

	cn.id = MutateNode(mutation_rule1(dcopy, var_count, ac_symbol))
	if not already_explored(cn.id, Tree):
		nextBranch.append(cn.id)

	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count, ac_symbol))
	if not already_explored(cn.c, Tree):
		nextBranch.append(cn.c)

	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count, ac_symbol))
	if not already_explored(cn.a1, Tree):
		nextBranch.append(cn.a1)

	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count, ac_symbol))
	if not already_explored(cn.a2, Tree):
		nextBranch.append(cn.a2)

	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count, ac_symbol))
	if not already_explored(cn.rc, Tree):
		nextBranch.append(cn.rc)

	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count, ac_symbol))
	if not already_explored(cn.lc, Tree):
		nextBranch.append(cn.lc)

	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count, ac_symbol))
	if not already_explored(cn.mc, Tree):
		nextBranch.append(cn.mc)

	Tree.append(nextBranch)
	Q.extend(nextBranch)

def build_tree(U: Set[Equation], single_sol, ac_symbol: Function):

	MAX_MUTATE_APPLICATION = 100 # Upper bound until algorithm performs better

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
	var_count = [0] # NOTE: Fresh variable global hack

	################### Step 1 #########################
	# Apply rules of S for as long as possible except
	# each distinct occurance of a variable is treated
	# as a distinct variable

	root = MutateNode(distinct_u)
	step_1_solutions: List[Set[Equation]] = []
	Q: List[MutateNode] = [root]
	Tree: List[List[MutateNode]] = [[root]]
	i = 0 # NOTE: DEBUG
	while len(Q) > 0:

		# Depth of search tree corresponds to the number of times
		# the mutation rules are applied
		# NOTE: Currently have an upper bound until algorithm improves
		if len(Tree) > MAX_MUTATE_APPLICATION:
			print("[Stage 1] Warning: Upper bound reached")
			break

		cn = Q.pop(0)

		# Saturate S rules without mutate
		U_temp = set()
		while U_temp != cn.data:
			U_temp = cn.data
			cn.data = s_rules_no_mutate(cn.data, original_variables_distinct, ac_symbol)

		# If we can't apply anymore rules,
		# then append to step 1 solution list
		if not can_apply_mutation_rules(cn, [0], Tree, ac_symbol):
			if len(cn.data) > 0:
				step_1_solutions.append(cn.data)
		else:
			apply_mutation_rules(cn, var_count, Q, Tree, ac_symbol)


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
	for s in step_1_5_solutions:
		Tree = [[MutateNode(s)]]
		Q = [MutateNode(s)]
		while len(Q) > 0:

			# Depth of search tree corresponds to the number of times
			# the mutation rules are applied
			# NOTE: Currently have an upper bound until algorithm improves
			if len(Tree) > MAX_MUTATE_APPLICATION:
				print("[Stage 2] Warning: Upper bound reached")
				break

			cn = Q.pop(0)

			# Saturate S Rules
			U_temp = set()
			while U_temp != cn.data:
				U_temp = cn.data
				cn.data = s_rules_no_mutate_new_vars(cn.data, original_variables, ac_symbol)


			# If we can't apply anymore rules,
			# then append to solution list
			if not can_apply_mutation_rules(cn, [0], Tree, ac_symbol):
				if len(cn.data) > 0:
					Sol.append(cn.data)
					if single_sol:
						return Sol
			else:
				apply_mutation_rules(cn, var_count, Q, Tree, ac_symbol)

	return Sol

def synt_ac_unif(U: Set[Equation], ac_symbol: Function, single_sol: bool = True):
	# This algorithm assumes that the same variable
	# doesn't appear on both sides.
	for equation in U:
		left_side_vars = get_vars(equation.left_side, unique=True)
		right_side_vars = get_vars(equation.right_side, unique=True)
		if len(left_side_vars.intersection(right_side_vars)) > 0:
			raise Exception(
				"[Syntactic AC] This algorithm only works for " +\
				"equations without shared variables on both sides"
			)

	res = build_tree(U, single_sol, ac_symbol)

	final_sol = set()
	for solve in res:
		delta = SubstituteTerm()
		# Convert equations to a substitution
		for e in solve:
			try:
				delta.add(e.left_side, e.right_side)
			except:
				# Print equations for easier debugging
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
