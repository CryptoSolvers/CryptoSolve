"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.

To see examples of how the inference rules work, please run $ python3 test.py
in the same directory as this file
"""

from typing import Tuple, Dict, List, Optional, Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation, get_vars
from symcollab.xor import xor
from symcollab.xor.xorhelper import is_XOR_Term, is_xor_term, xor_to_list
from symcollab.xor.structure import Zero, is_zero
from copy import deepcopy

f = Function("f", 1)
zero = Zero()
c = Function("C", 3)
p = Constant('p')
q = Constant('q')
i = Constant('i')
j = Constant('j')

# Check the symbolic security of moo
def symbolic_check(moo_gen):
	g = list(gamma(moo_gen, "p", "i", "q", "j"))
	for m in range(len(g)):
		for m_prime in range(m+1, len(g)):
			xor_term = xor(g[m], g[m_prime])
			xor_equation_set = set([Equation(xor_term, zero)])
			inference_result = infer(xor_equation_set, g[m], g[m_prime], moo_gen)
			if not inference_result:
				return False
	return True

# Apply the inference rules until no longer possible.
def infer(s : Set[Equation], tm, tm_prime, moo_gen):

	print("Current set of equations: ", s)
	ret_value = False

	s_new = elim_f(s)
	if s != s_new:
		print("Applied elim_f rule")
		print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	s_new = elim_c(s)
	if s != s_new:
		print("Applied elim_c rule")
		print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime,moo_gen)

	s_new = occurs_check(s)
	if s != s_new:
		print("Applied occurs_check rule")
		print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	s_new = pick_f(s)
	if s != s_new:
		print("Applied pick_f rule")
		print("Infered set: ", s_new)
		for s_eq in s_new:
			ret_value = infer(s_eq, tm, tm_prime, moo_gen) or ret_value
		return ret_value

	s_new = pick_c(s, tm, tm_prime, moo_gen)
	if s != s_new:
		print("Applied pick_c rule")
		print("Infered set: ", s_new)
		for s_eq in s_new:
			ret_value = infer(s_eq, tm, tm_prime, moo_gen) or ret_value
		return ret_value

	s_new = pick_fail(s, moo_gen)
	if s != s_new:
		print("Applied pick_fail rule")
		print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	print("No rules apply!")
	if len(s) > 0:
		return False
	else:
		return True

# Compute the set Gamma
def gamma(moo_gen, p_label, i_label, q_label, j_label):
	cpi = moo_gen(p_label, i_label)
	cqj = moo_gen(q_label, j_label)
	return set(top_f_terms(cpi)).union(set(top_f_terms(cqj)))

# Return list of top-f-terms of a given cipher block term.
def top_f_terms(cipher_block_term):
	xor_list = xor_to_list(cipher_block_term)
	is_f_predicate = lambda x: isinstance(x, FuncTerm) and x.function == f
	return list(filter(is_f_predicate, xor_list))

# Compute size_f of a mode of operation.
def compute_size_f(moo_gen, i):
	cipher_block = moo_gen("p", i)
	return len(top_f_terms(cipher_block))

"""
Given a set of equations, remove any in the form of f(t) = 0, returning
the new list
"""
def elim_f(sigma: Set[Equation]) -> Set[Equation]:
	elim_f_set = deepcopy(sigma)
	for eq in sigma:
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == f and is_zero(eq.right_side):
				elim_f_set.remove(eq)
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == f and is_zero(eq.left_side):
				elim_f_set.remove(eq)

	return elim_f_set

"""
Given a set of equations, remove those in the form of
C_{p,i-a} xor C_{q, j-a} = 0, where i!=j
Each equation is checked to see if it has the format of
C(p, i, a) xor C(q, j, a) = 0
if it matches then it will be removed, it is assumed that i!=j
"""
def elim_c(sigma: Set[Equation]) -> Set[Equation]:
	elim_c_set = deepcopy(sigma)
	for eq in sigma:
		args = None
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == xor and is_zero(eq.right_side):
				args = eq.left_side.arguments
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == xor and is_zero(eq.left_side):
				args = eq.right_side.arguments
		# if args == None that means the equation does not use xor
		if args!= None and len(args) == 2:
			t1 = args[0]
			t2 = args[1]
			t1_is_c = False # checking for format C(p, i, a) or
			t2_is_c = False # checking for format C(q, j, a)
			a1 = None
			a2 = None
			if isinstance(t1, FuncTerm) and t1.function == c \
			and isinstance(t2, FuncTerm) and t2.function == c:
				cargs1 = t1.arguments
				cargs2 = t2.arguments
				if len(cargs1) == 3 and len(cargs2) == 3:
					a1 = cargs1[2]
					a2 = cargs2[2]
					if cargs1[0] == p and cargs1[1] == i:
						t1_is_c = True
						if cargs2[0] == q and cargs2[1] == j:
							t2_is_c = True
					elif cargs1[0] == q and cargs1[1] == j:
						t1_is_c = True
						if cargs2[0] == p and cargs2[1] == i:
							t2_is_c = True
			if t1_is_c and t2_is_c and a1 == a2:
				elim_c_set.remove(eq)
	return elim_c_set

"""
Checks each equation in a set of equations for an occurs check
Does NOT check the entire set for an occurs check, only each equation one by one
For the general occurs check which considers the entire set, see the commented out
code at the bottom of this file
"""
def occurs_check(sigma: Set[Equation]) -> Set[Equation]:
	occurs_set = deepcopy(sigma)
	for e in sigma:
		t1 = e.left_side
		t2 = e.right_side
		if isinstance(t2, FuncTerm) and t1 in t2 or isinstance(t1, FuncTerm) and t2 in t1:
			occurs_set.remove(e)

	return occurs_set

"""
Implementing pick_f inference rule
"""
def pick_f(sigma: Set[Equation]) -> [Set[Equation]]:
	results = []
	backup = deepcopy(sigma)
	for eq in sigma:
		if check_xor_structure(eq.left_side) and is_zero(eq.right_side):
			n = len(xor_to_list(eq.left_side))
			sigmaMinusEq = deepcopy(sigma)
			sigmaMinusEq.remove(eq)
			for k in range(n):
				results.append(set(form_equations_list(eq.left_side, k)).union(sigmaMinusEq))
			return results
		elif check_xor_structure(eq.right_side) and is_zero(eq.left_side):
			n = len(xor_to_list(eq.right_side))
			sigmaMinusEq = deepcopy(sigma).remove(eq)
			for k in range(n):
				results = results.append(set(form_equations_list(eq.right_side, k)).union(sigmaMinusEq))
			return results
	return backup

def check_xor_structure(t: FuncTerm):
	if is_xor_term(t):
		if not isinstance(t.arguments[0], Variable) and t.arguments[0].function == f and not isinstance(t.arguments[1], Variable) and t.arguments[1].function == f:
			return True
		elif is_xor_term(t.arguments[0]) and not isinstance(t.arguments[1], Variable) and t.arguments[1].function == f:
			return check_xor_structure(t.arguments[0])
		else:
			return False
	else:
		return False

def form_equations_list(xorTerm: FuncTerm, k) -> Set[Equation]:
	subtermList = xor_to_list(xorTerm)
	tList = []
	tSubK = subtermList[k].arguments[0]
	for indexedFTerm in enumerate(subtermList, start=0):
		if not indexedFTerm[0] == k:
			fArg = indexedFTerm[1].arguments[0]
			tList.append(Equation(xor(tSubK,fArg), zero))
	return set(tList)

def pick_fail(sigma: Set[Equation], moo_gen) -> Set[Equation]:
	result_set = deepcopy(sigma)
	size_f = compute_size_f(moo_gen, 1)

	for eq in sigma:

		# term t, that is xor-rooted and t = 0 is an eq.
		t = None
        # Check if equation is of the form t = 0 or 0 = t where t is xor term
		if isinstance(eq.left_side, FuncTerm):
			if is_xor_term(eq.left_side) and is_zero(eq.right_side):
				t = eq.left_side
		elif isinstance(eq.right_side, FuncTerm):
			if is_xor_term(eq.right_side) and is_zero(eq.right_side):
				t = eq.right_side

		if t != None:
			termList = xor_to_list(t) # Convert the xor term to a list.
			cpis = list(filter(lambda xs: isinstance(xs, FuncTerm) and xs.function == c, termList)) # Find all C-rooted terms
			if len(cpis) == 1: # There can be only one C-rooted term for this rule to execute
				cpi = cpis[0]
				fs = list(filter(lambda ys: isinstance(ys, FuncTerm) and ys.function == f, termList)) # Find all f-rooted terms
				if len(fs) == len(termList)-1: # All other terms should be f-rooted, except the C
					if size_f > len(fs): # if size_f(Cpi) > n
						result_set.remove(eq) # conclusion
	return result_set

def pick_c(sigma: Set[Equation], tm: FuncTerm, tmPrime: FuncTerm, moo_gen) -> [Set[Equation]]:

	results = []
	size_f = compute_size_f(moo_gen, 1)

	for eq in sigma:

		# term t, that is xor-rooted and t = 0 is an eq.
		t = None

		# Check if equation is of the form t = 0 or 0 = t where t is xor term
		if isinstance(eq.left_side, FuncTerm):
			if is_xor_term(eq.left_side) == xor and is_zero(eq.right_side):
				t = eq.left_side
		elif isinstance(eq.right_side, FuncTerm):
			if is_xor_term(eq.right_side) == xor and is_zero(eq.right_side):
				t = eq.right_side

		if t != None:
			termList = xor_to_list(t)
			cpis = list(filter(lambda xs: isinstance(xs, FuncTerm) and xs.function == c, termList)) # Find all C-rooted terms
			if len(cpis) == 1: # There can be only one C-rooted term for this rule to execute
				cpi = cpis[0]
				fs = list(filter(lambda ys: isinstance(ys, FuncTerm) and ys.function == f, termList)) # Find all f-rooted terms
				if len(fs) == len(termList)-1: # All other terms should be f-rooted, except the C
					if size_f <= len(fs): # sizef(Cpi) <= n
						# Check Cpi \in CVar(tm) U CVar(tm')
						if tm.contains(cpi) or tmPrime.contains(cpi):
							unfold = moo_gen(int(cpi.subterms[0].symbol), int(cpi.subterms[1].symbol))
							f_rooted_summands = list(filter(lambda x: isinstance(x, FuncTerm) and x.function == f, xor_to_list(unfold)))
							for f_root_summand in f_rooted_summands:
								result_set = deepcopy(sigma)
								for k in fs:
									result_set.append(Equation(f_rooted_summand.subterms[0], k.subterms[0]))
								result_set.remove(eq)
								results.append(result_set)
							return results
	return sigma # Have to return the original set of equations.



# Example c generator for unfolding
def cbc_gen(p, i):
	if i == 0:
		return Constant('r'+str(p))
	else:
		return xor(
			FuncTerm(Function("f",1), [cbc_gen(p,i-1)]),
			Variable("x"+str(p)+str(i))
		)

def ex4_gen(p, i):
	if i == 0:
		return Constant('r'+str(p))
	else:
		return xor(
			xor (
					FuncTerm(f, [ex4_gen(p,i-1)]),
					FuncTerm(f, [FuncTerm(f, [ex4_gen(p,i-1)])])
				),
				Variable("x"+str(p)+str(i))
		)

# Treat the subscripts as labels
def symbolic_cbc_gen(session_label, block_label):

	a = Constant("1")
	p = Constant(session_label)
	i = Constant(block_label)

	cInner = FuncTerm(c, [p,i,a])
	x = Variable("xpi")
	return xor (
		FuncTerm(f, [cInner]),
		x
	)

def symbolic_ex4_gen(session_label, block_label):

	a = Constant("1")
	p = Constant(session_label)
	i = Constant(block_label)

	cInner = FuncTerm(c, [p,i,a])
	x = Variable("xpi")

	fSummandOne = FuncTerm(f, [cInner])

	fSummandTwo = FuncTerm(f, [FuncTerm(f, [cInner])])

	return xor (
		fSummandOne,
		fSummandTwo,
		x
	)

"""
def pick_f(sigma: Set[Equation]) -> Set[Equation]:

