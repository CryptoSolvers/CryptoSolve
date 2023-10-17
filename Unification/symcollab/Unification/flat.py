#!/usr/bin/env python3
"""
creates flat terms from terms.
needed for some unification algorithms such as E_AC
"""
from typing import Set, Dict

from symcollab.algebra import (
	FuncTerm, Variable, Equation, Function, depth, Term
)

# OrderedSet makes it so that the outputs are deterministic
# this is at a great expense of execution speed.
# Leave in when testing, remove when done.
from symcollab.Unification.orderedset import OrderedSet
OrderedSet = set

# NOTE: In syntactic AC, the algorithm expects older_var = newer_var
def flat(U: Set[Equation], varcount: int):

	#break equations into two
	# print("In Flat\n")
	# print("varcount is: ")
	# print(varcount)
	# print("U is: ")
	# print(U)
	def fresh_variable():
		nonlocal varcount
		var_name = 'v_'+str(varcount)
		varcount += 1
		return Variable(var_name)

	# Step 1: Create a new variable for the left hand side
	# of any given equation
	# new_equations = set()
	new_equations = OrderedSet()

	for e in U:
		# Skip if variable on right side
		if isinstance(e.right_side, Variable):
			new_equations.add(e)
			continue

		v = fresh_variable()
		new_equations.add(Equation(e.left_side, v))
		new_equations.add(Equation(e.right_side, v))


	U = new_equations

	# print("U after breaking two sided functions: ")
	# print(U)
	#Flatten the terms
	# temp = set()
	temp = OrderedSet()
	while U != temp:
		temp = U
		new_equations = OrderedSet()
		for e in U:
			lhs = e.left_side
			rhs = e.right_side
			if isinstance(lhs, FuncTerm):
				# Flatten each argument
				new_argument_list = []
				for arg_term in lhs.arguments:
					if isinstance(arg_term, FuncTerm):
						vtemp = fresh_variable()
						# Add a new equation mapping the fresh
						# variable to the arugment
						new_equations.add(
							Equation(arg_term, vtemp)
						)
						# Set the argument of this function
						# to be the new variable
						new_argument_list.append(vtemp)
					else:
						# No work needs to be done
						new_argument_list.append(arg_term)
				# Create new equation from flattened arguments
				new_equations.add(Equation(
					lhs.function(*new_argument_list),
					rhs
				))
			else:
				new_equations.add(e)

		U = new_equations
		# print("U : at end of loop: " + str(lp))
		# print(U)
		# print("Temp at end of loop: " + str(lp))
		# print(temp)

	# print("U after removing subterms: ")
	# print(U)
	# print("Final Varcount: ")
	# print(z)
	return (U, varcount)
