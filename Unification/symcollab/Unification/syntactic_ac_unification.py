from copy import deepcopy
from typing import List, Set, Optional

import itertools

from symcollab.algebra import (
	get_vars, Equation, Variable, FuncTerm,
	Term, SubstituteTerm
)
from .common import orient

#Tree
class MutateNode:
	def __init__(self, data: list):
		self.id = None
		self.c = None
		self.a1 = None
		self.a2 = None
		self.rc = None
		self.lc = None
		self.mc = None
		self.data = data


#helper function for solved forms
def found_cycle(var: Variable, S: Set[Equation], U: Set[Equation]):
	for x in S:
		if x == var:
			return(True)
	for x in S:
		for e in U:
			if isinstance(e.left_side, Variable) and x == e.left_side:
				return(found_cycle(var, get_vars(e.right_side), U - {e}))
			elif isinstance(e.right_side, Variable) and x == e.right_side:
				return(found_cycle(var, get_vars(e.left_side), U - {e}))
	return(False)


#helper function for solved forms
def solved_form(U: Set[Equation]):
	#orient
	#print("Checking for solved form: ")
	#print(U)
	U = orient(U)

	ft = False
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			ft=True
			if isinstance(e.left_side, FuncTerm) :
				return(False)
	if not ft:
		V = list()
		for e in U:
			V.append(e.left_side)
		if len(V) == len(set(V)):
			return(True)
		else:
			return(False)
		
	# Check for duplicate assignments
	V = list()
	for e in U:
		if isinstance(e.left_side, Variable):
			V.append(e.left_side)
	if len(V) != len(set(V)):
		return(False)

	if occurs_check(U):
		return False

	#print("Yes, solved")
	return(True)


#helper function for solved forms dist vars
def solved_form_vd(U: Set[Equation], VS1: Set[Term]) -> bool:
	U = set(U) # TODO: Remove
	#orient
	#print("Checking solved form for : ")
	#print(U)
	U = orient(U)
	
	FTF = False
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			FTF=True
			if isinstance(e.left_side, FuncTerm):
				return(False)
	if not FTF:
		return(True)
	
	# Look for duplicate assignments
	V = list()
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1:
				V.append(e.left_side)
	if len(V) != len(set(V)):
		return(False)
	
	if occurs_check(U):
		return False

	#print("Yes it's solved")
	return(True)

#helper function to check for linear term
def linear(t: Term, VS1: Set[Term]):
	V = get_vars(t)
	VTL = list()
	for var in V:
		#if var not in VS1:
		VTL.append(var)
	if len(VTL) == len(set(VTL)):
		return(True)
	else:
		return(False)

#helper function to get the init set of vars
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
	var1 = str()
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = str()
	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
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
		return list(U) # TODO: Remove list

	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)
	
	var2 = 'v_'+str(var_count[0])
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
		return list(U) #TODO: Remove list
	
	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = 'v_'+str(var_count[0])
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
		return list(U) # TODO: Remove list
	
	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = 'v_'+str(var_count[0])
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
		return list(U) # TODO: Remove list
	
	#Create the 7 possible mutations
	U = U - {matched_equation}
	#ID
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = 'v_'+str(var_count[0])
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
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = 'v_'+str(var_count[0])
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
	var1 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var1 = Variable(var1)

	var2 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var2 = Variable(var2)

	var3 = 'v_'+str(var_count[0])
	var_count[0] = var_count[0] + 1
	var3 = Variable(var3)

	var4 = 'v_'+str(var_count[0])
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
############# S', vars distinct           ################
##########################################################


def is_orriented(e: Equation) -> bool:
	"""
	Variable on left side, non-variable on right side.
	Dran doesn't like the name of this function...
	"""
	return isinstance(e.left_side, Variable) and not isinstance(e.right_side, Variable)


def merge(equations: Set[Equation], VS1: Set[Term]) -> Set[Equation]:
	"""
	(x = s) /\ (x = t) -> (x = s) /\ (s = t)
	if x not in VS1
	"""
	#print("U before merge: ")
	#print(equations)
	remove_equations = set()
	add_equations = set()
	for e1, e2 in itertools.product(equations, equations):
		# Require orriented equation with variable not in VS1
		e1_matches = is_orriented(e1) and e1.left_side not in VS1
		if not e1_matches:
			continue
		
		# Require distinct orriented equation with matching variable
		e2_matches = is_orriented(e2) and e1 != e2 and e1.left_side == e2.left_side
		if not e2_matches:
			continue
		
		# Rule applies
		remove_equations.add(e2)
		add_equations.add(Equation(
			e1.right_side,
			e2.right_side
		))
	
	#print("U after merge: ")
	#print((equations - remove_equations).union(add_equations) )

	return (equations - remove_equations).union(add_equations) 


