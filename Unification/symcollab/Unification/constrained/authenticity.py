from symcollab.algebra import Constant, Equation, Function, FuncTerm, Sort, \
     SubstituteTerm, Variable
from symcollab.algebra.dag import TermDAG

from symcollab.xor.xor import *
from copy import deepcopy



class IndexedVariable(Variable):
	def convertToConstant(self):
		s = self.symbol
		newSymbol = s[0].lower() + s[1:]
		return Constant(newSymbol)
	def __deepcopy__(self, memo):
        	return IndexedVariable(self.symbol, deepcopy(self.sort))

def convertToConstantTerm(t):
	if (isinstance(t, IndexedVariable)):
        	return t.convertToConstant()
	if (isinstance(t, Constant) or isinstance(t, Variable)):
		return t
	if (isinstance(t, FuncTerm) and t.function.symbol == "xor"):
        	new_arguments = list(map(convertToConstantTerm, t.arguments))
        	return xor(*new_arguments)
	if (isinstance(t, FuncTerm) and t.function.symbol != "xor"):
		new_arguments = list(map(convertToConstantTerm, t.arguments))
		return FuncTerm(t.function, new_arguments)
	else:
		print("error in convertToConstantTerm")
		return None


class Unification_state():
    #Each "unification state" has a set of equations and a substitution
    #Initially, there is one equation, and the substitution is the identity substitution.
    #The goal is to apply some inference rules so that the set of equations are simplified
    #and become empty eventually. As the rules are applied, we build up the substitution.
    #Eventually when the set of equations become empty, the substitution is the solution
    #that we are looking for.

    def __init__(self, equations, substitution):
        self.equations = equations
        self.substitution = substitution

    def is_empty(self):
        return self.equations == []

    def get_result(self):
        return self.substitution

    def print(self):
        print(self.equations)
        print(self.substitution)

def topSymbol(t, s):
    #checks if the top symbol of t is s
    return isinstance(t, FuncTerm) and t.function.symbol == s

def containsDorE(lst):
    #checks if a list of terms contains d-rooted or e-rooted terms
    result = False

    for t in lst:
        if(topSymbol(t, 'e') or topSymbol(t, 'd')):
            result = True

    return result

def isC(t):
    return isinstance(t, Variable) and t.symbol[0] == 'C'

def isT(t):
    return isinstance(t, Variable) and t.symbol[0] == 'T'

def containsC(lst):
    #checks if a list of terms contains a variable C
    result = False

    for t in lst:
        if(isC(t)):
            result = True

    return result

def containsT(lst):
    #checks if a list of terms contains a variable C
    result = False

    for t in lst:
        if(isT(t)):
            result = True

    return result

def pickC(lst):
    #Given a list of terms containing C, returns a pair containing C and the other terms
    for t in lst:
        if(isC(t)):
            tm = t

    remaining = []

    for t in lst:
        if(t != tm):
            remaining.append(deepcopy(t))

    return (tm, remaining)

def pickT(lst):
    #Given a list of terms containing T, returns a pair containing T and the other terms
    for t in lst:
        if(isT(t)):
            tm = t

    remaining = []

    for t in lst:
        if(t != tm):
            remaining.append(deepcopy(t))

    return (tm, remaining)

def decompose(state):
    #Try applying the "decompose" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state
    eqs = state.equations
    subst = state.substitution

    first = eqs[0]
    remaining = eqs[1:]

    lhs = first.left_side
    rhs = first.right_side
    flag = False
    new_eqs = []

    if(isinstance(lhs, Constant) and isinstance(rhs, Constant) and lhs == rhs):
        return (True, Unification_state(remaining, subst))

    if(topSymbol(lhs, 'e') and topSymbol(rhs, 'e')):
        flag = True
        new_eqs += [Equation(lhs._arguments[0], rhs._arguments[0])]
        new_eqs += [Equation(lhs._arguments[1], rhs._arguments[1])]

    if(topSymbol(lhs, 'd') and topSymbol(rhs, 'd')):
        flag = True
        new_eqs += [Equation(lhs._arguments[0], rhs._arguments[0])]
        new_eqs += [Equation(lhs._arguments[1], rhs._arguments[1])]

    if(topSymbol(lhs, 'n') and topSymbol(rhs, 'n')):
        flag = True
        new_eqs += [Equation(lhs._arguments[0], rhs._arguments[0])]

    return (flag, Unification_state(new_eqs + remaining, subst))

