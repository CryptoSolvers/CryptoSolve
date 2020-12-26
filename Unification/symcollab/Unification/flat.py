#creates flat terms from terms.
#needed for some unification algorithms such as E_AC


#!/usr/bin/env python3
from symcollab.algebra import *

def flat(U: set):
	#break equations into two
	z=0
	
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
	
	#Flatten the terms
	#Need to update to include deeper than two levels in the term
	for e in list(U):
		mod = False
		if isinstance(e.right_side, FuncTerm):
			root = e.right_side.function
			var_list = list()
			for arg in list(e.right_side.arguments):
				if isinstance(arg, FuncTerm):
					vtemp = Variable('v_'+str(z+1))
					U.add(Equation(vtemp, arg))
					var_list.append(vtemp)
					z=z+1
				else:
					var_list.append(arg)
			U.add(Equation(e.left_side, FuncTerm(Function(str(root.symbol), root.arity), var_list)))
			U.remove(e)

	return U
