#Elementary ACU-unification for single term pair

####################################################
#To-Do:
#-- Fix the conversion from the diophantine solver
#-- Add free function symbols
#-- Allow more than one AC symbol
#-- Test the solver and AC solutions

#!/usr/bin/env python3
from copy import deepcopy
from symcollab.algebra import *
import numpy as np # type: ignore
from sympy.solvers.diophantine import diophantine # type: ignore
from sympy import symbols # type: ignore
from sympy.solvers.diophantine import diop_linear # type: ignore
from sympy.parsing.sympy_parser import parse_expr # type: ignore
from collections import Counter


#convert a set of term equations into a single
#linear homogeneous diophantine equation
def convert_eq(U: set, func: str):
	var_count=dict()
	first=True
	for e in U:
		LS=get_vars(e.left_side)
		RS=get_vars(e.right_side)
		for x in list(LS):
			num = LS.count(x) - RS.count(x)
			if x in var_count:
				if first:
					var_count[x] = var_count[x] + num
				else:
					var_count[x] = var_count[x] - num
			else:
				if first:
					var_count[x] = num
				else: 
					var_count[x] = -num
			LS[:] = [y for y in LS if y != x]
			RS[:] = [y for y in RS if y != x]
		if len(RS) != 0:
			for x in RS:
				var_count[x] = -RS.count(x)
				RS[:] = [y for y in RS if y != x]
		first=False
	#convert to an equation
	i=0
	e = ""
	variables = list()
	row = list()
	for x in var_count:
		temp = str(x)
		i += 1
		e = e + str(var_count[x]) +"*"+ temp + (" + " if i < len(var_count) else "")
		temp = symbols(temp, integer=True)
		variables.append(temp)
		row.append(var_count[x])
	e = parse_expr(e)
	
	sol = diop_linear(e)
	
	F = deepcopy(func)
	j = 0 
	delta = SubstituteTerm()
	print(variables)
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
def ac_unify(U: set):
	
	#Check if they are the same term
	for e in list(U):
		if e.right_side == e.left_side:
			U.remove(e)
	if U == set():
		return set()
	
	#Occurs Check
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side in e.right_side:
				print('Occurs Check')
				return False
		if isinstance(e.right_side, Variable) and isinstance(e.left_side, FuncTerm):
			if e.right_side in e.left_side:
				print('Occurs Check')
				return False
				
	#Function Clash
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			if e.left_side.function.symbol != e.right_side.function.symbol:
				print('Function Clash')
				return False
					
	#Create the variable lists and send it to matrix solve
	delta = SubstituteTerm()
	delta=convert_eq(U, e.right_side.function.symbol)
	print(delta)
