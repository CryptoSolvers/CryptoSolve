from copy import deepcopy
from symcollab.algebra import SubstituteTerm, Equation, Variable, Constant, Function
from symcollab.xor.xor import xor
from symcollab.xor.xorhelper import xor_unification, is_XOR_Term, simplify_XOR_Term
from symcollab.xor.structure import Zero, XORTerm, Equations, ConstrainedTerm
from .p_unif import convert_to_xorterm, convert_to_XORTerm

def get_resolution_term_and_remaining_term(t):
    #Assume that t is in XOR form.
    #For example, if t is f(x) + a + b + c
    #The result is [(f(x), a + b + c), (a, f(x) + b + c), (b, f(x) + a + c), (c, f(x) + a + b)]
    if(not is_XOR_Term(t)):
        return [(t, Zero())]
    else:
        length = len(t.arguments)
        results = []
        for i in range(0, length):
            remaining = deepcopy(t.arguments)
            del remaining[i]
            results.append((t.arguments[i], XORTerm(remaining)))
        return results

def combine_two_XOR_Terms(t1, t2):
    if(not is_XOR_Term(t1)):
        args1 = [t1]
    else:
        args1 = t1.arguments
    if (not is_XOR_Term(t2)):
        args2 = [t2]
    else:
        args2 = t2.arguments
    return simplify_XOR_Term(XORTerm(args1 + args2))

def resolve(constrained_t1, constrained_t2):
    #Takes two constrained terms t1[sigma] and t2[tau], apply resolution to them,
    #returns a list of all possible results
    #For example, if t1 is f(x) + a[y |-> z] and t2 is f(a) + b[y |-> a],
    #then the result is a + b[y |-> a]
    t1 = convert_to_XORTerm(constrained_t1.term)
    constraint1 = constrained_t1.constraint
    t2 = convert_to_XORTerm(constrained_t2.term)
    constraint2 = constrained_t2.constraint
    constraint12 = combine_two_substitutions(constraint1, constraint2)
    if(constraint12 == []):
        return []
    results1 = get_resolution_term_and_remaining_term(t1)
    results2 = get_resolution_term_and_remaining_term(t2)
    results = []
    for (term1, remaining_t1) in results1:
        for (term2, remaining_t2) in results2:
            eq = Equation(convert_to_xorterm(term1), convert_to_xorterm(term2))
            eqs = Equations([eq])
            #print("solving:")
            #print(eq)
            xor_unifiers = xor_unification(eqs)
            #print("xor unifiers:")
            #for xor_u in xor_unifiers:
            #    print(xor_u)

            for unifier in xor_unifiers:
                for cons12 in constraint12:
                    constraint123 = combine_two_substitutions(unifier, cons12)
                    for cons123 in constraint123:
                        remaining_t1 = convert_to_xorterm(remaining_t1)
                        remaining_t2 = convert_to_xorterm(remaining_t2)
                        r1 = remaining_t1 * cons123
                        r2 = remaining_t2 * cons123
                        r1 = convert_to_XORTerm(r1)
                        r2 = convert_to_XORTerm(r2)
                        constraint_term = ConstrainedTerm(combine_two_XOR_Terms(r1, r2), cons123)
                        results.append(constraint_term)
    return results

def not_in_done(term, done):
    result = True
    for done_term in done:
        if(term == done_term):
            result = False
    return result

def saturate_helper(done, new_terms):
    if(new_terms == []):
        return done
    else:
        first = new_terms[0]
        del new_terms[0]
        for tm in done:
            #print("tm:")
            #print(tm.term)
            #print("first:")
            #print(first.term)
            results = resolve(tm, first)
            for res in results:
                if(not_in_done(res, done)):
                    done.append(res)
                    #print("adding:")
                    #print(res.term)
                    #print(res.constraint)
        done.append(first)
        return saturate_helper(done, new_terms)

def saturate(tms):
    #terms = list(map(convert_to_XORTerm, tms))
    #constrained_terms = []
    #for term in terms:
    #    constrained_terms.append(ConstrainedTerm(term, SubstituteTerm()))
    return saturate_helper([], tms)

def combine_two_substitutions(subst1, subst2):
    #Combine two substitutions, and get a list of combined substitutions.
    #For example, if sub1 = {x1 |-> f(x), x2 |-> b}, sub2 = {x1 |-> f(a)},
    #then the result would be [{x1 |-> f(a), x2 |-> b}]
    #print("combining")
    #print(sub1)
    #print("and")
    #print(sub2)
    #print("end")
    sub1 = deepcopy(subst1)
    sub2 = deepcopy(subst2)
    domain1 = list(sub1.domain())
    domain2 = list(sub2.domain())
    #if(sub2 == None):
    if(domain2 == []):
        return [sub1]
    else:
        #domain2 = list(sub2.domain())
        first_var_in_sub2 = domain2[0]
        first_var_maps_to_in_sub2 = first_var_in_sub2 * sub2
        if(first_var_in_sub2 in domain1):
            first_var_maps_to_in_sub1 = first_var_in_sub2 * sub1
            if(first_var_maps_to_in_sub1 == first_var_maps_to_in_sub2):
                #print("duplicate variables map to the same term")
                sub2.remove(first_var_in_sub2)
                return combine_two_substitutions(sub1, sub2)
            else:
                #print("duplicate variables map to different terms")
                eq = Equation(convert_to_xorterm(first_var_maps_to_in_sub1), convert_to_xorterm(first_var_maps_to_in_sub2))
                eqs = Equations([eq])
                unifiers = xor_unification(eqs)

                results = []
                sub2.remove(first_var_in_sub2)
                for unifier in unifiers:
                    result = combine_two_substitutions(sub1 * unifier, sub2 * unifier)
                    results = results + result
                return results
        else:
            #print("no duplicate variables found")
            sigma = SubstituteTerm()
            sigma.add(first_var_in_sub2, first_var_maps_to_in_sub2)
            sub1 = sub1 * sigma
            sub2.remove(first_var_in_sub2)
            return combine_two_substitutions(sub1, sub2)