def occurs_check(equations: Set[Equation]) -> bool:
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			S = set(get_vars(e.right_side))
			if found_cycle(e.left_side, S, equations - {e}) == True:
				return True
	return False

def create_substitution_from_equations(equations: Set[Equation], VS1: Set[Term]) -> SubstituteTerm:
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

def variable_replacement_vd(equations: Set[Equation], VS1: Set[Term]) -> Set[Equation]:
	#print("U before var-rep-vd: ")
	#print(equations)
	# Look for candidate equations to variable replace
	candidate_equations = set()
	for e in equations:
		variable_equality = isinstance(e.left_side, Variable) \
			and isinstance(e.right_side, Variable)
		if not variable_equality:
			continue
			
		if e.left_side in VS1:
			continue
		
		if e.left_side not in helper_gvs(equations - {e}):
			continue

		already_exists = any((e2.left_side == e.left_side for e2 in candidate_equations))
		if already_exists:
			continue
		
		# Add equation to ones we'll variable replace
		candidate_equations.add(e)

	if len(candidate_equations) == 0:
		return equations

	# Create substitution 
	delta = create_substitution_from_equations(candidate_equations, VS1)
	
	# Apply substitution
	add_equations = set()
	remove_equations = set()
	for e in (equations - candidate_equations):
		remove_equations.add(e)
		add_equations.add(Equation(
			e.left_side * delta,
			e.right_side * delta
		))
	
	#print("U after var-rep-vd: ")
	#print((equations - remove_equations).union(add_equations))

	return (equations - remove_equations).union(add_equations)


def replacement(equations: Set[Equation], VS1: Set[Term]) -> Set[Equation]:
	#print("U before replacement: ")
	#print(equations)
	candidate_equations = set()
	for e1 in equations:
		if not is_orriented(e1):
			continue
		if e1.left_side in VS1:
			continue
		already_exists = any((e2.left_side == e1.left_side for e2 in candidate_equations))
		if already_exists:
			continue

		candidate_equations.add(e1)
	
	if len(candidate_equations) == 0:
		return equations
	
	# Create Substitution
	delta = create_substitution_from_equations(candidate_equations, VS1)
	#print("Delta 2:")
	#print(delta)

	# Apply Substitution
	remove_equations = set()
	add_equations = set()
	for e in (equations - candidate_equations):
		remove_equations.add(e)
		add_equations.add(Equation(
			e.left_side * delta,
			e.right_side * delta
		))
	
	#print("U after replacement: ")
	#print((equations - remove_equations).union(add_equations))

	return (equations - remove_equations).union(add_equations)


def eqe_vd(equations: Set[Equation], VS1: Set[Term]):
	# print("U before EQE-VD: ")
	# print(equations)
	VP = helper_gvs(set(equations))
	equations_to_remove = set()
	for e in equations:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1:
				ST = VP.difference(get_vars(e.left_side, unique=True))
				if e.left_side not in ST:
					equations_to_remove.add(e)
		elif isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable):
			if e.left_side not in VS1: # and e.right_side in VS1:
				ST = VP.difference({e.left_side})
				if e.left_side not in ST:
					equations_to_remove.add(e)

	# print("U after EQE-VD: ")
	# print((equations - equations_to_remove))

	return (equations - equations_to_remove)



def s_rules_vd(U: Set[Equation], VS1: Set[Term]):
	U = orient(U)
	U = merge(U, VS1)

	# Occurs Check
	if occurs_check(U):
		#print("Occurs check: ")
		#print(U)
		return set()

	U = variable_replacement_vd(U, VS1)
	U = replacement(U, VS1)
	U = eqe_vd(U, VS1)

	return U


def variable_replacement(equations: Set[Equation], VS1: Set[Term]) -> Set[Equation]:
	# print("U before variable-replacement", equations)

	# Find candidate equations
	candidate_equations = set()
	for e in equations:
		variable_equality = isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable)
		if not variable_equality:
			continue
		
		if e.left_side in VS1:
			if e.right_side in VS1:
				continue
			
			etemp = Equation(e.right_side, e.left_side)
			already_exists = any((e2.left_side == etemp.left_side for e2 in candidate_equations))
			if not already_exists:
				candidate_equations.add(etemp)
		
		else:
			already_exists = any((e2.left_side == e.left_side for e2 in candidate_equations))
			if not already_exists:
				candidate_equations.add(e)


	#print("Here is candidate_equations: ")
	#print(candidate_equations)
	# Create substitution
	delta = SubstituteTerm()
	for e in candidate_equations:
		if e.left_side in VS1:
			delta.add(e.right_side, e.left_side)
		else:
			delta.add(e.left_side, e.right_side)

	# Apply substitution
	add_equations = set()
	remove_equations = set()
	for e in (equations - candidate_equations):
		remove_equations.add(e)
		add_equations.add(Equation(
			e.left_side * delta,
			e.right_side * delta
		))
	
	# print("U after variable-replacement")
	# print((equations - remove_equations).union(add_equations))

	return (equations - remove_equations).union(add_equations)


