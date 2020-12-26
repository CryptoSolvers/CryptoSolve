from copy import deepcopy
from itertools import *
from symcollab.algebra import *
from symcollab.xor import xor
from symcollab.xor.structure import XORTerm, Zero, Disequations, Disequation, Equations
from symcollab.xor.xorhelper import is_xor_term, xor_to_list, list_to_xor, simplify, xor_unification

class P_unif_problem:
    def __init__(self, eqs, constraints, diseqs):
        self.equations = eqs                #a set of equations
        self.constraints = constraints      #a dictionary
        self.disequations = diseqs          #disequations

def computable(func):
    #Check if func is computable by the attacker
    if(func.symbol == "f"):
        return False
    elif(func.symbol == "h"):
        return True
    elif(func.symbol == "xor"):
        return True
    else:
        return False

def convert_to_XORTerm(t):
    #convert all the sub-xor-terms to XORTerms
    if(isinstance(t, Constant)):
        return t
    if(isinstance(t, Variable)):
        return t
    if(is_xor_term(t)):
        arguments = xor_to_list(t)
        new_arguments = list(map(convert_to_XORTerm, arguments))
        return XORTerm(new_arguments)
    if(isinstance(t, FuncTerm) and not is_xor_term(t)):
        new_arguments = list(map(convert_to_XORTerm, t.arguments))
        return FuncTerm(t.function, new_arguments)
    if(isinstance(t, XORTerm)):
        new_arguments = list(map(convert_to_XORTerm, t.arguments))
        return XORTerm(new_arguments)

def convert_to_xorterm(t):
    # convert all the sub-XORTerms to xor terms
    if (isinstance(t, Constant)):
        return t
    if (isinstance(t, Variable)):
        return t
    if (is_xor_term(t)):
        new_arguments = list(map(convert_to_xorterm, t.arguments))
        return xor(*new_arguments)
    if (isinstance(t, FuncTerm) and not is_xor_term(t)):
        new_arguments = list(map(convert_to_xorterm, t.arguments))
        return FuncTerm(t.function, new_arguments)
    if (isinstance(t, XORTerm)):
        new_arguments = list(map(convert_to_xorterm, t.arguments))
        if(len(new_arguments) == 1):
            return new_arguments[0]
        else:
            return xor(*new_arguments)

def powerset(iterable):
    xs = list(iterable)
    return list(chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1)))

def findsubsets(s, n):
    return list(combinations(s, n))

def is_good_mapping(v, t, p_unif_problem):
    #check if "v |-> t" is a good mapping for p_unif_problem
    constraints = p_unif_problem.constraints
    terms = constraints[v]
    if(t in terms):
        return True
    elif(isinstance(t, Constant)):
        return False
    elif(isinstance(t, Variable)):
        return False
    elif(computable(t.function)):
        result = True
        for arg in t.arguments:
            result = result and is_good_mapping(v, arg, p_unif_problem)
        return result
    else:
        return False

def smaller_than(v1, v2):
    if(v1.symbol < v2.symbol):
        return True
    else:
        return False

def simplify_a_term(t):
    #f(xor(c, c)) ==> 0
    #f(xor(a, b, b)) ==> f(a)
    if(isinstance(t, Variable)):
        return t
    elif(isinstance(t, Constant)):
        return t
    elif(isinstance(t, XORTerm)):
        new_args = []
        term_list = t.arguments
        for arg in term_list:
            new_arg = simplify_a_term(arg)
            new_args.append(new_arg)
        simplified_args = simplify(new_args)
        return XORTerm(simplified_args)
    elif (isinstance(t, FuncTerm) and t.function.symbol != "xor"):
        new_args = []
        for arg in t.arguments:
            new_arg = simplify_a_term(arg)
            new_args.append(new_arg)
        return FuncTerm(t.function, new_args)
    elif(isinstance(t, FuncTerm) and t.function.symbol == "xor"):
        new_args = []
        term_list = xor_to_list(t)
        for arg in term_list:
            new_arg = simplify_a_term(arg)
            new_args.append(new_arg)
        simplified_args = simplify(new_args)
        return list_to_xor(simplified_args)

