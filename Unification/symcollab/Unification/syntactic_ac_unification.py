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

def apply_substitution_on_equations(delta: SubstituteTerm, U: Set[Equation]):
	add_equations = set()
	remove_equations = set()
	for e in U:
		remove_equations.add(e)
		add_equations.add(Equation(
			e.left_side * delta,
			e.right_side * delta
		))

	return (U - remove_equations).union(add_equations)

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

def already_explored(m: MutateNode, Tree: List[List[MutateNode]]):
	# TODO: Check for equilvalence modulo renaming
	for branch in Tree:
		for q in branch:
			if m.data == q.data:
				return True
	return False

#helper function for solved forms
def solved_form(U: Set[Equation], VS1: Set[Variable]):
	#print("Checking for solved form: ")
	#print(U)
	U = orient(U)

	V: List[Variable] = []
	# Make sure every equation starts with a variable
	# on the left side.
	for e in U:
		if not isinstance(e.left_side, Variable):
			return False
		if e.left_side not in VS1:
			V.append(e.left_side)
	
	# Check for duplicate assignments
	if len(V) != len(set(V)):
		return False

	if occurs_check_full(U):
		return False

	return True

#helper function to check for linear term
def linear(t: Term, VS1: Set[Term]):
	V = get_vars(t)
	# False if there are duplicate variables within a term
	return len(V) == len(set(V))

# Helper function to retrieve a set of variables from a set of equations
def helper_gvs(U: Set[Equation]):
	V = set()
	for e in U:
		V = V.union(get_vars(e.left_side))
		V = V.union(get_vars(e.right_side))
	return(V)


#Rules

#Mutation Rule ID
def mutation_rule1(U: Set[Equation], var_count: List[int]):
	# print("U before ID: ")
	# print(U)
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
	m1.add(Equation(var1, matched_equation.left_side.arguments[0]))
	m1.add(Equation(var1, matched_equation.right_side.arguments[0]))
	m1.add(Equation(var2, matched_equation.left_side.arguments[1]))
	m1.add(Equation(var2, matched_equation.right_side.arguments[1]))
	U = U.union(m1)

	U = orient(U)
	#print("U after ID :")
	#print(U)
	return(U)

#Mutation Rule C
def mutation_rule2(U: Set[Equation], var_count: List[int]):
	#print("U before C: ")
	#print(U)
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
	m1.add(Equation(var1, matched_equation.left_side.arguments[0]))
	m1.add(Equation(var2, matched_equation.right_side.arguments[0]))
	m1.add(Equation(var2, matched_equation.left_side.arguments[1]))
	m1.add(Equation(var1, matched_equation.right_side.arguments[1]))
	U = U.union(m1)

	U = orient(U)
	#print("U after C: ")
	#print(U)
	return U

#Mutation Rule A1
def mutation_rule3(U: Set[Equation], var_count: List[int]):
	#print("U before A1: ")
	#print(U)
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

	U = orient(U)

	#print("U after A1: ")
	#print(U)
	return U

#Mutation Rule A2
def mutation_rule4(U: Set[Equation], var_count: List[int]):
	#print("U before A2: ")
	#print(U)
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
	m1.add(Equation(var1, matched_equation.left_side.arguments[0]))
	m1.add(Equation(matched_equation.left_side.arguments[1], t2))
	m1.add(Equation(matched_equation.right_side.arguments[0], t1))
	m1.add(Equation(var3, matched_equation.right_side.arguments[1]))
	U = U.union(m1)

	U = orient(U)

	#print("U after A2: ")
	#print(U)
	return U

#Mutation Rule RC
def mutation_rule5(U: Set[Equation], var_count: List[int]):
	#print("U before RC: ")
	#print(U)

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
	m1.add(Equation(var3, matched_equation.left_side.arguments[1]))
	m1.add(Equation(matched_equation.right_side.arguments[0], t2))
	m1.add(Equation(var2, matched_equation.right_side.arguments[1]))
	U = U.union(m1)

	U = orient(U)

	#print("U after RC: ")
	#print(U)
	return U

#Mutation Rule LC
def mutation_rule6(U: Set[Equation], var_count: List[int]):
	#print("U before LC: ")
	#print(U)
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
	m1.add(Equation(var1, matched_equation.left_side.arguments[0]))
	m1.add(Equation(matched_equation.left_side.arguments[1], t1))
	m1.add(Equation(var2, matched_equation.right_side.arguments[0]))
	m1.add(Equation(matched_equation.right_side.arguments[1], t2))
	U = U.union(m1)


	U = orient(U)

	#print("U after LC: ")
	#print(U)
	return U