def combine_list_of_substitutions_helper(lst, current):
    if(lst == []):
        return current
    else:
        results = []
        list1 = lst[0]
        del lst[0]
        for lst1 in list1:
            for cur in current:
                res = combine_two_substitutions(lst1, cur)
                results = results + res
        return combine_list_of_substitutions_helper(lst, results)

def combine_list_of_substitutions(lst):
    #It takes lst is a list of lists of substitutions,
    #returns a list of substitutions.
    #For example, if lst is: [[{x |-> f(z)}, {x |-> a}], [{x |-> f(b)}]],
    #then the result is [{x |-> f(b)}]
    sigma = SubstituteTerm()
    return combine_list_of_substitutions_helper(lst, [sigma])

def is_original_variable(var):
    #Checks if var is an original variable appearing in some MOO program P.
    first_letter = var.symbol[0]
    return first_letter == 'x'

def contains_original_var_only(sigma):
    #Checks if sigma only contains original variables appearing in some MOO program P.
    domain = sigma.domain()
    for var in domain:
        if(not is_original_variable(var)):
            return False
    return True

def add_empty_subst_to_dictionary(dict):
    new_dict = {}
    for key in dict.keys():
        old_value = dict[key]
        new_value = []
        for val in old_value:
            new_value.append(ConstrainedTerm(val, SubstituteTerm()))
        new_dict.update({key: new_value})
    return new_dict

def add_empty_subst_to_initial_list(lst):
    new_list = []
    for item in lst:
        new_list.append(ConstrainedTerm(item, SubstituteTerm()))
    return new_list

def fix(sigma, constraint):
    #Fix sigma by instantiating it so that it becomes a P-unifier.
    print("fixing:")
    print(sigma)
    if(contains_original_var_only(sigma)):
        return sigma
    else:
        #Prepare for a list of saturation problem
        problem_list = []
        for var in sigma.domain():
            if(is_original_variable(var)):
                problem = deepcopy(constraint[var])
                problem.append(ConstrainedTerm(var * sigma, SubstituteTerm()))
                problem_list.append(problem)

        #Solve them
        list_of_substitutions = []
        for p in problem_list:
            saturation_result = saturate(p)
            substs = []
            for sat_res in saturation_result:
                if(sat_res.term == Zero()):
                    substs.append(sat_res.constraint)
            list_of_substitutions.append(substs)

        #Combine the resulting substitutions
        results = combine_list_of_substitutions(list_of_substitutions)
        if(results == []):
            return None

        #Find a substitution that can be fixed recursively
        # Use it to instantiate sigma, return the result
        for tau in results:
            result = fix(tau, instantiate_a_constraint(constraint, tau))
            if(result != None):
                return sigma * result
        return None

def instantiate_a_constraint(constraint, sigma):
    #Instantiate a constraint using sigma
    #For example, if constraint is {x1: [a, b], x2: [f(x1)]}, and sigma is {x1 |-> a}
    #then the result is {x1: [a, b], x2: [f(a)]}
    new_constraints = {}
    for key in constraint.keys():
        old_constraint = constraint[key]
        new_constraint = []
        for o in old_constraint:
            new_constraint.append(ConstrainedTerm(o.term * sigma, SubstituteTerm()))
        new_constraints.update({key: new_constraint})
    return new_constraints

x1 = Variable("x1")
x2 = Variable("x2")
x3 = Variable("x3")
x4 = Variable("x4")

a = Constant("a")
b = Constant("b")
c = Constant("c")
d = Constant("d")
f = Function("f", 1)

t0 = a
t1 = xor(a, b)
t2 = xor(b, c)
t3 = f(xor(x1, c))
t4 = f(x2)

constraint = dict()
constraint[x1] = [t1, t0]
constraint[x2] = [t0, t1, t2]
constraint[x3] = [t1, t2, t3]
constraint[x4] = [t1, t2, t3, t4]
initial_list = [t1, t2, t3, t4]

constraint = add_empty_subst_to_dictionary(constraint)

initial_list = list(map(convert_to_XORTerm, initial_list))
initial_list = add_empty_subst_to_initial_list(initial_list)

results = saturate(initial_list)
for res in results:
    if(res.term == Zero()):
        result = fix(res.constraint, constraint)
        if(result != None):
            print("I found a unifier:")
            print(result)




