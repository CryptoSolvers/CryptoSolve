#!/usr/bin/env python3
"""
creates flat terms from terms.
needed for some unification algorithms such as E_AC
"""
from typing import Set

from symcollab.algebra import (
	FuncTerm, Variable, Equation, Function, depth
)



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
	new_equations = set()
	for e in U:
		lhs = e.left_side; rhs = e.right_side
		if isinstance(lhs, FuncTerm):
			# If the rhs is a variable, then flip
			# the equation
			if isinstance(rhs, Variable):
				new_equations.add(Equation(rhs, lhs))
			else:
				# Otherwise create a new variable and split
				# the equation
				v = fresh_variable()
				add1 = Equation(v, e.left_side)
				add2 = Equation(v, e.right_side)
				new_equations.add(add1)
				new_equations.add(add2)
		else:
			# Otherwise the lhs is already a variable
			new_equations.add(e)
	U = new_equations

	# print("U after breaking two sided functions: ")
	# print(U)
	#Flatten the terms
	temp = set()
	while U != temp:
		# print("U : at start of loop: " + str(lp))
		# print(U)
		# print("Varcount: ")
		# print(z)
		temp = U
		# print("Temp at loop: " + str(lp))
		# print(temp)
		new_equations = set()
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
		# print("U : at end of loop: " + str(lp))
		# print(U)
		# print("Temp at end of loop: " + str(lp))
		# print(temp)

	# print("U after removing subterms: ")
	# print(U)
	# print("Final Varcount: ")
	# print(z)
	return (U, varcount)

"""
Below is an experiment with a version that doesn't enforce
variable = flat term
"""

# def flat(U: Set[Equation], varcount: int):
# 	def fresh_variable():
# 		nonlocal varcount
# 		var_name = 'vv_'+str(varcount)
# 		varcount += 1
# 		return Variable(var_name)

# 	beyond_depth_limit = any((
# 		depth(eq.left_side) > 1 or depth(eq.right_side) > 1 \
# 		for eq in U
# 	))
# 	while beyond_depth_limit:

# 		new_equations = set()
# 		for e in U:
# 			lhs = e.left_side
# 			rhs = e.right_side

# 			new_lhs = lhs
# 			if isinstance(lhs, FuncTerm):
# 				# Flatten each argument
# 				new_argument_list = []
# 				for arg_term in lhs.arguments:
# 					if isinstance(arg_term, FuncTerm):
# 						v = fresh_variable()
# 						# Add a new equation mapping the fresh
# 						# variable to the arugment
# 						new_equations.add(
# 							Equation(v, arg_term)
# 						)
# 						# Set the argument of this function
# 						# to be the new variable
# 						new_argument_list.append(v)
# 					else:
# 						# No work needs to be done
# 						new_argument_list.append(arg_term)
# 				new_lhs = lhs.function(*new_argument_list)

# 			new_rhs = rhs
# 			if isinstance(rhs, FuncTerm):
# 				# Flatten each argument
# 				new_argument_list = []
# 				for arg_term in rhs.arguments:
# 					if isinstance(arg_term, FuncTerm):
# 						vtemp = fresh_variable()
# 						# Add a new equation mapping the fresh
# 						# variable to the arugment
# 						new_equations.add(
# 							Equation(vtemp, arg_term)
# 						)
# 						# Set the argument of this function
# 						# to be the new variable
# 						new_argument_list.append(vtemp)
# 					else:
# 						# No work needs to be done
# 						new_argument_list.append(arg_term)
# 				new_rhs = rhs.function(*new_argument_list)

# 			# Create new equation from flattened arguments
# 			new_equations.add(Equation(
# 				new_lhs,
# 				new_rhs
# 			))

# 		U = new_equations
# 		beyond_depth_limit = any((
# 			depth(eq.left_side) > 2 or depth(eq.right_side) > 2 \
# 			for eq in U
# 		))
# 		# print("U : at end of loop: " + str(lp))
# 		# print(U)
# 		# print("Temp at end of loop: " + str(lp))
# 		# print(temp)

# 	# print("U after removing subterms: ")
# 	# print(U)
# 	# print("Final Varcount: ")
# 	# print(z)
# 	return (U, varcount)