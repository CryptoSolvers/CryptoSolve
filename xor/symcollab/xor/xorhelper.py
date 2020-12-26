from copy import deepcopy
from symcollab.algebra import Constant, Variable, FuncTerm, Equation, SubstituteTerm
from symcollab.Unification.unif import unif
from .structure import Zero, XORTerm, Equations, Disequations, Disequation
from .xor import xor

def is_xor_term(t):
    #return (isinstance(t, FuncTerm)) and (isinstance(t.function, Xor))
    if(isinstance(t, Zero)):
        return False
    else:
        return (isinstance(t, FuncTerm) and t.function.symbol == "xor")

def is_XOR_Term(t):
    return isinstance(t, XORTerm)

def xor_to_list(t):
    #convert a xor-term to a list of terms
    if(not is_xor_term(t)):
        return [t]
    else:
        lst1 = xor_to_list(t.arguments[0])
        lst2 = xor_to_list(t.arguments[1])
        return lst1 + lst2

def simplify(lst):
    result = []
    for item in lst:
        if(isinstance(item, Zero)):
            continue
        if(item in result):
            result.remove(item)
        else:
            result.append(item)
    return result

def simplify_XOR_Term(t):
    simplified_arguments = simplify(t.arguments)
    if(len(simplified_arguments) == 0):
        return Zero()
    elif(len(simplified_arguments) == 1):
        return simplified_arguments[0]
    else:
        return XORTerm(simplified_arguments)

def list_to_xor(lst):
    #convert a list of terms to a xor-term
    if(len(lst) == 0):
        return Zero()
    elif(len(lst) == 1):
        return lst[0]
    else:
        head, *tail = lst
        return xor(head, list_to_xor(tail))

def collect_all_variables_in_term(t):
#Returns a list of variables in a term.
#f(x, g(y)) ==> [x,y]
    if (isinstance(t, Zero)):
        return []
    elif (isinstance(t, Constant)):
        return []
    elif (isinstance(t, Variable)):
        return [t]
    elif (isinstance(t, FuncTerm)):
        result = []
        for arg in t.arguments:
            result = result + collect_all_variables_in_term(arg)
        return list(set(result))
    '''
    elif (isinstance(t, XORTerm)):
        result = []
        for arg in t.arguments:
            result = result + collect_all_variables_in_term(arg)
        return list(set(result))
    '''

def collect_all_variables_in_equation(eq):
    lhs = eq.left_side
    rhs = eq.right_side
    all_variables = collect_all_variables_in_term(lhs) + collect_all_variables_in_term(rhs)
    return list(set(all_variables))

def collect_all_unconstrained_variables_in_equation(eq):
    variables = collect_all_variables_in_equation(eq)
    results = ()
    for var in variables:
        if (not is_constrained_in_equation(var, eq)):
            results.add(var)
    return results

def look_up_a_name(t, eqs):
    #t is a xor-term, eqs is a set of equations.
    #This function looks t up in eqs, and checks if t already has a name in eqs.
    #If so, it returns the existing name. Otherwise, it returns None.
    first_term = t.arguments[0]
    second_term = t.arguments[1]
    for eq in eqs:
        rhs = eq.right_side
        if(is_xor_term(rhs)):
            fst_t = rhs.arguments[0]
            snd_t = rhs.arguments[1]
            possibility1 = first_term == fst_t and second_term == snd_t
            possibility2 = first_term == snd_t and second_term == fst_t
            if(possibility1 or possibility2):
                return eq.left_side
    return None



def name_xor_terms(t, eqs):
    # Purify arguments
    # Name top-level xor-subterms
    # Return (renamed_term, a set of equations)
    if (isinstance(t, Zero)):
        return (t, eqs)
    elif (isinstance(t, Constant)):
        return (t, eqs)
    elif (isinstance(t, Variable)):
        return (t, eqs)
    elif(is_xor_term(t)):
        (term1, eqs) = purify_a_term(t.arguments[0], eqs)
        #eqs = eqs + equation1
        (term2, eqs) = purify_a_term(t.arguments[1], eqs)
        #eqs = eqs + equation2
        #equations = equation1 + equation2

        name = look_up_a_name(xor(term1, term2), eqs)
        if(name != None):
            return (name, eqs)
        else:
            global variable_counter
            variable_counter += 1
            new_variable = Variable("N" + str(variable_counter))
            eqs.append(Equation(new_variable, xor(term1, term2)))
            return (new_variable, eqs)
    elif (isinstance(t, FuncTerm)):
        terms = []
        for arg in t.arguments:
            (term, eqs) = name_xor_terms(arg, eqs)
            #eqs = eqs + equations
            terms.append(term)
        return (FuncTerm(t.function, terms), eqs)
    else:
        print("error")
        return None