def eqe(equations: Set[Equation], VS1: Set[Term]) -> Set[Equation]:
	#print("U before EQE: ")
	#print(equations)
	equations_to_remove = set()
	for e in equations:
		ST = helper_gvs(equations - {e})
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1 and e.left_side not in ST:
				equations_to_remove.add(e)
		elif isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable):
			if e.left_side not in VS1 and e.left_side not in ST:
				equations_to_remove.add(e)
			elif e.right_side not in VS1 and e.right_side not in ST:
				equations_to_remove.add(e)
	
	#print("U after EQE: ")
	#print(equations - equations_to_remove)

	return equations - equations_to_remove


def s_rules(U: Set[Equation], VS1: Set[Equation]):
	U = orient(U)
	U = merge(U, set())
	U = variable_replacement(U, VS1)
	U = replacement(U, set())

	if occurs_check(U):
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
					return list()
	
	
	return U

def apply_mutation_rules(cn: MutateNode, var_count: int, Q: List[MutateNode]):
	"""
	Applies mutation rules and adds nodes to the queue
	"""
	dcopy = deepcopy(cn.data) 
	cn.id = MutateNode(mutation_rule1(dcopy, var_count))
	Q.append(cn.id)
	dcopy = deepcopy(cn.data)
	cn.c = MutateNode(mutation_rule2(dcopy, var_count))
	Q.append(cn.c)
	dcopy = deepcopy(cn.data)
	cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
	Q.append(cn.a1)
	dcopy = deepcopy(cn.data)
	cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
	Q.append(cn.a2)
	dcopy = deepcopy(cn.data)
	cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
	Q.append(cn.rc)
	dcopy = deepcopy(cn.data)
	cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
	Q.append(cn.lc)
	dcopy = deepcopy(cn.data)
	cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
	Q.append(cn.mc)
	
def build_tree(root: MutateNode, var_count, VS1, single_sol):
	EQS = list()
	Sol = list()
	Q = list()
	Q.append(root)
	################### Step 1 #########################
	#the upper length bound will be removed when we add pruning
	while len(Q) > 0:
		cn = Q.pop(0)
		#Apply S rules
		Max = 20
		count = 0
		Utemp = set()
		# While applying the rule changes...
		while (Utemp != cn.data):
			#print("Starting S rules: step(" +str(count) +")")
			Utemp = cn.data
			cn.data = s_rules_vd(cn.data, VS1)
			count = count + 1
			#print("U after S rules: ")
			#print(cn.data)
			if count > Max: #Remove after testing
				print("Hit Max")
				break
		if len(cn.data) > 0:
			if solved_form_vd(cn.data, VS1):
				EQS.append(cn.data)
			else:
				apply_mutation_rules(cn, var_count, Q)
		#print("Len 1: " + str(len(Q)))
	
	#print("The final length of EQS: ")
	#print(len(EQS))
	#print(EQS)
	################### Step 2, 3, 4 ###################
	for s in EQS:
		Q = list()
		root = MutateNode(s)
		Q.append(root)
		#the upper length bound will be removed when we add pruning
		while len(Q) > 0:
			cn = Q.pop(0)
			#Apply S rules - mutate
			Max = 20
			count =0
			Utemp = set()
			#print("Starting for problem: ")
			#print(cn.data)
			while (Utemp != cn.data):
				Utemp = cn.data
				#print("U before S rules: ")
				#print(cn.data)
				cn.data = s_rules(cn.data, VS1)
				count = count + 1
				#print("U after S rules: ")
				#print(cn.data)
				if count > Max: #Will remove when we add pruning rule
					print("Hit Max")
					break
			if len(cn.data) > 0:
				if solved_form(cn.data):
					Sol.append(cn.data)
					if single_sol:
						return Sol
				else:
					apply_mutation_rules(cn, var_count, Q)
			#print("Len 2: " + str(len(Q)))
	return(Sol)

def synt_ac_unif(U: Set[Equation], single_sol: bool = True):
	#print("Syntactic AC-Unification on the following problem: ")
	#print(U)
	var_count = [0] # Seems to be a global variable hack
	#get the intial set of vars
	VS1 = helper_gvs(U)
	N1 = MutateNode(U)
	res = build_tree(N1, var_count, VS1, single_sol)
	
	final_sol = set()
	for solve in res:
		delta = SubstituteTerm()
		for e in solve:
			try:
				delta.add(e.left_side, e.right_side)
			except:
				print("error adding substitution")
		final_sol.add(delta)
	
	#print("Solution: ")
	#if res == set():
	#	print("No solution found")
	#else:
	#	for s in res:
	#		print(s)
	
	return(final_sol)
