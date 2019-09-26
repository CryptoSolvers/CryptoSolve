#Slow syntactic unification

#!/usr/bin/env python3
from algebra import *
	

def unif(l: Term, r: Term):
	z = 1
	U = dict([(z, Equation(l, r))])
	solve = set()
	while bool(U):
		print('hello')
		#Occurs Check
		for i, e in U.items():
			if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
				if e.left_side in e.right_side:
					print('Occurs Check')
					return set()
		
		#check for function clash
		for i, e in U.items():
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
				if e.left_side.function.symbol != e.right_side.function.symbol:
					print('Function Clash')
					return {}
								
		#Check for solved equations and remove
		for i in list(U):
			if isinstance(U[i].left_side, Variable) and (isinstance(U[i].right_side, FuncTerm) or isinstance(U[i].right_side, Constant) or isinstance(U[i].right_side, Variable)):
				e = U[i]
				print(e)
				del U[i]
				sigma = SubstituteTerm()
				sigma.add(e.left_side, e.right_side) 
				for j in list(U):
					if (isinstance(U[j].left_side, FuncTerm) or isinstance(U[j].left_side, Variable)):
						U[j].left_side = U[j].left_side * sigma
					if (isinstance(U[j].right_side, FuncTerm) or isinstance(U[j].right_side, Variable)):
						U[j].right_side = U[j].right_side * sigma
				solve = solve.union({e})
				break
							
		#Orient
		for i, e in U.items():
			if (isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm)):
				temp = e.right_side
				e.right_side = e.left_side
				e.left_side = temp
				
		#Decompose
		for i in list(U):
			if isinstance(U[i].left_side, FuncTerm) and isinstance(U[i].right_side, FuncTerm):
				if U[i].left_side.function.symbol == U[i].right_side.function.symbol:
					dec = map(lambda t1, t2: Equation(t1, t2), list(U[i].left_side.arguments), list(U[i].right_side.arguments))
					del U[i]
					for i in dec:
						U[z] = i
						z += 1
						
	delta = SubstituteTerm()	
	for e in solve:
		delta.add(e.left_side, e.right_side)
	print(delta)								
	return solve
										
