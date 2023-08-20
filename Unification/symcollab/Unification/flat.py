#creates flat terms from terms.
#needed for some unification algorithms such as E_AC


#!/usr/bin/env python3
from typing import Set
from symcollab.algebra import (
	FuncTerm, Variable, Equation, Function
)
from copy import deepcopy
# from symcollab.algebra import *

#python == doesn't seem to work with sets of equations, so this:

def equ_test(S1: set, S2: set):
	equal = True
	for x in S1:
		if x not in S2:
			equal = False
	print("Results of equality test")
	print(equal)
	return equal

def flat(U: Set[Equation], varcount: int):
	#break equations into two
	print("In Flat\n")
	print("varcount is: ")
	print(varcount)
	print("U is: ")
	print(U)
	z=varcount
	
	for e in list(U):
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#create a new var for lhs of two new equations.
			var = str()
			var = 'v_'+str(z)
			z = z + 1
			var = Variable(var)
			add1 = Equation(var, e.left_side)
			add2 = Equation(var, e.right_side)
			U.remove(e)
			U.add(add1)
			U.add(add2)
	
	print("U after breaking two sided functions: ")
	print(U)
	#Flatten the terms
	#Need to update to include deeper than two levels in the term
	lp = 1
	temp = set()
	while not equ_test(U, temp):
		print("U : at start of loop: " + str(lp))
		print(U)
		print("Varcount: ")
		print(z)
		temp = set()
		temp = deepcopy(U)
		print("Temp at loop: " + str(lp))
		print(temp)
		for e in list(U):
			mod = False
			if isinstance(e.right_side, FuncTerm):
				root = e.right_side.function
				var_list = list()
				arity = len(e.right_side.arguments)
				for arg_index in range(0, arity):
					if isinstance(e.right_side.arguments[arg_index], FuncTerm):
						vtemp = Variable('v_'+str(z+1))
						U.add(Equation(vtemp, e.right_side.arguments[arg_index]))
						tempterm = list(e.right_side.arguments)
						tempterm[arg_index] = vtemp
						e.right_side.arguments = tuple(tempterm)
						z = z + 1
		print("U : at end of loop: " + str(lp))
		print(U)
		print("Temp at end of loop: " + str(lp))
		print(temp)
		lp = lp + 1
		if lp > 5:
			break				
	print("U after removing subterms: ")
	print(U)
	print("Final Varcount: ")
	print(z)
	return (U, z+1) 