def purify_a_term(t, eqs):
    if (isinstance(t, Zero)):
        return (t, eqs)
    elif (isinstance(t, Constant)):
        return (t, eqs)
    elif (isinstance(t, Variable)):
        return (t, eqs)
    elif (is_xor_term(t)):
        (left, eqs) = purify_a_term(t.arguments[0], eqs)
        #eqs = eqs + equation1
        (right, eqs) = purify_a_term(t.arguments[1], eqs)
        #eqs = eqs + equation2
        return (xor(left, right), eqs)
    elif(isinstance(t, FuncTerm)):
        terms = []
        for arg in t.arguments:
            (term, eqs) = name_xor_terms(arg, eqs)
            #eqs = eqs + equations
            terms.append(term)
        return (FuncTerm(t.function, terms), eqs)
    else:
        print("error")
        return None

def purify_an_equation(eq, eqs):
    (purified_lhs, eqs) = purify_a_term(eq.left_side, eqs)
    #eqs = eqs + eqs1
    (purified_rhs, eqs) = purify_a_term(eq.right_side, eqs)
    #eqs = eqs + eqs2
    new_equation = Equation(purified_lhs, purified_rhs)
    return (new_equation, eqs)

def purify_equations(eqs):
    equations = []
    for eq in eqs.contents:
        (left, equations) = purify_an_equation(eq, equations)
        equations.append(left)
        #equations = equations + right
    return Equations(equations)

def is_constrained_in_term(v, t):
    # Check if the current variable is constrained in t
    # That is, check if it appears underneath a function symbol.

    #Precondition: t should be purified.
    if (isinstance(t, Zero)):
        return False
    elif (isinstance(t, Constant)):
        return False
    elif (isinstance(t, Variable)):
        return False
    elif(is_xor_term(t)):
        left = is_constrained_in_term(v, t.arguments[0])
        right = is_constrained_in_term(v, t.arguments[1])
        return left or right
    elif (isinstance(t, FuncTerm)):
        return (v in t)

def is_constrained_in_equation(v, eq):
    lhs = eq.left_side
    rhs = eq.right_side
    return is_constrained_in_term(v, lhs) or is_constrained_in_term(v, rhs)

def is_constrained_in_equations(v, eqs):
    result = False
    equations = eqs.contents
    for eq in equations:
        result = result or is_constrained_in_equation(v, eq)
    return result

def normalize_an_equation(eq):
    if(isinstance(eq.right_side,Zero)):
        lhs = eq.left_side
    else:
        lhs = xor(eq.left_side, eq.right_side)
    lst = xor_to_list(lhs)
    lst = simplify(lst)
    new_lhs = list_to_xor(lst)

    new_rhs = Zero()
    new_eq = Equation(new_lhs, new_rhs)
    return new_eq

def normalize_equations(eqs):
    equations = eqs.contents
    new_eqs = []
    for eq in equations:
        new_eqs.append(normalize_an_equation(eq))
    return Equations(new_eqs)

def apply_sub_to_equation(eq, sub):
    lhs = eq.left_side
    rhs = eq.right_side
    return Equation(lhs * sub, rhs * sub)

def apply_sub_to_disequation(diseq, sub):
    lhs = diseq.left_side
    rhs = diseq.right_side
    return Disequation(lhs * sub, rhs * sub)

def apply_sub_to_equations(eqs, sub):
    equations = eqs.contents
    result = []
    for eq in equations:
        result.append(apply_sub_to_equation(eq, sub))
    return Equations(result)

def apply_sub_to_disequations(diseqs, sub):
    disequations = diseqs.contents
    result = []
    for diseq in disequations:
        result.append(apply_sub_to_disequation(diseq, sub))
    return Equations(result)

class XOR_proof_state:
    def __init__(self, equations, disequations, substitution):
        self.equations = equations
        self.disequations = disequations
        self.substitution = substitution

    def normalize(self):
        eqs = self.equations
        diseqs = self.disequations
        substs = self.substitution
        eqs = normalize_equations(eqs)
        return XOR_proof_state(eqs, diseqs, substs)

    def __repr__(self):
        return str(self.equations) + " | " + str(self.disequations) + " | " + str(self.substitution)

class XOR_Rule:
    def __init__(self):
        pass
    def is_applicable(self, state):
        pass
    def apply(self, state):
        pass

