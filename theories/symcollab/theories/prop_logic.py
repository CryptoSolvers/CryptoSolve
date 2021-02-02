
from symcollab.algebra import Constant, Function, Variable, Term
from .inductive import TheorySystem, system_from_sort
from .proposition import *

""" 
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


class Clause:
	def __init__(self, name:str, lits:set):
		self.name = name
		self.lits = lits
	def __str__(self):
		return self.name
	def values(self):
		return self.lits
	def names(self):
		return lits
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

