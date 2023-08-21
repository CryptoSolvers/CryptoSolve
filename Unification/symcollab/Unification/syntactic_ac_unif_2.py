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
	for branch_num in Tree:
		for q in Tree[branch_num]:
			if m.data == q.data:
				return True
	return False


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

	print("Applied ID")

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

	print("Applied C")

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
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(lhs, FuncTerm) and isinstance(rhs, FuncTerm):
			bad_condition1 = lhs.arguments[0] == rhs.arguments[1] and \
				lhs.arguments[1] == rhs.arguments[0]
			if not bad_condition1:
				matched_equation = e
				break

	if matched_equation is None:
		return U

	print("+++++++++Applying A1++++++++++++++++")
	print(matched_equation)
	print(U)
	print("++++++++++++++++++++++++++++++++++++")

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
	print("--------------After Applying A1-------------------")
	print(U)
	print("--------------------------------------------------")

	return U

#Mutation Rule A2
def mutation_rule4(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			bad_condition1 = lhs.arguments[0] == rhs.arguments[1] and \
				lhs.arguments[1] == rhs.arguments[0]
			if not bad_condition1:
				matched_equation = e
				break

	if matched_equation is None:
		return U

	print("+++++++++Applying A2++++++++++++++++")
	print(matched_equation)
	print(U)
	print("++++++++++++++++++++++++++++++++++++")


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

	print("--------------After Applying A2-------------------")
	print(U)
	print("--------------------------------------------------")
	return U

#Mutation Rule RC
def mutation_rule5(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	matched_equation: Optional[Equation] = None
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			bad_condition = lhs.arguments[0] == rhs.arguments[0]
			if not bad_condition:
				matched_equation = e
				break

	if matched_equation is None:
		return U

	print("++++++++++++Applying RC++++++++++")
	print(matched_equation)
	print(U)
	print("+++++++++++++++++++++++++++++++++")

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

	print("----------After applying RC--------------")
	print(U)
	print("-----------------------------------------")
	
	return U

#Mutation Rule LC
def mutation_rule6(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	print("=============In LC============")
	print(U)
	print("==============================")
	matched_equation: Optional[Equation] = None
	for e in U:
		lhs = e.left_side
		rhs = e.right_side
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			bad_condition = lhs.arguments[1] == rhs.arguments[1]
			if not bad_condition:
				matched_equation = e
				break

	if matched_equation is None:
		return U

	print("++++++++++Applying LC+++++++++++++")
	print(matched_equation)
	print(U)
	print("+++++++++++++++++++++++++++++++++")


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
	
	print("---------After applying LC---------------")
	print(U)
	print("-----------------------------------------")
	return U

#Mutation Rule MC
def mutation_rule7(U: Set[Equation], var_count: List[int]) -> Set[Equation]:
	print("=======In MC Rule ======")
	print(U)
	print("========================")
	matched_equation: Optional[Equation] = None
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			# TODO: Is this condition complete?
			# NOTE: This is a distinct variable check
			if len(get_vars(e.right_side, unique=True).union(get_vars(e.left_side, unique=True))) == 4:
				matched_equation = e
				break

	if matched_equation is None:
		return U

	print("++++++++++Applying MC+++++++++++++")
	print(matched_equation)
	print(U)
	print("++++++++++++++++++++++++++++++++++")

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
	
	print("--------After applying MC------------")
	print(U)
	print("-------------------------------------")

	return U


##########################################################
############# S Rules                     ################
##########################################################

def merge(equations: Set[Equation], restricted_vars: Set[Variable]) -> Tuple[Set[Equation], bool]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x is a variable and s and t are not variables
	Returns new set of equations and whether merge was applied
	"""
	#Bug in this code, the for loop will double match and remove x = s when it is supposed to keep it.
	#the break below is a hack fix
	applied_merge = False
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
			applied_merge = True
			print("Applying merge on: ")
			print(e1)
			print(e2)
			remove_equations.add(e2)
			if (Equation(e1.right_side, e2.right_side) not in add_equations) and (Equation(e2.right_side, e1.right_side) not in add_equations):
				add_equations.add(Equation(
					e1.right_side,
					e2.right_side
				))
			break
	print("New set of equations after merge: ")
	print(equations)
	print(remove_equations)
	print(add_equations)
	print((equations - remove_equations).union(add_equations))
	return (equations - remove_equations).union(add_equations), applied_merge

def non_flat_check(eqs):
	for eq in eqs:
		if isinstance(eq.left_side, FuncTerm) and isinstance(eq.right_side, FuncTerm):
			return True
	return False

def orient_andrew(equations, original_equations):
	VS1 = helper_gvs(original_equations)
	new_equations = set()

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		if not isinstance(lhs, Variable) and isinstance(rhs, Variable):
			new_equations.add(Equation(
                  rhs, lhs
             ))
		elif isinstance(lhs, Variable) and isinstance(rhs, Variable) and \
			rhs in VS1 and lhs not in VS1:
			new_equations.add(Equation(
				rhs, lhs
			))
		else:
			new_equations.add(equation)
	return new_equations

def var_rep_andrew(equations):
	matched_equation: Optional[Equation] = None

	for equation in equations:
		lhs = equation.left_side
		rhs = equation.right_side
		rest_vars = helper_gvs(equations - {equation})
		if isinstance(lhs, Variable) and lhs in rest_vars:
			matched_equation = equation

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
            equation.left_side * new_sub,
            equation.right_side * new_sub
        ))

    # Add the matched equation to the result
	new_equations.add(matched_equation)

	return new_equations

def delete_trivial_brandon(equations, original_equations):
	new_equations = set()
	VS1 = helper_gvs(original_equations)

	for equation in equations:
		lhs = equation.left_side
		rest_vars = helper_gvs(equations - {equation})
		if not (isinstance(lhs, Variable) and lhs not in rest_vars and lhs not in VS1):
			new_equations.add(equation)

	return new_equations


from .common import variable_replacement

def s_rules(U: Set[Equation], var_count, ES1):
	"""
	S Rules
	"""
	print("in S rules\n")
	print(U)
	Utemp = set()
	U = deepcopy(U)
	U, var_count[0] = flat(U, var_count[0])
	while (Utemp != U):
		Utemp = U
		U = orient_andrew(U, ES1)
		U = var_rep_andrew(U)
		U = delete_trivial_brandon(U, ES1)
		if occurs_check(U):
			print("Found Occurs Check in: ")
			print(U)
			return set()

	U = deepcopy(U)
	U, var_count[0] = flat(U, var_count[0])
	# NOTE: Need occurs check here
	if occurs_check(U):
		print("Found Occurs check after flat in: ")
		print(U)
		return set()

	return U


def apply_mutation_rules(
		cn: MutateNode, var_count: int,
		Q: List[MutateNode], Tree: List[List[MutateNode]], level: int):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	nextBranch: List[Tuple[MutateNode, int]] = []

	dcopy = deepcopy(cn.data)
	cn.id = MutateNode(mutation_rule1(dcopy, var_count))
	if not already_explored(cn.id, Tree):
		nextBranch.append((cn.id, level + 1))

	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count))
	if not already_explored(cn.c, Tree):
		nextBranch.append((cn.c, level + 1))

	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
	if not already_explored(cn.a1, Tree):
		nextBranch.append((cn.a1, level + 1))

	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
	if not already_explored(cn.a2, Tree):
		nextBranch.append((cn.a2, level + 1))

	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
	if not already_explored(cn.rc, Tree):
		#Q.append(cn.rc)
		nextBranch.append((cn.rc, level + 1))

	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
	if not already_explored(cn.lc, Tree):
		nextBranch.append((cn.lc, level + 1))

	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
	if not already_explored(cn.mc, Tree):
		nextBranch.append((cn.mc, level + 1))

	Tree[level + 1].extend([c for c, _ in nextBranch])
	Q.extend(nextBranch)


Tree = None
from collections import defaultdict

def build_tree(root: MutateNode, var_count, ES1, single_sol):
	global Tree
	Sol = list()
	Q = list()
	Q.append((root, 0))
	Tree = defaultdict(list)
	Tree[0] = [root]
	current_level = 0
	while 0 < len(Q):
		if current_level > 100:
			print("[HIT UPPER BOUND]")
			break
		if current_level > 3:
			print("Stopping after level 3")
			raise Exception("")

		cn, level = Q.pop(0)

		if level > current_level:
			print("=" * 5)
			print("Layer", current_level)
			last_branch = Tree[current_level]
			for node in last_branch:
				print(node.data)
			print("=" * 5)
			current_level = level


		#Apply S rules - mutate
		# print("Mutate rule count", mutate_rule_count)
		cn.data = s_rules(cn.data, var_count, ES1)
		if len(cn.data) > 0:
			cn.data, applied_merge = merge(cn.data, set())
			if not applied_merge:
				# Check failure conditions
				if not occurs_check(cn.data) and not function_clash(cn.data):
					Sol.append(cn.data)
			else:
				print('-' * 5)
				print("About to Mutate", cn.data)
				apply_mutation_rules(cn, var_count, Q, Tree, level)
				print('-' * 5)


	return Sol

def synt_ac_unif2(U: Set[Equation], single_sol: bool = True):
	var_count = [0]
	#flatten equations:
	ES1 = deepcopy(U)
	U, var_count[0] = flat(deepcopy(U), 0)
	# print(U)
	N1 = MutateNode(U)
	res = build_tree(N1, var_count, ES1, single_sol)
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
