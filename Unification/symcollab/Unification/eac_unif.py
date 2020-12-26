#E_AC unification 
#cite the E_AC paper

#############################################
#Theory:                                    #
#                                           #
# exp(exp(x, y), z) = exp(x, f(y, z))       #
# exp(g(x, y), z) = g(exp(x, z), exp(y, z)) #
# f is AC                                   #
#############################################

#!/usr/bin/env python3
from copy import deepcopy
from symcollab.algebra import *
from symcollab.Unification.ac_unif import ac_unify
from symcollab.Unification.flat import flat
#from itertools import combinations


def eac_unif(U: set):
	
	unif_problems = dict()
	U2 = set()
	#First call flat
	U2 = flat(U)
	
	#Get the set of variables from the equations
	var_set = set()
	for e in U2:
		var_set = var_set.union(get_vars(e.left_side))
		var_set = var_set.union(get_vars(e.right_side))
	
	#Collect the variables for the set V
	V = list()
	for e in U2:
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			V.append(e.right_side.arguments[1])
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "f":
			V.append(e.right_side.arguments[0])
			V.append(e.right_side.arguments[1])
	#Generate the codewords of the partitions
	VL = list(V)
	P = list()
	P = setpartitions(set(V))
	
	#For each codeword, create the set of new equalities and
	#send the set of equations to the unification algorithm rules
	for code in P:
		UE = set()
		for  p in range(len(code)):
			UE.add(Equation(VL[p], VL[code[p]-1]))
		#Add the new equalities
		U2.update(UE)
		#Call the unification rules or R1
		U3 = U4 = list()
		U3 = R1(U2)
		#now for each solution in U3 call AC-unification
		for sol in U3:
			#first get just the f-terms
			f_terms = set()
			if len(sol) != 0:
				for e in sol:
					if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "f":
						f_terms.add(e)
				delta = SubstituteTerm()
				#call ac-unif
				delta=ac_unify(f_terms)
				U4.append([sol, delta])
	print("EAC Unification is complete")
	return U4
	
def R1(U2: set):
	
	var_count = [0]
	UP=list()
	UP.append(U2)
	Utemp = list()
	Bound = 3
	x = 0
	#bound until graph termination method is added
	while Utemp != UP and  x < Bound:
		Utemp = UP
		UP = rule_c1(UP, var_count)
		UP = rule_c2(UP, var_count)
		UP = rule_c3(UP, var_count)
		UP = rule_c4(UP, var_count)
		x = x + 1
	return(UP)


def rule_c1(UP: list, var_count):
	#rule c1, i*a*
	
	#fail test
	for U2 in UP:
		if fail_rules(U2):
			print("Fail found")
			U2 = U2.clear()
	
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_i(UP[i], var_count)
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_a(UP[i])
	return(UP)
	
	
def rule_c2(UP: list, var_count):
	#Old: rule c2, [b + c + d]a*
	#New: rule c2, [bcd]a*
	#fail test
	for U2 in UP:
		if fail_rules(U2):
			U2 = U2.clear()
	
	for i in range(len(UP)):
		UP[i]=rule_b_c(UP[i])
	for i in range(len(UP)):
		UP[i] = rule_d(UP[i])
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_a(UP[i])
	
	return(UP)
	
def rule_c3(UP: list, var_count):
	#Old: rule c3, [b + c + d]*a*i*e[b + c + d]*a*
	#New: rule c3, [bcd]*a*i*e[bcd]*a*
	#fail test
	for U2 in UP:
		if fail_rules(U2):
			U2 = U2.clear()
	
	for i in range(len(UP)):
		UP[i] = rule_b_c(UP[i])
		
	for i in range(len(UP)):
		UP[i] = rule_d(UP[i])
	
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_a(UP[i])
	
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_i(UP[i], var_count)
	
	for i in range(len(UP)):
		UP[i] = rule_e(UP[i], var_count)
	
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_b_c(UP[i])
			UP[i] = rule_d(UP[i])
	
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_a(UP[i])
	return(UP)
	
def rule_c4(UP: list, var_count):
	#Old: rule c4, (i*[b + c + d]*a*)*(f + g + h)a*
	#New: rule c4, (i*[bcd]*a*)*(f + g + h)a*
	#fail test
	for U2 in UP:
		if fail_rules(U2):
			U2 = U2.clear()
	
	
	for i in range(len(UP)):
		Utemp2 = set()
		while Utemp2 != UP[i]:
			Utemp2 = UP[i]
			Utemp = set()
			while Utemp != UP[i]:
				Utemp = UP[i]
				UP[i] = rule_i(UP[i], var_count)
			Utemp = set()
			while Utemp != UP[i]:
				Utemp = UP[i]
				UP[i] = rule_b_c(UP[i])
				UP[i] = rule_d(UP[i])
			Utemp = set()
			while Utemp != UP[i]:
				Utemp = UP[i]
				UP[i] = rule_a(UP[i])
	for i in range(len(UP)):
		Utempa = Utempb = set()
		UP[i] = rule_f(UP[i], var_count)
		Utempa = rule_g(UP[i])
		Utempb = rule_h(UP[i], var_count)
		UP.append(Utempa)
		UP.append(Utempb)
		
	for i in range(len(UP)):
		Utemp = set()
		while Utemp != UP[i]:
			Utemp = UP[i]
			UP[i] = rule_a(UP[i])
	
	return(UP)
	