def elim_c(state):
    #Try applying the "elim_c" rule

    #This rule applied if an equation is of the form: s_1 xor ... xor s_m = t_1 xor ... xor t_n,
    #where no s_i or t_j is d-rooted or e-rooted, and some s_i is a indexed variable C.
    #C1 xor C2 = c1 xor c2; id (applicable)
    #C1 xor e(Tk, C2) = c1 xor e(tk, c2); id (not applicable)

    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

    #Example: C1 xor C2 = c1 xor c2; id ==> True, ; {C1 |-> c1 xor c2 xor C2}
    #Example: C1 xor e(T, C2) = c1 xor e(T, c2); id ==> False, C1 xor e(T, C2) = c1 xor e(T, c2); id
    eqs = state.equations
    subst = state.substitution

    first = eqs[0]
    remaining_eqs = eqs[1:]

    lhs = first.left_side
    rhs = first.right_side
    lhs_summands = summands(lhs)
    rhs_summands = summands(rhs)
    applicable = (not containsDorE(lhs_summands)) and containsC(lhs_summands)
    new_subst = SubstituteTerm()
    remaining_terms = []
    results = []

    if(applicable):
        (var, remaining_terms) = pickC(lhs_summands)
        remaining_terms += rhs_summands
        if(len(remaining_terms) == 1):
            new_subst.add(var, remaining_terms[0])
        else:
            new_subst.add(var, xor(*remaining_terms))
        for t in remaining_eqs:
            results.append(Equation(t.left_side * new_subst, t.right_side * new_subst))

    return (applicable, Unification_state(results, subst * new_subst))

def elim_tk(state):
    #Try applying the "elim_tk" rule

    #This rule applied if an equation is of the form: s_1 xor ... xor s_m = t_1 xor ... xor t_n,
    #where no s_i or t_j is d-rooted or e-rooted, and some s_i is a indexed variable Tk.
    #Tk = tk; id (applicable)
    #Tk xor e(Tk, C1) = tk xor e(tk, c1); id (not applicable)

    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

    #Example: Tk = tk; id ==> true, ; {Tk |-> tk}
    #Example: Tk xor e(Tk, C1) = tk xor e(tk, c1); id ==> false, Tk xor e(Tk, C1) = tk xor e(tk, c1); id
    eqs = state.equations
    subst = state.substitution

    first = eqs[0]
    remaining_eqs = eqs[1:]

    lhs = first.left_side
    rhs = first.right_side
    lhs_summands = summands(lhs)
    rhs_summands = summands(rhs)
    applicable = (not containsDorE(lhs_summands)) and containsT(lhs_summands)
    new_subst = SubstituteTerm()
    remaining_terms = []
    results = []

    if(applicable):
        (var, remaining_terms) = pickT(lhs_summands)
        remaining_terms += rhs_summands
        if(len(remaining_terms) == 1):
            new_subst.add(var, remaining_terms[0])
        else:
            new_subst.add(var, xor(*remaining_terms))
        for t in remaining_eqs:
            results.append(Equation(t.left_side * new_subst, t.right_side * new_subst))

    return (applicable, Unification_state(results, subst * new_subst))

def split_terms(terms):
    #Split a list of terms
    #Example: [e(a, b), t1, t2] => (e(a, b), [t1, t2])

    for t in terms:
        if(topSymbol(t, 'e') or topSymbol(t, 'd')):
            print("debugging:")
            print(t)
            terms.remove(t)
            for tm in terms:
                print(tm)
            return (t, terms)

def split_terms_wrt_term(terms, t1):
    #Split a list of terms
    #Example: [e(a, b), t1, t2], e(a, b') => (e(a, b), [t1, t2])

    def same_top_symbol(t1, t2):
        fst = topSymbol(t1, 'e') and topSymbol(t2, 'e')
        snd = topSymbol(t1, 'd') and topSymbol(t2, 'd')
        return fst or snd
    def same_first_argument(t1, t2):
        t1_arg = t1._arguments[0]
        t2_arg = t2._arguments[0]
        return convertToConstantTerm(t1_arg) == t2_arg

    for t2 in terms:
        if same_top_symbol(t1, t2) and same_first_argument(t1, t2):
            print("Debug:")
            print(t2)
            terms.remove(t2)
            for tm in terms:
                print(tm)
            return (t2, terms)

