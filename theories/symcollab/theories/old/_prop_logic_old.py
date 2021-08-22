
from typing import List, Set
from symcollab.algebra import Constant, Function, FuncTerm, Variable, Term
from .inductive import TheorySystem, system_from_sort
# from .proposition import Prop, Implies, Or, Not

""" 
Assumes conjunctive normal form, so we can treat each clause as a set. 

Example:
P = Variable("P", sort=Prop.sort)
Q = Variable("Q", sort=Prop.sort)
R = Variable("R", sort=Prop.sort)
S = Variable("S", sort=Prop.sort)
C1 = Clause("C1", {Not(P), Q})
C2 = Clause("C2", {Not(Q), Not(R), S})
C3 = Clause("C3", {P})
C4 = Clause("C4", {R})
C5 = Clause("C5", {Not(S)})
prop_dpp({C1, C2, C3, C4, C5}, {P, Q, R, S})
"""


def clause_extractor(t: Term) -> Set[Term]:
	"""
	Extracts a clause out of an
	Or rooted term. Assumes signature
	{Or, Not}
	"""
	if isinstance(t, (Variable, Constant)):
		return {t}
	if isinstance(t, FuncTerm) and t.function == Not:
		return {t}
	result = set()
	result = result.union(clause_extractor(t.arguments[0]))
	result = result.union(clause_extractor(t.arguments[1]))
	return result

def ptc_helper(prop: Term) -> List[Set[Term]]:
	"""
	Assumes that term is in conjunctive normal
	form and returns a list of clauses.
	Signature must be {Or, Not, And}
	"""
	if isinstance(prop, (Variable, Constant)):
		return [clause_extractor(prop)]
	if isinstance(prop, FuncTerm) and prop.function in [Not, Or]:
		return [clause_extractor(prop)]
	
	result = list()
	for arg in prop.arguments:
		result.extend(ptc_helper(arg))
	return result

def proposition_to_clause(prop: Term) -> List[Set[Term]]:
	"""
	Takes a proposition and returns it
	as a set of clauses
	"""
	if not isinstance(prop, FuncTerm) or prop.function != Implies:
		raise ValueError("[proposition_to_clause] must take Implication proposition as the input.")
	# Negate conclusion as per the DPP resolution algorithm
	prop_arguments = list(prop.arguments)
	prop_arguments[1] = Not(prop_arguments[1])
	prop.arguments = prop_arguments
	# Convert proposition to conjunctive normal form
	cf_prop = Prop.simplify(prop)
	return ptc_helper(cf_prop)


class Clause:
	def __init__(self, name:str, lits:set):
		self.name = name
		self.lits = lits
	def __str__(self):
		return self.name
	def values(self):
		return self.lits
	def names(self):
		return self.lits
	def intersection(self, C):
		return self.lits.intersection(C.lits)
	def union(self, C):
		return self.lits.union(C.lits)
	def isdisjoint(self, C):
		return self.lits.isdisjoint(C.lits)
	def rintersection(self, C):
		for x in self.lits:
			for y in C.lits:
				if x == Not(y):
					return {x, y}
		return {}
	def remove(self, L:Variable):
		if L in self.lits:
			self.lits.remove(L)
	def degen(self):
		for x in self.lits:
			for y in self.lits:
				if x == Not(y):
					return True
		return False
	def contains(self, p:Variable):
		if p in self.lits:
			return True
		else:
			return False

def prop_resolution(C:Clause, D:Clause, name:str):
	S = C.rintersection(D)
	C1=C
	D1=D
	for x in S:
		C1.remove(x)
		D1.remove(x)
	temp = Clause(name, C1.union(D1))
	return temp

def remove_degen(S:set) -> set:
	S2 = set()
	for x in S:
		if not x.degen():
			S2.add(x)
	return S2

#DPP
def prop_dpp(SC:set, SV:set) -> bool:
	N = len(SV)
	S = SC
	for i in range(N):
		S = remove_degen(S)
		p = SV.pop()
		T = set()
		for x in S:
			if x.contains(p):
				T.add(x)
		U = set()
		for x in T:
			for y in T:
				if x != y:
					U.add(prop_resolution(x, y, "tmp"))
		S = S.union(U)
		S = S.difference(T)
	if len(S) == 0:
		return True
	else:
		return False

