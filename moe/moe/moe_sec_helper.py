from algebra import Term, Parser, Function, Variable, Constant, SubstituteTerm, Equation
from xor import xor

#Compute the f-depth of a ***ground*** term
def moe_f_depth(t: Term):
	
	#Check if t is a constant
	if isinstance(t, Constant):
		return (0,0)
	#compute depth
	if str(t.function) == "f":
		(l, h) = moe_f_depth(t.arguments[0])
		return (l+1, h+1)
	if str(t.function) == "xor":
		(l1,h1) = moe_f_depth(t.arguments[0])
		(l2,h2) = moe_f_depth(t.arguments[1])
		#check for overlap
		if h1 >= l2 or l1 >= h2:
			return (0, max(h1, h2))
		else:
			return (max(l1, l2), max(h1, h2))

#Compute if a ***ground term *** has randomness 
def moe_has_random(t: Term):
	overlap = False
	if isinstance(t, Variable):
		return False
	if isinstance(t, Constant):
		return True
	if str(t.function) == "f":
		return moe_has_random(t.arguments[0])
	if str(t.function) == "xor":
		(l1,h1) = moe_f_depth(t.arguments[0])
		(l2,h2) = moe_f_depth(t.arguments[1])
		if h1 >= l2 or l1 >= h2:
			overlap = True
		else:
			overlap = False
		rand = moe_has_random(t.arguments[0])
		if not overlap and rand:
			return True
		else:
			return False
			

def moe_syn_security(new_term, old_term):
	(l_new, h_new) = moe_f_depth(new_term)
	(l_old, h_old) = moe_f_depth(old_term)
	rand = moe_has_random(new_term)
	if l_new == h_new and h_new > h_old and rand:
		return True
	else:
		return False
	
	
