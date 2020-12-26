#!/usr/bin/env python3
from symcollab.algebra import Variable, SubstituteTerm, FuncTerm
from symcollab.Unification.ac_unif import ac_unify
from symcollab.Unification.eac_unif import R1
from symcollab.Unification.flat import flat

#H_AC(R_1) unification 
#Using the new hierarrchical method

#############################################
#Theory:                                    #
#(same as E_AC)                             #
# exp(exp(x, y), z) = exp(x, f(y, z))       #
# exp(g(x, y), z) = g(exp(x, z), exp(y, z)) #
# f is AC                                   #
# \Sigma_0 = {f}                            #
# \Sigma_1 = {exp, g}                       #
#############################################


def h_eac(U: set):
	#H_E rules
	P = list()
	P.append(U)
	for i in range(len(P)):
		P[i] = coalesce(P[i])
		P[i] = split_flatten(P[i])
		ptemp = list()
		ptemp = R1(P[i])
		P.extend(ptemp)
		ptemp = list()
		ptemp = solve(P[i])
		P.extend(ptemp)
	print(P)
		
	
def coalesce(U2: set):
	#Rule (a)
	Uremove = set()
	for e in list(U2):
		if isinstance(e.right_side, Variable) and isinstance(e.left_side, Variable) and e not in Uremove:
			sigma = SubstituteTerm()
			sigma.add(e.left_side, e.right_side)
			for e2 in list(U2):
				if e2 != e:
					if (isinstance(e2.left_side, FuncTerm) or isinstance(e2.left_side, Variable)):
						e2.left_side = e2.left_side * sigma
					if (isinstance(e2.right_side, FuncTerm) or isinstance(e2.right_side, Variable)):
						e2.right_side = e2.right_side * sigma
			#U2.remove(e)
			Uremove.add(e)
	return U2
	
def split_flatten(U2: set):
	U2 = flat(U2)
	return(U2)


def solve(U2: set):
	#collect the \Sigma_0 terms
	f_terms = set()
	for e in U2:
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "f":
			f_terms.add(e)
	delta = SubstituteTerm()
	#call ac-unif
	delta=ac_unify(f_terms)
	return(delta)
	
