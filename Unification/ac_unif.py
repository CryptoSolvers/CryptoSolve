#Elementary ACU-unification for single term pair

#!/usr/bin/env python3
from algebra import *
import numpy as np # type: ignore
from sympy.solvers.diophantine import diophantine # type: ignore
from sympy import symbols # type: ignore
from sympy.solvers.diophantine import diop_linear # type: ignore
from sympy.parsing.sympy_parser import parse_expr # type: ignore
from collections import Counter


#Constuct the system of linear
#diophantine equations and use the 
#SymPy lib
def matrix_solve(vll: list, vlr: list, func: str):
	#get the count for the vars
	var_countl = Counter(vll)
	var_countr= Counter(vlr)

	
	vars_total = list(set(vll)) + list((set(vlr) - set(vll)))
	var_count = dict()
	for j in vars_total:
		var_count[j] = var_countl[j] - var_countr[j]

	#use the count to create the linear diophantine equation
	#first the variables
	i=0
	e=""
	variables = list()
	row = list()
	for x in var_count:
		#temp = "x_" + str(i)
		temp = str(x)
		i += 1
		e = e + str(var_count[x]) +"*"+ temp + (" + " if i < len(var_count) else "")
		temp = symbols(temp, integer=True)
		variables.append(temp)
		row.append(var_count[x])

	e = parse_expr(e)
	#solve the equation
	sol = diop_linear(e)


	#matrix form
	#need a new Diophantine solver to 
	#solve more than a single equation		

	#convert back to a substitution
	F = deepcopy(func)
	j = 0 
	delta = SubstituteTerm()
	for x in range(0, len(variables)):
		
		if row[x] == 0:
			temp = Variable(str(variables[x]))
			delta.add(temp, temp)
		else:
			var_list = list()
			num = '0'
			if '*' in str(sol[j]):
				num, var = str(sol[j]).split("*", 1)
			else:
				var = str(sol[j])
			var = Variable(var)	 	
			
			num = int(num)
			func = Function(func, 2)
			ran = str()
			if num > 0:
				for y in range(0, num):
					if y == 0:
						ran = ran
					if y >= 1 and y <= num-2:	
						ran = ran + F + '(' + str(var) + ','
					if y == num-1:
						ran = ran + str(var) 
					if y == num:
						num = num		
				for y in range(2, num):
					ran = ran + ')'	
			else:
				ran = var				
			y = Variable(str(sol[j]))
			if num > 0:
				T = FuncTerm(Function(str(func.symbol), 2), [str(var),ran])
			else:
				T = var	
			z= Variable(str(variables[x]))
			delta.add(z, T)
			j+= 1
	
	return delta


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
	delta = SubstituteTerm()
	delta=matrix_solve(vll, vlr, l.function.symbol)
	print(delta)