class Rule_Trivial(XOR_Rule):
    def __init__(self):
        pass
    def is_applicable(self, state):
        eqs = state.equations.contents
        for eq in eqs:
            if (isinstance(eq.left_side, Zero) and isinstance(eq.right_side, Zero)):
                return True
        return False
    def apply(self, state):
        eqs = state.equations.contents
        diseqs = state.disequations
        substs = state.substitution
        for index in range(len(eqs)):
            eq = eqs[index]
            if (isinstance(eq.left_side, Zero) and isinstance(eq.right_side, Zero)):
                del eqs[index]
                return XOR_proof_state(Equations(eqs), diseqs, substs)

class Rule_Subst(XOR_Rule):
    def is_applicable(self, state):
        #Check if the "Variable Substitution" rule is applicable.
        eqs = state.equations.contents
        for eq in eqs:
            all_variables = collect_all_variables_in_equation(eq)
            for var in all_variables:
                if(not is_constrained_in_equations(var, state.equations)):
                    return True
        return False

    def build_a_substitution_from(self, v, eq):
        #Build a substitution from equation eq. The domain is variable v.
        #For example, if v: x, eq: f(y) + a = x + b,
        #then, the result would be: x |-> f(y) + a + b
        #Assume that there are no duplicate terms in eq.


        args = xor_to_list(eq.left_side)

        for arg in args:
            if(v == arg):
                args.remove(arg)
        range = list_to_xor(args)
        sigma = SubstituteTerm()
        sigma.add(v, range)
        return sigma

    def get_a_substitution(self, state):
        #Precondition: Variable Substitution rule is applicable.
        #Postcondition: It returns a substitution of the form x |-> t, where x is not constrained.
        #It also remove that equation from state.equations.
        eqs = state.equations.contents
        for eq in eqs:
            all_variables = collect_all_variables_in_equation(eq)
            for var in all_variables:
                if (not is_constrained_in_equations(var, state.equations)):
                    subst = self.build_a_substitution_from(var, eq)
                    state.equations.contents.remove(eq)
                    return subst
        return None

    def apply(self, state):
    #need to be reduced
        subst = self.get_a_substitution(state)
        new_eqs = apply_sub_to_equations(state.equations, subst)
        new_eqs = normalize_equations(new_eqs)
        #new_diseqs = apply_sub_to_disequations(state.disequations, subst)
        state.substitution = state.substitution * subst
        return XOR_proof_state(new_eqs, state.disequations, state.substitution)

class Rule_N_Decompose(XOR_Rule):
    def __init__(self):
        pass

    def consistent_with_one_disequation(self, t1, t2, diseq):
        #Assume that the terms have been reduced.
        #In other words, there are no duplicates xor-subterms.
        if(t1 == diseq.left_side and t2 == diseq.right_side):
            return False
        if (t2 == diseq.left_side and t1 == diseq.right_side):
            return False
        return True

    def consistent_with_disequations(self, t1, t2, diseqs):
        # Assume that the terms have been reduced.
        # In other words, there are no duplicates xor-subterms.
        result = True
        for diseq in diseqs:
            result = result and self.consistent_with_one_disequation(t1, t2, diseq)
        return result

    def is_applicable(self, state):
        result = self.get_equation_and_two_terms(state)
        return result != None

    def get_equation_and_two_terms(self, state):
        eqs = state.equations.contents
        #substs = state.substitution
        diseqs = state.disequations.contents

        def same_function(t1, t2):
            v1 = isinstance(t1, FuncTerm)
            v2 = isinstance(t2, FuncTerm)
            return v1 and v2 and (t1.function.symbol == t2.function.symbol)

        for index in range(len(eqs)):
            seen_terms = []
            all_xor_terms = xor_to_list(eqs[index].left_side)
            for new_term in all_xor_terms:
                    for seen_term in seen_terms:
                        if (same_function(new_term, seen_term) and self.consistent_with_disequations(new_term, seen_term, diseqs)):
                            return (index, new_term, seen_term)
                    seen_terms.append(new_term)
        return None

    def apply(self, state):
        #Apply a rule to some equation
        #Assume that the N-Decomposition rule is applicable.
        #Returns two states
        equations = state.equations.contents
        disequations = state.disequations.contents
        substs = state.substitution

        (eq_index, first_term, second_term) = self.get_equation_and_two_terms(state)

        equations1 = equations
        equations2 = deepcopy(equations)

        equation_to_be_processed = equations1[eq_index]
        del equations1[eq_index]

        #Remove first_term and second_term from new_equation.
        new_term = xor(equation_to_be_processed.left_side, equation_to_be_processed.right_side)
        term_list = xor_to_list(new_term)
        new_lhs = []
        for t in term_list:
            if(t == first_term or t == second_term):
                continue
            else:
                new_lhs.append(t)
        if(len(new_lhs) != 0):
            new_equation = Equation(list_to_xor(new_lhs), Zero())
        else:
            new_equation = Equation(Zero(), Zero())
        equations1.append(new_equation)
        unifier = unif(first_term, second_term)
        #equations1.append(Equation(xor(first_term.arg, second_term.arg), Zero()))

        #if((first_term == second_term) or (unifier.domain() != [])):
        #    unifiable = True
        #else:
        #    unifiable = False
        if(unifier == False):
            unifiable = False
        else:
            unifiable = True

        disequations1 = disequations
        disequations2 = deepcopy(disequations)
        new_disequation = Disequation(first_term, second_term)
        disequations2.append(new_disequation)

        state2 = XOR_proof_state(Equations(equations2), Disequations(disequations2), substs)
        if(unifiable):
            state1 = XOR_proof_state(apply_sub_to_equations(Equations(equations1), unifier),apply_sub_to_disequations(Disequations(disequations1), unifier), substs * unifier)
            return (unifiable, state1, state2)
        else:
            return (unifiable, state, state2)

