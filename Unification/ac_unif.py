#Elementary AC-unification

#!/usr/bin/env python3
from algebra import *
import numpy as np
from scipy import linalg
from sympy.solvers.diophantine import diophantine
from sympy import symbols
from sympy.solvers.diophantine import diop_solve
from sympy.parsing.sympy_parser import parse_expr



#Constuct the system of linear
#diophantine equations and use the 
#SymPy lib
def matrix_solve(vll: list, vlr: list):
	var_count = dict()
	l = vll + vlr
	
	#get the count for the vars
	for v in l:
		 if v not in var_count:
			 var_count[v] = num_vars(vll, v) - num_vars(vlr, v) 
	print(var_count)
	#use the count to create the linear diophantine equation
	#first the variables
	i=0
	e=""
	vars = list()
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

def num_vars(l: list, v: Variable):
	x = 0
	for i in l:
		if i == v:
			x += 1
	
	return x			




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
	vll = find_vars(l)
	vlr = find_vars(r)
	matrix_solve(vll, vlr)
	

		
def find_vars(t: term):
	if isinstance(t, Variable): 
		return [t]
	
	l=[]
	if isinstance(t, FuncTerm):
		for i in t.arguments:
			l = l + find_vars(i)
	
	return l
			
		
		
	
		
	

		
								
				
				
