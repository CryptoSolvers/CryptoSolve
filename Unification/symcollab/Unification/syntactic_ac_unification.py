from .unif import unif
from copy import deepcopy
from symcollab.algebra import *
from collections import Counter
from symcollab.Unification.flat import flat
from typing import Dict, Set

#Tree
class MutateNode:
	def __init__(self, data: list):
		self.id = None
		self.c = None
		self.a1 = None
		self.a2 = None
		self.rc = None
		self.lc = None
		self.mc = None
		self.data = data



#helper for getting vars
def get_vars_from_list(U: list):
	V = set()
	for e in U:
		V = V.union(get_vars(e.left_side))
		V = V.union(get_vars(e.right_side))
	return(V)

#helper function for solved forms
def found_cycle(var: Variable, S: set, U: list):
	for x in S:
		if x == var:
			return(True)
	for x in S:
		for e in U:
			if isinstance(e.left_side, Variable) and x == e.left_side:
				U1 = deepcopy(U)
				U1.remove(e)
				return(found_cycle(var, get_vars(e.right_side), U1))
			elif isinstance(e.right_side, Variable) and x == e.right_side:
				U1 = deepcopy(U)
				U1.remove(e)
				return(found_cycle(var, get_vars(e.left_side), U1))
	return(False)


#helper function for solved forms
def solved_form(U: list):
	#orient
	#print("Checking for solved form: ")
	#print(U)
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	ft = False
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			ft=True
			if isinstance(e.left_side, FuncTerm) :
				return(False)
	if ft == False:
		V= list()
		for e in U:
			V.append(e.left_side)
		if len(V) == len(set(V)):
			return(True)
		else:
			return(False)
	V = list()
	for e in U:
		if isinstance(e.left_side, Variable):
			V.append(e.left_side)
	if len(V) != len(set(V)):
		return(False)
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			S = get_vars(e.right_side)
			var = e.left_side
			U1 = deepcopy(U)
			U1.remove(e)
			if found_cycle(var, S, U1):
				return(False)
	#print("Yes, solved")
	return(True)


#helper function for solved forms dist vars
def solved_form_vd(U: list, VS1: set):
	#orient
	#print("Checking solved form for : ")
	#print(U)
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	FTF = False
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			FTF=True
			if isinstance(e.left_side, FuncTerm):
				return(False)
	if FTF == False:
		return(True)
	V = list()
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1:
				V.append(e.left_side)
	if len(V) != len(set(V)):
		return(False)
	for e in U:
		if isinstance(e.right_side, FuncTerm):
			S = get_vars(e.right_side)
			var = e.left_side
			U1 = deepcopy(U)
			U1.remove(e)
			if found_cycle(var, S, U1):
				return(False)
	#print("Yes it's solved")
	return(True)

#helper function to check for linear term
def linear(t: term, VS1: set):
	V = get_vars(t)
	VTL = list()
	for var in V:
		#if var not in VS1:
		VTL.append(var)
	if len(VTL) == len(set(VTL)):
		return(True)
	else:
		return(False)

#helper function to get the init set of vars
def helper_gvs(U: set):
	V = set()
	for e in U:
		V = V.union(get_vars(e.left_side))
		V = V.union(get_vars(e.right_side))
	return(V)


#Converts equations in U s.t. for 
#each s = t in U, var(s) \cap var(t) = 0
def helper_convert(U: list):
	rmvdl = list()
	addl = list()
	for e in U:
		rmvd = False
		IL = list()
		IR = list()
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			dep = min(depth(e.left_side), depth(e.right_side))
			L = IL = get_vars_or_constants(e.left_side)
			IR = get_vars_or_constants(e.right_side)
			for var in L:
				if var in IR:
					IL.remove(var)
					IR.remove(var)
					rmvd = True
		if rmvd == True:
			rmvdl.append(e)
			t1 = IL[0]
			if len(IL) > 1: 
				t1 = FuncTerm(e.right_side.function, [IL[0], IL[1]])
				for x in range(2, len(IL)):
					t1 = FuncTerm(e.right_side.function, [IL[x], t1])
			t2 = IR[0]
			if len(IR) > 1:
				t2 = FuncTerm(e.right_side.function, [IR[0], IR[1]])
				for y in range(2, len(IR)):
					t2 = FuncTerm(e.right_side.function, [IR[y], t2])
			addl.append(Equation(t1, t2))
	if len(rmvdl) > 0:
		for x in rmvdl:
			U.remove(x)
		U.extend(addl)
	return(U)

#Rules

