
from Unification import *
from xor import *

x = Variable("x")
y = Variable("y")
a = Constant("a")
b = Constant("b")
f = Function("f", 1)
t1 = xor(f(x), x)
t2 = xor(f(a), b)
t1 = convert_to_XORTerm(t1)
t2 = convert_to_XORTerm(t2)

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
    return XORTerm(args1 + args2)

def resolve(t1, t2):
    #Takes two terms t1 and t2, apply resolution to them, returns all possible results
    #For example, if t1 is f(x) + x and t2 is f(a) + b, then the result is a + b
    results1 = get_resolution_term_and_remaining_term(t1)
    results2 = get_resolution_term_and_remaining_term(t2)
    results = []
    for (term1, remaining_t1) in results1:
        for (term2, remaining_t2) in results2:
            eq = Equation(term1, term2)
            eqs = Equations([eq])
            xor_unifiers = xor_unification(eqs)

            for unifier in xor_unifiers:
                remaining_t1 = convert_to_xorterm(remaining_t1)
                remaining_t2 = convert_to_xorterm(remaining_t2)
                r1 = remaining_t1 * unifier
                r2 = remaining_t2 * unifier
                r1 = convert_to_XORTerm(r1)
                r2 = convert_to_XORTerm(r2)
                results.append(combine_two_XOR_Terms(r1, r2))
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
        print(first)
        del new_terms[0]
        for tm in done:
            results = resolve(tm, first)
            for res in results:
                if(not_in_done(res, done)):
                    done.append(res)
        done.append(first)
        return saturate_helper(done, new_terms)

def saturate(tms):
    terms = list(map(convert_to_XORTerm, tms))
    return saturate_helper([], terms)

