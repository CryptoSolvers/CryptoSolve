class Lit:
	def __init__(self, name:str, neg:bool):
		self.name = name
		self.neg = neg
	def __str__(self):
		if self.neg:
			st = "-"+self.name
		else:
			st = self.name
		return st
	def nm(self):
		if self.neg:
			st = "-"+self.name
		else:
			st = self.name
		return st
	def negated(self):
		return self.neg
		

class Clause:
	def __init__(self, name:str, lits:set):
		self.name = name
		self.lits = lits
	def __str__(self):
		return self.name
	def values(self):
		return self.lits
	def names(self):
		S = set()
		for L in self.lits:
			S.update({L.nm()})
		return S
	def intersection(self, C):
		return self.lits.intersection(C.lits)
	def union(self, C):
		return self.lits.union(C.lits)
	def isdisjoint(self, C):
		return self.lits.isdisjoint(C.lits)
	def rintersection(self, C):
		for x in self.lits:
			for y in C.lits:
				if x.name == y.name and x.neg != y.neg:
					return {x, y}
		return {}
	def remove(self, L:Lit):
		if L in self.lits:
			self.lits.remove(L)
	def degen(self):
		for x in self.lits:
			for y in self.lits:
				if x.name == y.name and x.neg != y.neg:
					return True
		return False
	def contains(self, p:str):
		for x in self.lits:
			if x.name == p:
				return True
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