#Mutation Rule ID
def mutation_rule1(U: list, var_count):
	# print("U before ID: ")
	# print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		m1 =  list()
		m1.append(Equation(var1, TempEq.left_side.arguments[0]))
		m1.append(Equation(var1, TempEq.right_side.arguments[0]))
		m1.append(Equation(var2, TempEq.left_side.arguments[1]))
		m1.append(Equation(var2, TempEq.right_side.arguments[1]))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after ID :")
	#print(U)
	return(U) 

#Mutation Rule C
def mutation_rule2(U: list, var_count):
	#print("U before C: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		m1 =  list()
		m1.append(Equation(var1, TempEq.left_side.arguments[0]))
		m1.append(Equation(var2, TempEq.right_side.arguments[0]))
		m1.append(Equation(var2, TempEq.left_side.arguments[1]))
		m1.append(Equation(var1, TempEq.right_side.arguments[1]))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after C: ")
	#print(U)
	return(U)

#Mutation Rule A1
def mutation_rule3(U: list, var_count):
	#print("U before A1: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var3 = str()
		var3 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		var3 = Variable(var3)
		m1 =  list()
		t1 = FuncTerm(TempEq.right_side.function, [var1, var2])
		t2 = FuncTerm(TempEq.right_side.function, [var2, var3])
		m1.append(Equation(TempEq.left_side.arguments[0], t1))
		m1.append(Equation(TempEq.left_side.arguments[1], var3))
		m1.append(Equation(TempEq.right_side.arguments[0], var1))
		m1.append(Equation(TempEq.right_side.arguments[1], t2))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after A1: ")
	#print(U)
	return(U)

#Mutation Rule A2
def mutation_rule4(U: list, var_count):
	#print("U before A2: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var3 = str()
		var3 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		var3 = Variable(var3)
		m1 =  list()
		t1 = FuncTerm(TempEq.right_side.function, [var1, var2])
		t2 = FuncTerm(TempEq.right_side.function, [var2, var3])
		m1.append(Equation(var1, TempEq.left_side.arguments[0]))
		m1.append(Equation(TempEq.left_side.arguments[1], t2))
		m1.append(Equation(TempEq.right_side.arguments[0], t1))
		m1.append(Equation(var3, TempEq.right_side.arguments[1]))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after A2: ")
	#print(U)
	return(U)

#Mutation Rule RC
def mutation_rule5(U: list, var_count):
	#print("U before RC: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var3 = str()
		var3 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		var3 = Variable(var3)
		m1 =  list()
		t1 = FuncTerm(TempEq.right_side.function, [var1, var2])
		t2 = FuncTerm(TempEq.right_side.function, [var1, var3])
		m1.append(Equation(TempEq.left_side.arguments[0], t1))
		m1.append(Equation(var3, TempEq.left_side.arguments[1]))
		m1.append(Equation(TempEq.right_side.arguments[0], t2))
		m1.append(Equation(var2, TempEq.right_side.arguments[1]))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after RC: ")
	#print(U)
	return(U)
	

#Mutation Rule LC
def mutation_rule6(U: list, var_count):
	#print("U before LC: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
		var1 = str()
		var1 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var2 = str()
		var2 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var3 = str()
		var3 = 'v_'+str(var_count[0])
		var_count[0] = var_count[0] + 1
		var1 = Variable(var1)
		var2 = Variable(var2)
		var3 = Variable(var3)
		m1 =  list()
		t1 = FuncTerm(TempEq.right_side.function, [var2, var3])
		t2 = FuncTerm(TempEq.right_side.function, [var1, var3])
		m1.append(Equation(var1, TempEq.left_side.arguments[0]))
		m1.append(Equation(TempEq.left_side.arguments[1], t1))
		m1.append(Equation(var2, TempEq.right_side.arguments[0]))
		m1.append(Equation(TempEq.right_side.arguments[1], t2))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after LC: ")
	#print(U)
	return(U)


#Mutation Rule MC
def mutation_rule7(U: list, var_count):
	#print("U before MC: ")
	#print(U)
	TempEq = U[0]
	eqfound = False
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
			#new vars
			TempEq = e
			eqfound = True
			break
	if eqfound:
		#Create the 7 possible mutations
		U.remove(TempEq)
		#ID
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
		var1 = Variable(var1)
		var2 = Variable(var2)
		var3 = Variable(var3)
		var4 = Variable(var4)
		m1 =  list()
		t1 = FuncTerm(TempEq.right_side.function, [var1, var2])
		t2 = FuncTerm(TempEq.right_side.function, [var3, var4])
		t3 = FuncTerm(TempEq.right_side.function, [var1, var3])
		t4 = FuncTerm(TempEq.right_side.function, [var2, var4])
		m1.append(Equation(TempEq.left_side.arguments[0], t1))
		m1.append(Equation(TempEq.left_side.arguments[1], t2))
		m1.append(Equation(TempEq.right_side.arguments[0], t3))
		m1.append(Equation(TempEq.right_side.arguments[1], t4))
		U = U + m1
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	#print("U after MC: ")
	#print(U)
	return(U)



