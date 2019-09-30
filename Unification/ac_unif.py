#Elementary AC-unification

#!/usr/bin/env python3
from algebra import *
import numpy as np
from scipy import linalg
from sympy.solvers.diophantine import diophantine
from sympy import symbols
from sympy.solvers.diophantine import diop_solve
from sympy.parsing.sympy_parser import parse_expr
from collections import Counter


#Constuct the system of linear
#diophantine equations and use the 
#SymPy lib
def matrix_solve(vll: list, vlr: list):
	#get the count for the vars
	var_count = Counter(vll)
	var_count.subtract(Counter(vlr))
	print(var_count)
	#use the count to create the linear diophantine equation
	#first the variables
	i=0
	e=""
	variables = list()
	for x in var_count.values():
		temp = "x_" + str(i)
		i += 1
		e = e + str(x) +"*"+ temp + (" + " if i < len(var_count) else "")
		temp = symbols(temp, integer=True)
	#print(e)
	e = parse_expr(e)
	#print(e)
	
	#solve the equation
	sol = diop_solve(e)
	print(sol) 		

	#convert back to a substitution
	

	return var_count


#Assumes currently that we have a single AC-symbol
#need to update to allow other function symbols and cons 
def ac_unify(l: Term, r: Term):
	
	#Check if they are the same term
	if l == r:
		return set()
	
	#Occurs Check
	if isinstance(l, Variable) and isinstance(r, FuncTerm):
		if l in r:
			print('Occurs Check')
			return set()
				
	#Function Clash
		if isinstance(l, FuncTerm) and isinstance(r, FuncTerm):
			if l.function.symbol != r.function.symbol:
				print('Function Clash')
				return {}
					
	#Create the variable lists and send it to matrix solve
	vll = get_vars(l)
	vlr = get_vars(r)
	matrix_solve(vll, vlr)