def pick_c(sigma: Set[Equation], cipherblock: Equation) -> Set[Equation]:

def pick_fail(sigma: Set[Equation], cipherblock: Equation) -> Set[Equation]:
	for eq in sigma:
		args = None
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == xor and is_zero(eq.right_side):
				args = eq.left_side.arguments
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == xor and is_zero(eq.left_side):
				args = eq.right_side.arguments
		if args != None && len(args) == 2:
			cpi = args[0]
			t = args[1]
"""

"""
# old code that might be useful for something else but isnt applicable in this situation

Given a set of equations, returns true if an occurs check exists between all of the equations
def occurs_check(sigma: Set[Equation]) -> bool:
	for e in sigma:
		var = None
		term = None
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			var = e.left_side
			term = e.right_side
		elif isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm):
			var = e.right_side
			term = e.left_side
		if var != None and term != None:
			if var in term:
				return True
			check_vars = set(get_vars(term))
			check_eq = deepcopy(sigma)
			check_eq.remove(e)
			if found_cycle(var, check_vars, check_eq):
				return True
	return False

Returns true when a cycle is found, which occurs when a variable is written in terms of itself
def found_cycle(target: Variable, check: Set[Variable], equations: Set[Equation]) -> bool:
	for var in check:
		if var == target:
			return True

		for e in equations:
			term = None
			if isinstance(e.left_side, Variable) and var == e.left_side:
				term = e.right_side
			elif isinstance(e.right_side, Variable) and var == e.right_side:
				term = e.left_side
			if term != None:
				eq = deepcopy(equations)
				eq.remove(e)
				return found_cycle(target, get_vars(term), eq)
	return False
"""