def split(state):
    #Try applying the "split" rule
    #This rule applied if an equation is of the form: s_1 xor e(...) = t_1 xor e(...)
    #or s_1 xor d(...) = t_1 xor d(...)
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state
    #Example: s_1 xor e(...) = t_1 xor e(...); id ==> s_1 = t_1, e(...) xor e(...); id
    #Example: s_1 = t_1; id (not applicable)
    eqs = state.equations
    subst = state.substitution

    first = eqs[0]
    remaining_eqs = eqs[1:]

    lhs = first.left_side
    rhs = first.right_side
    lhs_summands = summands(lhs)
    rhs_summands = summands(rhs)
    applicable = containsDorE(lhs_summands)

    if(applicable):
        (e_term1, others1) = split_terms(lhs_summands)
        (e_term2, others2) = split_terms_wrt_term(rhs_summands, e_term1)

        eq1 = Equation(e_term1, e_term2)
        if(len(others1) == 1):
            eq2 = Equation(*others1, *others2)
        else:
            eq2 = Equation(xor(*others1), xor(*others2))


        remaining_eqs.append(eq1)
        remaining_eqs.append(eq2)

        return (applicable, Unification_state(remaining_eqs, subst))
    else:
        return (applicable, state)

def apply_rules(state):
    while(not state.is_empty()):
        (successful, new_state) = decompose(state)
        if(successful):
            print("decompose rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = elim_c(state)
        if(successful):
            print("elim_c rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = elim_tk(state)
        if(successful):
            print("elim_tk rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

        (successful, new_state) = split(state)
        if(successful):
            print("split rule applied.")
            state = new_state
            print("new state:")
            state.print()
            continue

    return state.get_result()

def summands(t):
    #Given a term, return the list of all summands
    #Example: xor(a, b, c) ==> [a, b, c], f(a) ==> [f(a)]
    if(isinstance(t, FuncTerm) and isinstance(t.function, Xor)):
        first = t._arguments[0]
        second = t._arguments[1]
        return summands(first) + summands(second)
    else:
        return [t]

def trivial_subst(sub):
    #checks if a substitution is a trivial substitution: e.g. {T |-> t, C1 |-> c1}
    dom = sub.domain()
    result = True

    for var in dom:
        if(var * sub != convertToConstantTerm(var)):
            result = False

    return result

def check_security(tag):
    if not check_syntax(tag):
        print(f"{tag} is not a valid tag.")
        return None
    lhs = tag
    rhs = convertToConstantTerm(lhs)
    eq = Equation(lhs, rhs)
    subst = SubstituteTerm()
    state = Unification_state([eq], subst)
    subst = apply_rules(state)
    if(trivial_subst(subst)):
        print("The authenticity property is satisfied.")
    else:
        print("The authenticity property is violated.")

def check_syntax(t):
    dict = {}
    return (topSymbol(t, 'e') or topSymbol(t, 'd')) and valid_term(t, dict)

def valid_variable(x):
    if isinstance(x, IndexedVariable):
        return x.symbol[0] == 'C'
    else:
        return False

def valid_tweak(t):
    if isinstance(t, IndexedVariable):
        return t.symbol[0] == 'T'
    elif isinstance(t, FuncTerm):
        return t.function.symbol == 'n' and valid_tweak(t.arguments[0])
    else:
        return False

def valid_term(t, dict):
    if valid_variable(t) or valid_tweak(t):
        return True
    if isinstance(t, FuncTerm):
        if t.function.symbol == 'e' or t.function.symbol == 'd':
            first_arg = t.arguments[0]
            second_arg = t.arguments[1]
            if first_arg in dict and dict[first_arg] != second_arg:
                return False
            else:
                dict[first_arg] = second_arg
                return valid_tweak(first_arg) and valid_term(second_arg, dict)
    if isinstance(t, FuncTerm) and t.function.symbol == "xor":
        for arg in t.arguments:
            if valid_tweak(arg) or not valid_term(arg, dict):
                return False
        return True
    else:
        return False



