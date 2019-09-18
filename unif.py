#!/usr/bin/env python3
from algebra import *

def get_var(l):
	V = set()
	if not l:
		return {}
	
	for t in l:
		if isinstance(t, Variable):
			V=V.union({t})
			l.remove(t)
		if isinstance(t, Constant):
			l.remove(t)	
	
	L = []
	for t in l:
		if isinstance(t, FuncTerm):
			for x in t.arguments:
				L = L + [x]

	return V.union(get_var(L))			
	

def unif(l: Term, r: Term):
	z = 1
	U = dict([(z, Equation(l, r))])
	solve = set()
	while bool(U):
		
		#Occurs Check
		for i, e in U.items():
			if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
				V = get_var(list(e.right_side.arguments))
				if e.left_side in V:
					print('Occurs Check')
					return set()
		
		#check for function clash
		for i, e in U.items():
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
				if e.left_side.function.symbol != e.right_side.function.symbol:
					print('Function Clash')
					return {}
								
		#Check for solved equations and remove
		#Need to add variable replacement by using Brandon's new method
		for i in list(U):
			if isinstance(U[i].left_side, Variable):
				solve = solve.union({U[i]})
				del U[i]
						
		
		#Orient
		for i, e in U.items():
			if isinstance(e.right_side, Variable):
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
						
		
								
	return solve
										