def get_bad_subterms(subst, v, t, p_unif_problem):
    #Take a variable, a term, a P unification problem
    #returns all bad subterms of t
    constraints = p_unif_problem.constraints
    terms = constraints[v]
    #instantiate terms using variables smaller than v
    sigma = SubstituteTerm()
    domain = subst.domain()
    range = subst.range()
    for var in domain:
        if(smaller_than(var, v)):
            sigma.add(var, range[domain.index(var)])
    new_terms = []
    for constraint_t in terms:
        new_terms.append(simplify_a_term(constraint_t * sigma))
    #print("These are the constraints on ", end = " ")
    #print(v)
    #for t1 in new_terms:
    #    print(t1)
    #print("end constraints.")
    t = simplify_a_term(t)
    if (isinstance(t, Constant)):
        if((t in new_terms) or (isinstance(t, Zero))):
            return []
        else:
            return [(v, t)]
    if (isinstance(t, Variable)):
        if(t in new_terms):
            return []
        else:
            return [(v, t)]
    if (isinstance(t, FuncTerm) and (not computable(t.function))):
        if (t in new_terms):
            return []
        else:
            return [(v, t)]
    if ((isinstance(t, FuncTerm) and computable(t.function)) or isinstance(t, XORTerm)):
        result = []
        for arg in t.arguments:
            new_result = get_bad_subterms(subst, v, arg, p_unif_problem)
            result = result + new_result
        if(result != []):
            result = result + [(v, t)]
        return result

def get_all_bad_subterms(subst, p_unif_problem):
    domain = subst.domain()
    result = []
    constraints = p_unif_problem.constraints
    for v in domain:
        if(v in constraints.keys()):
            t = v * subst
            t = convert_to_XORTerm(t)
            result = result + get_bad_subterms(subst, v, t, p_unif_problem)
    return result

def consistent_with_one_diseq(eq, diseq):
    lhs1 = eq.left_side
    set1 = set(xor_to_list(lhs1))
    lhs2 = diseq.left_side
    set2 = set(xor_to_list(lhs2))
    return (not (set1 == set2))

def consistent_with_diseqs(eq, diseqs):
    result = True
    for diseq in diseqs.contents:
        new_result = consistent_with_one_diseq(eq, diseq)
        result = result and new_result
    return result

def get_vars_in_list(terms):
    #Get a list of variables from a list of terms
    result = []
    for t in terms:
        if(isinstance(t, Variable)):
            result.append(t)
    return result

def make_a_decision(bad_var_term_pairs, p_unif_problem):
    constraints = p_unif_problem.constraints
    disequations = p_unif_problem.disequations
    for (var, term) in bad_var_term_pairs:
        if(isinstance(term, Constant)):
            continue
        if(isinstance(term, FuncTerm) and term.function.symbol == "h"):
            continue
        if(isinstance(term, FuncTerm) and term.function.symbol == "f"):
            #fix it using the Prev rule
            term = convert_to_xorterm(term)
            for prev_term in constraints[var]:
                if(not isinstance(prev_term, Variable)):
                    candidate_equation = Equation(xor(term, prev_term), Zero())
                    if (consistent_with_diseqs(candidate_equation, disequations)):
                        return candidate_equation
        if(isinstance(term, Variable)):
            #set it to zero if consistent
            candidate_equation = Equation(term, Zero())
            if (consistent_with_diseqs(candidate_equation, disequations)):
                return candidate_equation
        if(isinstance(term, XORTerm)):
            #if it has a variable x in it, set x to some subset
            #otherwise, use the cancel rule to cancel two terms
            terms = term.arguments
            terms = simplify(terms)
            terms = list(map(convert_to_xorterm, terms))
            vars = get_vars_in_list(terms)
            if(len(vars) == 0):
                pairs = findsubsets(terms, 2)
                #print(pairs)
                for pair in pairs:
                    (left, right) = pair
                    left = convert_to_xorterm(left)
                    right = convert_to_xorterm(right)
                    candidate_equation = Equation(xor(left, right), Zero())
                    if (consistent_with_diseqs(candidate_equation, disequations)):
                        return candidate_equation
            else:
                for var in vars:
                    subsets = powerset(terms)
                    for subset in subsets:
                        xor_terms = list(set(subset) | set([var]))
                        if(len(xor_terms) == 1):
                            left_side = xor_terms[0]
                        else:
                            left_side = xor(*xor_terms)
                        candidate_equation = Equation(left_side, Zero())
                        if (consistent_with_diseqs(candidate_equation, disequations)):
                            return candidate_equation
    return None

