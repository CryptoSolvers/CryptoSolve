from copy import deepcopy
from symcollab.algebra import Function, Variable, Constant, FuncTerm, Equation
from symcollab.algebra.forest import Term_Forest

def test_small():
	f = Function("f", 1)
	g = Function("g", 1)
	x = Variable("x")
	y = Variable("y")
	z = Variable("z")
	c = Constant("c")
		
	eq1 = Equation(f(x), y)
	eq2 = Equation(y, g(z))
	eq3 = Equation(z, c)

	forest = Term_Forest([eq1, eq2, eq3], 5)
	print("creating forest from ", forest.seed)
	print()
	print(forest)
	print(forest.describe())

#test_small()

def test_big():
	f = Function("f", 2)
	g = Function("g", 1)
	z = Variable("z")
	x = Variable("x")
	y = Variable("y")
	b = Variable("b")
	a = Variable("a")
	c = Variable("c")

	fyz = FuncTerm(f, [y, z])
	gb = FuncTerm(g, [b])
	fxz = FuncTerm(f, [x, z])
	fba = FuncTerm(f, [b, a])

	eq1 = Equation(fyz, x)
	eq2 = Equation(y, gb)
	eq3 = Equation(b, fxz)
	eq4 = Equation(z, fba)
	eq5 = Equation(x, a)

	occ = [eq1, eq2, eq4, eq5]
	occ2 = [eq2, eq1, eq4, eq5, eq3]

	print("creating forest from ", occ)
	print()
	steve = Term_Forest(occ, 10)
	print(steve)
	print(steve.describe())
	#print(steve.get_height(steve.forest[0]))
	print("all terms from ", steve.forest[0].term, ":\n ", steve.get_tree(steve.forest[0]))
	
	bob = Term_Forest(occ2, 10)
	print("creating forest from ", occ2)
	print()
	print(bob)

	print("steve equals bob ", steve==bob)
	print("steve lt bob ", steve<bob)
	print("steve le bob ", steve<=bob)
	print("steve gt bob ", steve>bob)
	print("steve ge bob ", steve>=bob)
	print("steve ne bob ", steve!=bob)
	print()

	print("Creating deepcopy of steve: ")
	clone = deepcopy(steve)
	print(clone)
	print("clone contains x ", x in clone)
	print("clone contains g(y) ", g(y) in clone)
	print("clone hash ", hash(clone))
	print("steve hash ", hash(steve))
	print("repr steve:\n", repr(steve))
	
test_big()
