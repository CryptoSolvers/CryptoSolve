#Slow syntactic unification

#!/usr/bin/env python3
from symcollab.algebra import *
from typing import Dict, Set
from . import Unification_Algorithms

# Franz Baader and Wayne Snyder. Unification Theory. Handbook of Automated Reasoning, 2001.
@Unification_Algorithms.register('')
def unif(U: Set[Equation]):

	z = 1
	U_dict = dict()
	for i, e in enumerate(U):
		U_dict[i] = e
		z += 1

	solve : Set[Equation] = set()
	while bool(U_dict):
		#Occurs Check
		for e in U_dict.values():
			if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
				if e.left_side in e.right_side:
					print('Occurs Check')
					#We could think of an improved method for errors
					return False

		#check for function clash
		for e in U_dict.values():
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
				if e.left_side.function.symbol != e.right_side.function.symbol:
					# print('Function Clash')
					#Fix the return false
					return False

		#Check for solved equations and remove
		for i, e in U_dict.items():
			if isinstance(e.left_side, Variable) and (isinstance(e.right_side, FuncTerm) or isinstance(e.right_side, Constant) or isinstance(e.right_side, Variable)):
				del U_dict[i]
				sigma = SubstituteTerm()
				sigma.add(e.left_side, e.right_side)
				for j in U_dict.keys():
					if (isinstance(U_dict[j].left_side, FuncTerm) or isinstance(U_dict[j].left_side, Variable)):
						U_dict[j].left_side = U_dict[j].left_side * sigma
					if (isinstance(U_dict[j].right_side, FuncTerm) or isinstance(U_dict[j].right_side, Variable)):
						U_dict[j].right_side = U_dict[j].right_side * sigma
				solve = solve.union({e})
				break

		#Orient
		for i, e in U_dict.items():
			if (isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm)):
				temp = e.right_side
				e.right_side = e.left_side
				e.left_side = temp

		#Decompose
		for i in list(U_dict.keys()):
			e = U_dict[i]
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
				if e.left_side.function.symbol == e.right_side.function.symbol:
					dec = map(lambda t1, t2: Equation(t1, t2), list(e.left_side.arguments), list(e.right_side.arguments))
					del U_dict[i]
					for d in dec:
						U_dict[z] = d
						z += 1

	delta = SubstituteTerm()
	for e in solve:
		delta.add(e.left_side, e.right_side)

	return delta