def disequation_from_equation(eq):
    lhs = deepcopy(eq.left_side)
    return Disequation(lhs, Zero())

def add_disequation_to_p(diseq, p):
    disequations = p.disequations.contents
    disequations.append(diseq)

def instantiate_a_problem(p, sigma):
    eqs = p.equations
    constraints = p.constraints

    new_eqs = deepcopy(eqs)

    diseqs = p.disequations.contents
    new_diseqs = []
    for diseq in diseqs:
        new_diseq = Disequation(diseq.left_side * sigma, diseq.right_side * sigma)
        new_diseqs.append(new_diseq)

    new_constraints = {}
    for key in constraints:
        old_constraint = constraints[key]
        new_constraint = []
        for o in old_constraint:
            new_constraint.append(o * sigma)
        new_constraints.update({key: new_constraint})

    return P_unif_problem(new_eqs, new_constraints, Disequations(new_diseqs))

def simplify_substitution(sigma):
    domain = list(sigma.domain())
    r = list(sigma.range())
    tau = SubstituteTerm()
    for index in range(0, len(domain)):
        tau.add(domain[index], simplify_a_term(r[index]))
    return tau

def fix_subst(subst, p):
    #print("Trying to fix this substitution:")
    #print(subst)
    #print("Here are the constraints:")
    #print(p.constraints)
    #print("Here are the disequations:")
    #print(p.disequations)
    bad_var_term_pairs = get_all_bad_subterms(subst, p)
    if(bad_var_term_pairs == []):
        #print("I found a p-unifier.")
        return [subst]        #found a p unifier
    else:
        eq = make_a_decision(bad_var_term_pairs, p)

        if(eq == None):
            #print("I cannot make a decision, failed on this branch.")
            return []

        # debugging info######
        #print("Here is a decision that I made.")
        #print(eq)
        #####################

        diseq = disequation_from_equation(eq)
        eqs = Equations([eq])
        unifiers = xor_unification(eqs)

        #if(unifiers == [SubstituteTerm()]):
        if(unifiers == []):
            #print("I made a bad decision, failed on this branch.")
            add_disequation_to_p(diseq, p)
            return fix_subst(subst, p)

        result = []
        for unifier in unifiers:
            subst2 = deepcopy(subst)
            p2 = deepcopy(p)
            add_disequation_to_p(diseq, p2)

            new_subst = subst * unifier
            new_subst = simplify_substitution(new_subst)
            new_p = instantiate_a_problem(p, unifier)

            res1 = fix_subst(new_subst, new_p)
            res2 = fix_subst(subst2, p2)
            result = result + res1
            result = result + res2
        return result

def p_unif(eqs, constraints):
    diseqs = Disequations([])
    print("Here is the problem:")
    print(eqs)
    print("end")
    p_unif_problem = P_unif_problem(eqs, constraints, diseqs)
    xor_unifiers = xor_unification(eqs)
    p_unifiers = []
    for xor_unifier in xor_unifiers:
        new_p_unifiers = fix_subst(xor_unifier, p_unif_problem)
        p_unifiers = p_unifiers + new_p_unifiers
    return p_unifiers

'''
def get_open_positions(t):
    #t is a term.
    #It returns a list of open positions, which are lists.
    if(isinstance(t, Constant)):
        return [[]]
    elif(isinstance(t, Variable)):
        return [[]]
    else:
        if(computable(t.function)):
            result = [[]]
            for index in range(0, len(t.arguments)):
                sub_result = get_open_positions(t.arguments[index])
                for sub_r in sub_result:
                    sub_r.insert(0, index)
                result = result + sub_result
            return result
        else:
            return [[]]

def subterm_at_position(t, p):
    #returns a subterm of t at position p
    if(len(p) == 0):
        return t
    else:
        p1, *p2 = p
        return subterm_at_position(t.arguments[p1], p2)

def smallest_variable(lst):
    #pick the smallest variable from a list of variables
    if(len(lst) == 0):
        print("Error, trying to pick the smallest variable from an empty list.")
        return None
    else:
        candidate = lst[0]
        for i in range(1, len(lst)):
            if(smaller_than(lst[i], candidate)):
                candidate = lst[i]
        return candidate

'''
