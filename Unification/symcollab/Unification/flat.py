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

def flat(U: Set[Equation], varcount: int):

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
		if isinstance(e.left_side, Variable):
			new_equations.add(e)
			continue

		v = fresh_variable()
		new_equations.add(Equation(v, e.left_side))
		new_equations.add(Equation(v, e.right_side))


	U = new_equations

	temp = OrderedSet()
	while U != temp:
		temp = U
		new_equations = OrderedSet()
		for e in U:
			lhs = e.left_side
			rhs = e.right_side
			if isinstance(rhs, FuncTerm):
				# Flatten each argument
				new_argument_list = []
				for arg_term in rhs.arguments:
					if isinstance(arg_term, FuncTerm):
						vtemp = fresh_variable()
						# Add a new equation mapping the fresh
						# variable to the arugment
						new_equations.add(
							Equation(vtemp, arg_term)
						)
						# Set the argument of this function
						# to be the new variable
						new_argument_list.append(vtemp)
					else:
						# No work needs to be done
						new_argument_list.append(arg_term)
				# Create new equation from flattened arguments
				new_equations.add(Equation(
					lhs,
					rhs.function(*new_argument_list)
				))
			else:
				new_equations.add(e)

		U = new_equations

	return (U, varcount)