class Rule_Decompose(XOR_Rule):
    def __init__(self):
        pass
    def has_two_arguments(self, t):
        if(is_xor_term(t)):
            left_is_not_xor = not is_xor_term(t.arguments[0])
            right_is_not_xor = not is_xor_term(t.arguments[1])
            return left_is_not_xor and right_is_not_xor
    def is_of_form_f_f(self, eq):
        lhs = eq.left_side
        if(self.has_two_arguments(lhs)):
            first = lhs.arguments[0]
            second = lhs.arguments[1]
            lhs_is_func_term = isinstance(first, FuncTerm) and (not isinstance(first, Constant))
            rhs_is_func_term = isinstance(second, FuncTerm) and (not isinstance(second, Constant))
            return lhs_is_func_term and rhs_is_func_term and (first.function.symbol == second.function.symbol)
        else:
            return False
    def is_applicable(self, state):
        eqs = state.equations.contents
        for eq in eqs:
            if(self.is_of_form_f_f(eq)):
                return eq
        return False
    def apply(self, state):
        eq = self.is_applicable(state)
        first = eq.left_side.arguments[0]
        second = eq.left_side.arguments[1]
        sigma = unif(first, second)
        if(sigma == False):
            return (False, None)
        else:
            new_eqs = apply_sub_to_equations(state.equations, sigma)
            new_eqs = normalize_equations(new_eqs)
            state.substitution = state.substitution * sigma
            return (True, XOR_proof_state(new_eqs, state.disequations, state.substitution))


def xor_unification_helper(state):
    #Returns a list of substitutions

    state = state.normalize()
    #print("Here is a state: ")
    #print(state)

    eqs = state.equations
    substs = state.substitution
    diseqs = state.disequations

    if (len(eqs.contents) == 0):     #unifiable
        return [substs]
    trivial_rule = Rule_Trivial()
    subst_rule = Rule_Subst()
    n_decompose_rule = Rule_N_Decompose()
    decompose_rule = Rule_Decompose()
    #if no rule is applicable, return []
    #otherwise take an inference step

    #trivial_applicable = trivial_rule.is_applicable(state)
    #subst_applicable = subst_rule.is_applicable(state)
    #decompose_applicable = decompose_rule.is_applicable(state)

    #
    #if(not (trivial_applicable or subst_applicable or decompose_applicable)):
    #    return []       #not unifiable

    if(trivial_rule.is_applicable(state)):
        new_state = trivial_rule.apply(state)
        return xor_unification_helper(new_state)
    elif(decompose_rule.is_applicable(state)):
        (unifiable, new_state) = decompose_rule.apply(state)
        if(unifiable):
            return xor_unification_helper(new_state)
        else:
            return []
    elif(subst_rule.is_applicable(state)):
        new_state = subst_rule.apply(state)
        return xor_unification_helper(new_state)
    elif(n_decompose_rule.is_applicable(state)):
        (unifiable, state1, state2) = n_decompose_rule.apply(state)
        if(unifiable):
            return xor_unification_helper(state1) + xor_unification_helper(state2)
        else:
            return xor_unification_helper(state2)
    else:
        return []

def xor_unification(eqs):
    equations = purify_equations(eqs)
    diseqs = Disequations([])
    subst = SubstituteTerm()

    state = XOR_proof_state(equations, diseqs, subst)
    solutions = xor_unification_helper(state)

    return solutions


variable_counter = 0