"""
Functions that check symbolically
the security of a mode of operation.

Based on Hai Lin's work.
"""

from typing import Set
from symcollab.algebra import Term, Function, Variable, Constant, FuncTerm, Equation
from symcollab.xor import xor
from symcollab.xor.xorhelper import is_xor_term, xor_to_list
from symcollab.xor.structure import Zero, is_zero
from copy import deepcopy
from .generator import MOOGenerator

f = Function("f", 1)
zero = Zero()
c = Function("C", 3)
p = Constant('p')
q = Constant('q')
i = Constant('i')
j = Constant('j')

def start(moo_generator):
	pattern = next(moo_generator)
	return lambda block_label, session_label: moo_mapper(pattern, block_label, session_label)

def moo_mapper(generated_moo_term, block_label, session_label):
	if isinstance(generated_moo_term, Variable): # base cases
		var_name = generated_moo_term.symbol[0] # Assuming 'C' or 'P'
		subscripts = generated_moo_term.symbol.split('[')[1].split(']')[0].split('-')

		if len(subscripts) > 1:
			index = subscripts[1]
		else:
			index = "0"

		if var_name == 'C':
			return c(Constant(block_label),Constant(session_label),Constant(index))
		elif var_name == 'P':
			return Variable(f'x{block_label}{index}')
		else:
			raise Exception("Unknown variable symbol found.")

	else: # Function symbol
		fun_name = generated_moo_term.function.symbol
		if fun_name == 'f':
			return f(moo_mapper(generated_moo_term.arguments[0], block_label, session_label)) # Recurse
		elif fun_name == 'xor':
			return xor(
				moo_mapper(generated_moo_term.arguments[0],block_label, session_label),
				moo_mapper(generated_moo_term.arguments[1],block_label, session_label)
			)
		elif fun_name == 'r':
			return c(p,zero,zero)
		else:
			raise Exception("Unknown function symbol found")

# Check the symbolic security of moo
def symbolic_check(moo_gen):
	"""Check the symbolic security of a MOO"""
	g = list(gamma(moo_gen, "p", "i", "q", "j"))
	if len(g) == 0:
		return False
	for m in range(len(g)):
		for m_prime in range(m+1, len(g)):
			xor_term = xor(g[m], g[m_prime])
			xor_equation_set = set([Equation(xor_term, zero)])
			inference_result = infer(xor_equation_set, g[m], g[m_prime], moo_gen)
			if not inference_result:
				return False
	return True

def infer(s : Set[Equation], tm, tm_prime, moo_gen):
	"""Apply the inference rules until no longer possible."""

	#print("Current set of equations: ", s)
	ret_value = False

	s_new = elim_f(s)
	if s != s_new:
		#print("Applied elim_f rule")
		#print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	s_new = elim_c(s)
	if s != s_new:
		#print("Applied elim_c rule")
		#print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime,moo_gen)

	s_new = occurs_check(s)
	if s != s_new:
		#print("Applied occurs_check rule")
		#print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	s_new = pick_f(s)
	if s != s_new:
		#print("Applied pick_f rule")
		#print("Infered set: ", s_new)
		for s_eq in s_new:
			ret_value = infer(s_eq, tm, tm_prime, moo_gen) or ret_value
		return ret_value

	s_new = pick_c(s, tm, tm_prime, moo_gen)
	if s != s_new:
		#print("Applied pick_c rule")
		#print("Infered set: ", s_new)
		for s_eq in s_new:
			ret_value = infer(s_eq, tm, tm_prime, moo_gen) or ret_value
		return ret_value

	s_new = pick_fail(s, moo_gen)
	if s != s_new:
		#print("Applied pick_fail rule")
		#print("Infered set: ", s_new)
		return infer(s_new, tm, tm_prime, moo_gen)

	#print("No rules apply!")
	if len(s) > 0:
		return False
	else:
		return True

def gamma(moo_gen, p_label, i_label, q_label, j_label):
	"""Compute the set Gamma"""
	cpi = moo_gen(p_label, i_label)
	cqj = moo_gen(q_label, j_label)
	return set(top_f_terms(cpi)).union(set(top_f_terms(cqj)))

def top_f_terms(cipher_block_term):
	"""Return list of top-f-terms of a given cipher block term"""
	xor_list = xor_to_list(cipher_block_term)
	is_f_predicate = lambda x: isinstance(x, FuncTerm) and x.function == f
	return list(filter(is_f_predicate, xor_list))


def compute_size_f(moo_gen, i):
	"""Compute size_f of a mode of operation"""
	cipher_block = moo_gen("p", i)
	return len(top_f_terms(cipher_block))


def elim_f(sigma: Set[Equation]) -> Set[Equation]:
	"""
	Given a set of equations, remove any in the form of f(t) = 0, returning
	the new list
	"""
	elim_f_set = deepcopy(sigma)
	for eq in sigma:
		if isinstance(eq.left_side, FuncTerm):
			if eq.left_side.function == f and is_zero(eq.right_side):
				elim_f_set.remove(eq)
		elif isinstance(eq.right_side, FuncTerm):
			if eq.right_side.function == f and is_zero(eq.left_side):
				elim_f_set.remove(eq)

	return elim_f_set


def elim_c(sigma: Set[Equation]) -> Set[Equation]:
	"""
	Given a set of equations, remove those in the form of
	C_{p,i-a} xor C_{q, j-a} = 0, where i!=j
	Each equation is checked to see if it has the format of
	C(p, i, a) xor C(q, j, a) = 0
	if it matches then it will be removed, it is assumed that i!=j
	"""
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


def occurs_check(sigma: Set[Equation]) -> Set[Equation]:
	"""
	Checks each equation in a set of equations for an occurs check
	Does NOT check the entire set for an occurs check, only each equation one by one
	For the general occurs check which considers the entire set, see the commented out
	code at the bottom of this file
	"""
	occurs_set = deepcopy(sigma)
	for e in sigma:
		t1 = e.left_side
		t2 = e.right_side
		if isinstance(t2, FuncTerm) and t1 in t2 or isinstance(t1, FuncTerm) and t2 in t1:
			occurs_set.remove(e)

	return occurs_set


def pick_f(sigma: Set[Equation]) -> Set[Equation]:
	"""Implementing pick_f inference rule"""
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

def pick_c(sigma: Set[Equation], tm: FuncTerm, tmPrime: FuncTerm, moo_gen) -> Set[Equation]:

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