def help_eq_eq(e1: Equation, e2: Equation):
	l1 = e1.left_side 
	l2 = e2.left_side
	r1 = e1.right_side
	r2 = e2.right_side
	s1 = {l1, r1}
	s2 = {l2, r2}
	if set() == s1.symmetric_difference(s2):
		return True
	else:
		return False 
	

##########################################################
############# S', vars distinct           ################
##########################################################
def s_rules_vd(U:list, var_count, VS1:set):
	#if solved_form_vd(U, VS1):
	#	return(U)
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	
	#merge
	Utemp = list()
	Uremove = list()
	#print("U before merge: ")
	#print(U)
	for i in range(len(U)):
		if isinstance(U[i].left_side, Variable) and isinstance(U[i].right_side, FuncTerm):
			if U[i].left_side not in VS1:
				for j in range(len(U)):
					if isinstance(U[j].left_side, Variable) and isinstance(U[j].right_side, FuncTerm):
						if not help_eq_eq(U[i], U[j]) and U[i].left_side == U[j].left_side:
							if U[j].left_side not in VS1:
								U[j].left_side = U[i].right_side
	#print("U after merge")
	#print(U)
	
	
	
	#Occurs Check
	#Need to improve to more than one layer
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			S = set(get_vars(e.right_side))
			Utemp = deepcopy(U)
			Utemp.remove(e)
			if found_cycle(e.left_side, S, Utemp) == True:
				#print("Occurs check: ")
				#print(U)
				return(list())

	
	
	#Var-rep
	#print("U before var-rep: ")
	#print(U)
	delta = SubstituteTerm()
	Uadd = list()
	for e1 in U:
		if isinstance(e1.left_side, Variable) and isinstance(e1.right_side, Variable):
			if e1.left_side not in VS1:
				U2 = deepcopy(U)
				U2.remove(e1)
				if e1.left_side in helper_gvs(set(U2)):
					addeq = True
					for e2 in Uadd:
						if e2.left_side == e1.left_side:
							addeq = False
					if addeq == True:
						Uadd.append(e1)
	for e in Uadd:
		#print(e)
		if e.right_side in VS1:
			delta.add(e.left_side, e.right_side)
		else:
			temp1=int(str().join(filter(str.isdigit, str(e.left_side))))
			temp2=int(str().join(filter(str.isdigit, str(e.right_side))))
			if temp1 <= temp2:
				delta.add(e.right_side, e.left_side)
			else:
				delta.add(e.left_side, e.right_side)
		#print("Delta 1:")
		#print(delta)
	for e1 in U:
		applysub = True
		for e2 in Uadd:
			if help_eq_eq(e1, e2) == True:
				applysub = False
		if applysub == True:
			e1.left_side = e1.left_side * delta
			e1.right_side = e1.right_side * delta 
	#print("U after var-rep: ")
	#print(U)
	
	
	#replacement
	#print("U before replace: ")
	#print(U)
	delta2 = SubstituteTerm()
	Uadd = list()
	for e1 in U:
		if isinstance(e1.left_side, Variable) and isinstance(e1.right_side, FuncTerm):
			if e1.left_side not in VS1:
				addeq = True
				for e2 in Uadd:
					if e1.left_side == e2.left_side:
						addeq = False
				if addeq == True:
					Uadd.append(e1)
	for e in Uadd:
		delta2.add(e.left_side, e.right_side)
	#print("Delta 2:")
	#print(delta2)
	if Uadd != list():
		for e1 in U:
			applysub = True
			for e2 in Uadd:
				if help_eq_eq(e1, e2) == True:
					applysub = False
			if applysub == True:
				e1.left_side = e1.left_side * delta2
				e1.right_side = e1.right_side * delta2 
	#print("U after replace: ")
	#print(U)
	
	
	
	#EQE rule
	# print("Before EQE: ")
	# print(U)
	# print(VS1)
	Uremove = list()
	VP = helper_gvs(set(U))
	# print("VP:")
	# print(VP)
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1:
				ST = VP.difference(set(get_vars(e.left_side)))
				if e.left_side not in ST:
					Uremove.append(e)
		elif isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable):
			if e.left_side not in VS1: # and e.right_side in VS1:
				ST = VP.difference({e.left_side})
				if e.left_side not in ST:
					Uremove.append(e)
			# if e.right_side not in VS1 and e.left_side in VS1:
				# ST = VP.difference(set(get_vars(e.right_side)))
				# if e.right_side not in ST:
					# Uremove.append(e)
	for e in Uremove:
		#print("EQE remove: ")
		#print(e)
		U.remove(e)
		
	
	#End
	return(U)