def rule_a(U2: set):
	#Rule (a)
	Uremove = set()
	for e in list(U2):
		if isinstance(e.right_side, Variable) and isinstance(e.left_side, Variable) and e not in Uremove:
			sigma = SubstituteTerm()
			sigma.add(e.left_side, e.right_side)
			for e2 in list(U2):
				if e2 != e:
					if (isinstance(e2.left_side, FuncTerm) or isinstance(e2.left_side, Variable)):
						e2.left_side = e2.left_side * sigma
					if (isinstance(e2.right_side, FuncTerm) or isinstance(e2.right_side, Variable)):
						e2.right_side = e2.right_side * sigma
			#U2.remove(e)
			Uremove.add(e)
	return U2
					
def rule_b_c(U2: set):
	#Rule (b) and (c)
	#exp terms with the same base or the same exp
	Uremove = set()
	Utemp = U2
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			Utemp = Utemp - {e}
			for e2 in list(Utemp):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "exp" and e2 not in Uremove:
						if e.right_side.arguments[0] == e2.right_side.arguments[0]:
							# rule (b)
							e3 = Equation(e.right_side.arguments[1], e2.right_side.arguments[1])
							U2.add(e3)
							U2 = U2 - {e2}
							Uremove.add(e2)
					else:
						if e.right_side.arguments[1] == e2.right_side.arguments[1]:
							# rule (c)
							e3 = Equation(e.right_side.arguments[0], e2.right_side.arguments[0])
							U2.add(e3)
							U2 = U2 - {e2}
							Uremove.add(e2)
	U2=U2.difference(Uremove)
	return U2
	
	
def rule_d(U2: set):
	#Rule (d)
	#two g-terms
	Uremove=set()
	Utemp=set()
	Utemp = U2
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "g":
			Utemp = Utemp - {e}
			for e2 in list(Utemp):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "g" and e2 not in Uremove:
						e4 = Equation(e.right_side.arguments[1], e2.right_side.arguments[1])
						e5 = Equation(e.right_side.arguments[0], e2.right_side.arguments[0])
						U2.add(e4)
						U2.add(e5)
						Uremove.add(e2)
						
	U2=U2.difference(Uremove) 
	return U2
	
	
	
def rule_e(U2: set, var_count):
	#Rule (e) 
	# exp and a g term
	Uremove=set()
	Utemp=set()
	Utemp = U2
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			for e2 in list(U2):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "g" and e2 not in Uremove:
						#create three new equations
						var1 = str()
						var1 = 'v_'+str(var_count[0])
						var_count[0] = var_count[0] + 1
						var2 = str()
						var2 = 'v_'+str(var_count[0])
						var_count[0] = var_count[0] + 1
						var1 = Variable(var1)
						var2 = Variable(var2)
						t1 = FuncTerm(e2.right_side.function, [var1, var1])
						t2 = FuncTerm(e.right_side.function, [var1, e.right_side.arguments[1]])
						t3 = FuncTerm(e.right_side.function, [var2, e.right_side.arguments[1]])
						add1 = Equation(e.right_side.arguments[0], t1)
						add2 = Equation(e2.right_side.arguments[0], t2)
						add3 = Equation(e2.right_side.arguments[1], t3)
						U2.add(add1)
						U2.add(add2)
						U2.add(add3)
						Uremove.add(e2)
						U2.remove(e2)
	return U2
	
def rule_i(U2: set, var_count):
	#Rule (i), fourth of 4 exp = exp rules
	Uremove=set()
	U3=Utemp=set()
	Utemp=U3=U2
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			U3 = U3 - {e}
			for e2 in list(U3):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side != e.left_side and str(e2.right_side.function) == "exp" and e2 not in Uremove:
						#create three new equations
						F = Function("f", 2)
						var1 = str()
						var1 = 'v_'+str(var_count[0]) 
						var_count[0] = var_count[0] + 1
						var1 = Variable(var1) #Z
						t1 = FuncTerm(e.right_side.function, [e2.right_side.arguments[0], var1])
						t2 = FuncTerm(F, [e2.right_side.arguments[1], e.right_side.arguments[1]])
						add1 = e2
						add2 = Equation(e.left_side, t1)
						add3 = Equation(var1, t2)
						Utemp.add(add1)
						Utemp.add(add2)
						Utemp.add(add3)
						Uremove.add(e2)
						Uremove.add(e)
						#U2.remove(e2)
						U2.remove(e)
	U2 = U2.union(Utemp)
	return U2
	
