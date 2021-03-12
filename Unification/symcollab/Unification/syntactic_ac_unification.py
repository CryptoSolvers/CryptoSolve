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



#Rules

#Mutation Rule ID
def mutation_rule1(U: list, var_count):
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
	return(U) 

#Mutation Rule C
def mutation_rule2(U: list, var_count):
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
	return(U)

#Mutation Rule A1
def mutation_rule3(U: list, var_count):
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
		m1.append(Equation(var3, TempEq.left_side.arguments[1]))
		m1.append(Equation(var1, TempEq.right_side.arguments[0]))
		m1.append(Equation(TempEq.right_side.arguments[1], t2))
		U = U + m1
	return(U)

#Mutation Rule A2
def mutation_rule4(U: list, var_count):
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
	return(U)

#Mutation Rule RC
def mutation_rule5(U: list, var_count):
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
	return(U)
	

#Mutation Rule LC
def mutation_rule6(U: list, var_count):
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
	return(U)


#Mutation Rule MC
def mutation_rule7(U: list, var_count):
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
	

def s_rules(U:list, var_count):
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
				if not help_eq_eq(U[i], U[j]) and U[i].left_side == U[j].left_side:
					U[j].left_side = U[i].right_side
	
	#print("U after merge: ")
	#print(U)
	#Var-rep
	#print("U before var-rep: ")
	#print(U)
	delta = SubstituteTerm()
	Uadd = list()
	for e1 in U:
		if isinstance(e1.left_side, Variable) and isinstance(e1.right_side, Variable):
			addeq = True
			for e2 in Uadd:
				if e2.left_side == e1.left_side:
					addeq = False
			if addeq == True:
				Uadd.append(e1)
	for e in Uadd:
		delta.add(e.left_side, e.right_side)
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
	#Need to improve to more than one layer
	for e in U:
		if isinstance(e.left_side, Variable) and isinstance(e.right_side, FuncTerm):
			if e.left_side in e.right_side:
				print('Occurs Check')
				return list()
	
	#EQE rule
	#add this rule
	
	#remove dup
	#print("U before remove dup: ")
	#print(U)
	Ukeep = list()
	Uremove = list()
	Utemp = U
	for i in range(len(Utemp)):
		adde = True
		for j in range(len(Ukeep)):
			if Utemp[i].left_side == Ukeep[j].left_side and Utemp[i].right_side == Ukeep[j].right_side:
				adde = False
				break
		if adde == True:
			Ukeep.append(Utemp[i])
	U = Ukeep
	#print("print U after remove dup: ")
	#print(U)
	
	#Mutate
	#U = mutation_rules(U, var_count)
	
	#End
	return(U)
	
	
def build_tree(root: MutateNode, var_count):
	Q = list()
	Q.append(root)
	#the length bound will be removed when we add pruning
	while Q != list() and len(Q) <= 50:
		cn = Q.pop(0)
		#Apply S rules - mutate
		Max = 10
		count =0
		Utemp = list()
		while (Utemp != cn.data):
			Utemp = cn.data
			cn.data = s_rules(cn.data, var_count)
			count = count + 1
			#Will remove when we add pruning rule
			if count > Max:
				print("Hit Max")
				break
		if cn.data == list():
			return(list())
		#Test if solved, if so stop
		solved = True
		for e in cn.data:
			if isinstance(e.left_side, FuncTerm) and isinstance(e.right_side, FuncTerm):
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
			return(cn.data)
		#print(len(Q))
	return(list())
		
def synt_ac_unif(U: set):
	#counter until prune is implemented
	print("Syntactic Ac-Unification on the following problem: ")
	print(U)
	Max = 3
	count = 0
	var_count = [0]
	N1 = MutateNode(list(U))
	res = build_tree(N1, var_count)
	#delta = SubstituteTerm()
	print("Solution: ")
	print(res)
	return(res)