def s_rules(U:list, var_count, VS1:set):
	#orient
	for e in U:
		if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, Variable):
			temp = e.left_side
			e.left_side = e.right_side
			e.right_side = temp
	
	
	#merge
	Utemp = list()
	Uremove = list()
	#print("U before merge: ")
	#print(U)
	for i in range(len(U)):
		if isinstance(U[i].left_side, Variable) and isinstance(U[i].right_side, FuncTerm):
			for j in range(len(U)):
				if isinstance(U[j].left_side, Variable) and isinstance(U[j].right_side, FuncTerm):
					if not help_eq_eq(U[i], U[j]) and U[i].left_side == U[j].left_side:
						U[j].left_side = U[i].right_side
	
	#print("U after merge: ")
	#print(U)
	
	
	#Var-rep
	#print("U before var-rep: ")
	#print(U)
	#print(VS1)
	delta = SubstituteTerm()
	Uadd = list()
	for e1 in U:
		if isinstance(e1.left_side, Variable) and isinstance(e1.right_side, Variable):
			if e1.left_side in VS1:
				if e1.right_side not in VS1:
					etemp = Equation(e1.right_side, e1.left_side)
					fndeq = False
					for e in Uadd:
						if e.left_side == etemp.left_side:
							fndeq = True
					if fndeq == False:
						Uadd.append(etemp)
			else:
				fndeq = False
				for e in Uadd:
					if e.left_side == e1.left_side:
						fndeq = True
				if fndeq == False:
					Uadd.append(e1)
	#print("Here is Uadd: ")
	#print(Uadd)
	for e in Uadd:
		#print("Creating sub for: ")
		#print(e)
		if e.left_side in VS1:
			delta.add(e.right_side, e.left_side)
		else:
			delta.add(e.left_side, e.right_side)
		#print("Delta in step 2: ")
		#print(delta)
	for e1 in U:
		applysub = True
		for e2 in Uadd:
			if help_eq_eq(e1, e2) == True:
				applysub = False
		if applysub == True:
			e1.left_side = e1.left_side * delta
			e1.right_side = e1.right_side * delta 
	#print("U after var-rep: ")
	#print(U)
	
	
	#replacement
	#print("U before replace: ")
	#print(U)
	delta2 = SubstituteTerm()
	Uadd = list()
	for e1 in U:
		if isinstance(e1.left_side, Variable) and isinstance(e1.right_side, FuncTerm):
			addeq = True
			for e2 in Uadd:
				if e1.left_side == e2.left_side:
					addeq = False
			if addeq == True:
				Uadd.append(e1)
	for e in Uadd:
		delta2.add(e.left_side, e.right_side)
	for e1 in U:
		applysub = True
		for e2 in Uadd:
			if help_eq_eq(e1, e2) == True:
				applysub = False
		if applysub == True:
			e1.left_side = e1.left_side * delta2
			e1.right_side = e1.right_side * delta2 
	#print("U after replace: ")
	#print(U)
	
	#Occurs Check
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			S = set(get_vars(e.right_side))
			Utemp = deepcopy(U)
			Utemp.remove(e)
			if found_cycle(e.left_side, S, Utemp) == True:
				#print("Occurs check: ")
				#print(U)
				return(list())
	
	#EQE rule
	Uremove = list()
	#print("U before EQE rule: ")
	#print(U)
	for e in U:
		Utemp = deepcopy(U)
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side not in VS1:
				Utemp.remove(e)
				ST = get_vars_from_list(Utemp)
				if e.left_side not in ST:
					Uremove.append(e)
		elif isinstance(e.left_side, Variable) and isinstance(e.right_side, Variable):
			if e.left_side not in VS1:
				Utemp.remove(e)
				ST = get_vars_from_list(Utemp)
				#print("Here is ST: ")
				#print(ST)
				if e.left_side not in ST:
					Uremove.append(e)
	for e in Uremove:
		#print("EQE remove: ")
		#print(e)
		U.remove(e)

	
	#Prune rule
	VS2 = helper_gvs(set(U))
	VS2 = VS2.difference(VS1)
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side in VS2:
				if not linear(e.right_side, VS1):
					#print("Prune: ")
					#print(e)
					return list()
	
	
	#End
	return(U)
	
	
