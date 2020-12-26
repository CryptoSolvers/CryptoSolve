#!/usr/bin/env python3
from symcollab.algebra import *
from typing import List


def decomposable(term : Term) -> bool:
	return isinstance(term, FuncTerm) and term.function.arity > 0

# Franz Baader and Wayne Snyder. Unification Theory. Handbook of Automated Reasoning, 2001.
def syntactic_unif(l: Term, r: Term) -> Union[bool, SubstituteTerm]:
	U = [Equation(l, r)]
	solve : List[Equation] = []
	while bool(U):
		equations_to_remove : List[int] = []
		apply_sigma = False
		sigma = SubstituteTerm()
		decomposed_equations : List[Equation] = []
		for i, e in enumerate(U):
			#Trival
			if e.left_side == e.right_side:
				equations_to_remove.append(i)
				continue # Don't need to perform other checks...
				
			#Symbol Clash
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
				if e.left_side.function.symbol != e.right_side.function.symbol:
					print('Symbol Clash')
					return False #Fix the return false
			
			#Orient
			if (isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm)):
				temp = U[i].right_side
				U[i].right_side = U[i].left_side
				U[i].left_side = temp
			
			#Occurs Check
			if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
				if e.left_side in e.right_side:
					print('Occurs Check')
					return False #We could think of an improved method for errors
			
			#Decomposition
			if decomposable(e.left_side) and decomposable(e.right_side):
				dec = map(lambda t1, t2: Equation(t1, t2), list(e.left_side.arguments), list(e.right_side.arguments))
				equations_to_remove.append(i)
				decomposed_equations += dec
				continue # Variable Elimination can't happen if equation was decomposable
				
			#Variable Elimination (passed occurs check at this point)
			if isinstance(e.left_side, Variable):
				equations_to_remove.append(i)
				sigma.add(e.left_side, e.right_side)
				apply_sigma = True
				break # Break out of loop so that substitutions can be applied to U
		#End For

		# Remove solved or decomposed equations
		# Reverse so that we don't have to pay attention to the order we delete
		for i in sorted(equations_to_remove, reverse = True):
			del U[i]
		
		# Add new decomposed equations to U
		U += decomposed_equations

		# Apply substitutions
		if apply_sigma:
			# Apply substitutions to U
			for i, e in enumerate(U):
				U[i].left_side *= sigma
				U[i].right_side *= sigma
			# Apply substitutions to solve set
			for i, e in enumerate(solve):
				solve[i].left_side *= sigma
				solve[i].right_side *= sigma
			# Add equation from substitution to solve
			solve += [Equation(*(sigma.subs.pop()))]

	
	delta = SubstituteTerm()	
	for e in set(solve):
		delta.add(e.left_side, e.right_side)
	print(delta)								
	return delta
										