#Mutation Rule MC
def mutation_rule7(U: Set[Equation], var_count: List[int]):
	#print("U before MC: ")
	#print(U)
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

	U = orient(U)

	#print("U after MC: ")
	#print(U)
	return U


##########################################################
############# S Rules                     ################
##########################################################

def merge(equations: Set[Equation], VS1: Set[Variable]) -> Set[Equation]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x not in VS1
	"""
	#print("U before merge: ")
	#print(equations)
	remove_equations = set()
	add_equations = set()
	for e1, e2 in itertools.product(equations, equations):
		# Skip if the two equations are the same
		if e1 == e2:
			continue

		# Conditions for merge
		matching_left_variable = e1.left_side == e2.left_side and isinstance(e1.left_side, Variable)
		right_side_not_variable = not isinstance(e1.right_side, Variable) and not isinstance(e2.right_side, Variable)
		not_within_vs1 = e1.left_side not in VS1

		if matching_left_variable and right_side_not_variable and not_within_vs1:
			remove_equations.add(e2)
			add_equations.add(Equation(
				e1.right_side,
				e2.right_side
			))

	#print("U after merge: ")
	#print((equations - remove_equations).union(add_equations) )

	return (equations - remove_equations).union(add_equations)

def create_substitution_from_equations(equations: Set[Equation], VS1: Set[Variable]) -> SubstituteTerm:
	delta = SubstituteTerm()
	for e in equations:
		if not isinstance(e.left_side, Variable):
			raise Exception("create_substitution_from_equations require orriented equations")

		# Determine ordering of substitution
		if not isinstance(e.right_side, Variable):
			delta.add(e.left_side, e.right_side)
		elif e.right_side in VS1:
			delta.add(e.left_side, e.right_side)
		else:
			calc_index = lambda x: int("".join(filter(str.isdigit, "0" + str(x))))
			temp1=calc_index(e.left_side)
			temp2=calc_index(e.right_side)
			if temp1 <= temp2:
				delta.add(e.right_side, e.left_side)
			else:
				delta.add(e.left_side, e.right_side)
	return delta

def variable_replacement(equations: Set[Equation], VS1: Set[Variable]) -> Set[Equation]:
	#print("U before var-rep-vd: ")
	#print(equations)
	# Look for candidate equations to variable replace
	candidate_equations = set()
	for e in equations:
		"""
		Old version of variable_replacement included:
		if e.left_side in VS1:
			if e.right_side in VS1:
				continue

			etemp = Equation(e.right_side, e.left_side)
			already_exists = any((e2.left_side == etemp.left_side for e2 in candidate_equations))
			if not already_exists:
				candidate_equations.add(etemp)
		"""


		# Conditions
		both_sides_variables = isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable)
		variables_in_P = helper_gvs(equations - {e})
		exists_within_p = e.left_side in variables_in_P and e.right_side in variables_in_P
		not_within_vs1 = e.left_side not in VS1 and e.right_side not in VS1

		if both_sides_variables and exists_within_p and not_within_vs1:
			already_exists = any((e.left_side in [ce.left_side, ce.right_side] or e.right_side in [ce.left_side, ce.right_side] for ce in candidate_equations))
			if not already_exists:
				candidate_equations.add(e)

	if len(candidate_equations) == 0:
		return equations

	# Create substitution
	delta = create_substitution_from_equations(candidate_equations, VS1)

	# Apply substitution
	substituted_equations = apply_substitution_on_equations(delta, equations - candidate_equations)

	return substituted_equations.union(candidate_equations)

def replacement(equations: Set[Equation], VS1: Set[Variable]) -> Set[Equation]:
	#print("U before replacement: ")
	#print(equations)
	candidate_equations = set()
	for e in equations:
		# Conditions
		variable_left_side = isinstance(e.left_side, Variable)
		nonvariable_right_side = not isinstance(e.right_side, Variable)
		left_not_within_right = e.left_side not in get_vars(e.right_side)
		not_within_vs1 = e.left_side not in VS1

		if variable_left_side and nonvariable_right_side and left_not_within_right and not_within_vs1:
			already_exists = any((ce.left_side == e.left_side for ce in candidate_equations))
			if not already_exists:
				candidate_equations.add(e)

	if len(candidate_equations) == 0:
		return equations

	# Create Substitution
	delta = create_substitution_from_equations(candidate_equations, VS1)
	#print("Delta 2:")
	#print(delta)

	# Apply Substitution
	substituted_equations = apply_substitution_on_equations(delta, equations - candidate_equations)

	return substituted_equations.union(candidate_equations)

def eqe(equations: Set[Equation], VS1: Set[Variable]):
	# print("U before EQE-VD: ")
	# print(equations)
	equations_to_remove = set()
	for e in equations:
		# Conditions
		variable_left_side = isinstance(e.left_side, Variable)
		variables_in_right_side = set(get_vars(e.right_side))
		variables_in_P = helper_gvs(equations - {e})
		not_in_SP = e.left_side not in variables_in_right_side.union(variables_in_P)
		not_in_VS1 = e.left_side not in VS1

		if variable_left_side and not_in_SP and not_in_VS1:
			equations_to_remove.add(e)

	# print("U after EQE-VD: ")
	# print((equations - equations_to_remove))

	return (equations - equations_to_remove)

def s_rules_vd(U: Set[Equation], VS1: Set[Variable]):
	U = orient(U)
	U = merge(U, VS1)

	# Occurs Check
	if occurs_check_full(U):
		#print("Occurs check: ")
		#print(U)
		return set()

	U = variable_replacement(U, VS1)
	U = replacement(U, VS1)
	U = eqe(U, VS1)

	return U

def s_rules(U: Set[Equation], VS1: Set[Equation]):
	U = orient(U)
	U = merge(U, set())
	U = variable_replacement(U, set())
	U = replacement(U, set())

	if occurs_check_full(U):
		#print("Occurs check: ")
		#print(U)
		return(set())

	U = eqe(U, VS1)

	#Prune rule
	VS2 = helper_gvs(U)
	VS2 = VS2.difference(VS1)
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side in VS2:
				if not linear(e.right_side, VS1):
					#print("Prune: ")
					#print(e)
					print("Prune rule applied")
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
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count))
	if not already_explored(cn.c, Tree):
		nextBranch.append(cn.c)
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
	if not already_explored(cn.a1, Tree):
		nextBranch.append(cn.a1)
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
	if not already_explored(cn.a2, Tree):
		nextBranch.append(cn.a2)
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
	if not already_explored(cn.rc, Tree):
		Q.append(cn.rc)
		nextBranch.append(cn.rc)
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
	if not already_explored(cn.lc, Tree):
		nextBranch.append(cn.lc)
	else:
		print("Pruning Branch")

	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
	if not already_explored(cn.mc, Tree):
		nextBranch.append(cn.mc)
	else:
		print("Pruning Branch")
	
	Tree.append(nextBranch)
	Q.extend(nextBranch)


def build_tree(root: MutateNode, var_count, VS1, single_sol):
	EQS = list()
	Sol = list()
	Q: List[MutateNode] = list()
	Tree: List[List[MutateNode]] = list()
	Q.append(root)
	Tree.append([root])
	################### Step 1 #########################
	#the upper length bound will be removed when we add pruning
	while 0 < len(Q):
		cn = Q.pop(0)
		# print(cn)
		#Apply S rules
		Utemp = set()
		# While applying the rule changes...
		while (Utemp != cn.data):
			Utemp = cn.data
			cn.data = s_rules_vd(cn.data, VS1)
			#print("U after S rules: ", cn.data)
		if len(cn.data) > 0:
			if solved_form(cn.data, VS1):
				EQS.append(cn.data)
			else:
				apply_mutation_rules(cn, var_count, Q, Tree)
		#print("Len 1: " + str(len(Q)))

	#print("The final length of EQS: ")
	#print(len(EQS))
	#print(EQS)
	################### Step 2, 3, 4 ###################
	for s in EQS:
		Q = []
		Tree = []
		root = MutateNode(s)
		Q.append(root)
		Tree.append([root])
		#the upper length bound will be removed when we add pruning
		while 0 < len(Q) < 1000:
			cn = Q.pop(0)
			#Apply S rules - mutate
			Utemp = set()
			#print("Starting for problem: ", cn.data)
			while (Utemp != cn.data): # Remove once pruning is improved
				Utemp = cn.data
				#print("U before S rules: ", cn.data)
				cn.data = s_rules(cn.data, VS1)
				#print("U after S rules: ", cn.data)
			if len(cn.data) > 0:
				if solved_form(cn.data, set()):
					Sol.append(cn.data)
					if single_sol:
						return Sol
				else:
					apply_mutation_rules(cn, var_count, Q, Tree)
			#print("Len 2: " + str(len(Q)))
	return(Sol)

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