def build_tree(root: MutateNode, var_count, VS1):
	EQS = list()
	Sol = list()
	Q = list()
	Q.append(root)
	################### Step 1 #########################
	#the length bound will be removed when we add pruning
	while Q != list() and len(Q) <= 200:
		cn = Q.pop(0)
		#Apply S rules
		Max = 20
		count =0
		Utemp = list()
		while (Utemp != cn.data):
			#print("Starting S rules: step(" +str(count) +")")
			Utemp = cn.data
			cn.data = s_rules_vd(cn.data, var_count, VS1)
			count = count + 1
			#print("U after S rules: ")
			#print(cn.data)
			#Remove after testing
			if count > Max:
				print("Hit Max")
				break
		if cn.data != list():
			solved = True
			if not solved_form_vd(cn.data, VS1):
				solved = False
			if solved != True:
				#print("No solved for yet for U: ")
				#print(cn.data)
				dcopy = list()
				dcopy = deepcopy(cn.data) 
				cn.id = MutateNode(mutation_rule1(dcopy, var_count))
				Q.append(cn.id)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.c = MutateNode(mutation_rule2(dcopy, var_count))
				Q.append(cn.c)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
				Q.append(cn.a1)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
				Q.append(cn.a2)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
				Q.append(cn.rc)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
				Q.append(cn.lc)
				dcopy = list()
				dcopy = deepcopy(cn.data)
				cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
				Q.append(cn.mc)
			else:
				#print("Solved True")
				#return(cn.data)
				#print("Adding to EQS: ")
				#print(cn.data)
				EQS.append(cn.data)
				#return(list())
		#print("Len 1: " + str(len(Q)))
	#print("The final length of EQS: ")
	#print(len(EQS))
	#print(EQS)
	#return(list())
	#return(list())
	################### Step 2, 3, 4 ###################
	#the length bound will be removed when we add pruning
	#EQT = list()
	#EQT.append(EQS[0])
	for s in EQS:
		Q = list()
		root = MutateNode(s)
		Q.append(root)
		while Q != list() and len(Q) <= 50:
			cn = Q.pop(0)
			#Apply S rules - mutate
			Max = 20
			count =0
			Utemp = list()
			#print("Starting for problem: ")
			#print(cn.data)
			while (Utemp != cn.data):
				Utemp = cn.data
				#print("U before S rules: ")
				#print(cn.data)
				cn.data = s_rules(cn.data, var_count, VS1)
				count = count + 1
				#print("U after S rules: ")
				#print(cn.data)
				#Will remove when we add pruning rule
				if count > Max:
					print("Hit Max")
					break
			if cn.data != list():
				#return(list())
			#Test if solved, if so stop
				solved = True
				#print("Checking if solved: ")
				#print(cn.data)
				if not solved_form(cn.data):
					solved = False
				if solved != True:
					dcopy = list()
					dcopy = deepcopy(cn.data) 
					cn.id = MutateNode(mutation_rule1(dcopy, var_count))
					Q.append(cn.id)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.c = MutateNode(mutation_rule2(dcopy, var_count))
					Q.append(cn.c)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.a1 = MutateNode(mutation_rule3(dcopy, var_count))
					Q.append(cn.a1)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.a2 = MutateNode(mutation_rule4(dcopy, var_count))
					Q.append(cn.a2)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.rc = MutateNode(mutation_rule5(dcopy, var_count))
					Q.append(cn.rc)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.lc = MutateNode(mutation_rule6(dcopy, var_count))
					Q.append(cn.lc)
					dcopy = list()
					dcopy = deepcopy(cn.data)
					cn.mc = MutateNode(mutation_rule7(dcopy, var_count))
					Q.append(cn.mc)
				else:
					#print("Solved True")
					#return(cn.data)
					Sol.append(cn.data)
			#print("Len 2: " + str(len(Q)))
		#print("Return empty list")
		#return(list())
	return(Sol)
		
def synt_ac_unif(U: set):
	print("Syntactic AC-Unification on the following problem: ")
	print(U)
	Max = 3
	count = 0
	var_count = [0]
	#get the intial set of vars
	VS1 = helper_gvs(U)
	N1 = MutateNode(list(U))
	res = build_tree(N1, var_count, VS1)
	#delta = SubstituteTerm()
	print("Solution: ")
	if res == list():
		print("No solution found")
	else:
		for s in res:
			print(s)
	return(res)