def rule_f(U2: set, var_count):
	#Rule (f), first of 4 exp = exp rules
	Uremove=set()
	U3=Utemp=set()
	Utemp=U3=U2
	print(U2)
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			U3 = U3 - {e}
			for e2 in list(U3):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "exp" and e2 not in Uremove:
						#create three new equations
						F = Function("f", 2)
						var1 = str()
						var1 = 'v_'+str(var_count[0]) 
						var_count[0] = var_count[0] + 1
						var1 = Variable(var1) #Z
						t1 = FuncTerm(F, [var1, e.right_side.arguments[1]])
						t2 = FuncTerm(e.right_side.function, [e2.right_side.arguments[0], var1])
						add1 = e2
						add2 = Equation(e2.right_side.arguments[1], t1)
						add3 = Equation(e.right_side.arguments[0], t2)
						Utemp.add(add1)
						Utemp.add(add2)
						Utemp.add(add3)
						Uremove.add(e2)
						Uremove.add(e)
						#U2.remove(e2)
						U2.remove(e)
	U2 = U2.union(Utemp)
	return U2
	
def rule_h(U2: set, var_count):
	#Rule (h), third of 4 exp = exp rules
	Uremove=set()
	U3=Utemp=set()
	Utemp=U3=U2
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			U3 = U3 - {e}
			for e2 in list(U3):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "exp" and e2 not in Uremove:
						#create three new equations
						u=e2.left_side
						F = Function("f", 2)
						var1 = str()
						var1 = 'v_'+str(var_count[0]) 
						var_count[0] = var_count[0] + 1
						var2 = str()
						var2 = 'v_'+str(var_count[0])
						var_count[0] = var_count[0] + 1
						var3 = str()
						var3 = 'v_'+str(var_count[0])
						var_count[0] = var_count[0] + 1
						var4 = str()
						var4 = 'v_'+str(var_count[0])
						var_count[0] = var_count[0] + 1
						var1 = Variable(var1) #W'
						var2 = Variable(var2) #Y'
						var3 = Variable(var3) #Z
						var4 = Variable(var4) #L
						t1 = FuncTerm(e.right_side.function, [var3, var4])
						t2 = FuncTerm(e.right_side.function, [var3, var2])
						t3 = FuncTerm(e.right_side.function, [var3, var1])
						t4 = FuncTerm(F, [e.right_side.arguments[1], var2])
						t5 = FuncTerm(F, [e2.right_side.arguments[1], var1])
						add1 = Equation(u, t1)
						add2 = Equation(e.right_side.arguments[0], t2)
						add3 = Equation(e2.right_side.arguments[0], t3)
						add4 = Equation(var4, t4)
						add5 = Equation(var4, t5)
						Utemp.add(add1)
						Utemp.add(add2)
						Utemp.add(add3)
						Utemp.add(add4)
						Utemp.add(add5)
						Uremove.add(e2)
						Uremove.add(e)
						U2.remove(e2)
						U2.remove(e)
	U2 = U2.union(Utemp)
	return U2
	
def rule_g(U2: set):
	#Rule (g), second of 4 exp = exp rules
	Utemp=set()
	Utemp = U2
	Uremove=set()
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "exp":
			Utemp = Utemp - {e}
			for e2 in list(Utemp):
				if isinstance(e2.right_side, FuncTerm):
					if e2.left_side == e.left_side and str(e2.right_side.function) == "exp" and e2 not in Uremove:
						e4 = Equation(e.right_side.arguments[1], e2.right_side.arguments[1])
						e5 = Equation(e.right_side.arguments[0], e2.right_side.arguments[0])
						U2.add(e4)
						U2.add(e5)
						Uremove.add(e2)
						U2.remove(e2)
	return U2


#Failure rules

def fail_rules(U2: set):
	test = False
	for e in list(U2):
		if isinstance(e.right_side, FuncTerm) and str(e.right_side.function) == "f":
			for e2 in list(U2):
				if e2.left_side == e.left_side and (( isinstance(e.right_side, FuncTerm) and str(e2.right_side.function) == "g") or (isinstance(e.right_side, FuncTerm) and str(e2.right_side.function) == "exp")):
					test = True
	return(test)

def setpartitions(S: set):
	n = len(S)
	C = list()
	U = list()
	for i in range(n):
		C.append(1)
	sp(0, 1, C, n, U)
	return(U)
	

def sp(m: int, p: int, C: list, N: int, U: list):
	if p > N:
		#print(C)
		U.append(deepcopy(C))
	else:
		for i in range(1, m+1):
			C[p-1] = i
			sp(m, p+1, C, N, U)
		C[p-1] = m+1
		sp(m+1, p+1, C, N, U)
