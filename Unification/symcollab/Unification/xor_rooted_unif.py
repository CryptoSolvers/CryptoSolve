from symcollab.algebra import Function
from symcollab.Unification.bool_unif import *


def is_maximal(term, terms):
    #Checks if term is maximal in terms.
    (term_low, term_high) = f_depth(term)
    for tm in terms:
        (tm_low, tm_high) = f_depth(tm)
        if(tm_low > term_high):
            return False
    return True

def over_lapping_f_depth(term1, term2):
    #Checks if the f-depth of term1 and term2 are overlapping
    (low1, high1) = f_depth(term1)
    (low2, high2) = f_depth(term2)
    if((low2 <= high1) and (low1 <= high2)):
        return True
    else:
        return False

def convert_to_BTerm(t):
    #Convert a normal term to a term that contains boolean variables
    if (isinstance(t, Constant)):
        return Constant_BTerm(t.symbol)
    if (isinstance(t, Variable)):
        return Var_BTerm(t.symbol)
    if (is_xor_term(t)):
        arguments = xor_to_list(t)
        new_arguments = list(map(convert_to_BTerm, arguments))
        return Xor_BTerm(new_arguments)
    if (isinstance(t, FuncTerm) and not is_xor_term(t)):
        new_arguments = list(map(convert_to_BTerm, t.arguments))
        return BFuncTerm(BFunction(t.function.symbol, t.function.arity), new_arguments)
    print("error in convert_to_BTerm")

def convert_to_Term(t):
    #t is a BTerm
    type = t.get_type()
    if (type == "Zero_BTerm"):
        return Constant("0")
    if(type == "Var_BTerm"):
        return Variable(t.name)
    if (type == "Constant_BTerm"):
        return Constant(t.name)
    elif (type == "BFuncTerm"):
        args = t.arguments
        func = Function(t.function.symbol, t.function.arity)
        new_args = list(map(convert_to_Term, args))
        return FuncTerm(func, new_args)
    elif (type == "Variable_BTerm"):
        return Variable(t.name)
    elif (type == "Mul_BTerm"):
        func = Function("Mul", 2)
        return func(
            convert_to_Term(t.left),
            convert_to_Term(t.right)
        )
    elif (type == "Xor_BTerm"):
        args = t.arguments
        #xor = XorFunction()
        new_args = list(map(convert_to_Term, args))
        #return xor(*[Constant("a"), Constant("b")])
        if(len(new_args) == 1):
            return new_args[0]
        else:
            return xor(*new_args)
    else:
        print("type error in convert_to_Term.")

    return t

def remove_var_not_under_f(t):
    #Takes a term, which doesn't contain any boolean variables,
    #remove vars that do not occur under function symbols.
    if(not is_xor_term(t)):
        return t
    else:
        arguments = xor_to_list(t)
        new_arguments = []
        for arg in arguments:
            if(isinstance(arg, Variable)):
                pass
            else:
                new_arguments.append(arg)
        if(len(new_arguments) == 1):
            return new_arguments[0]
        else:
            return xor(*new_arguments)

class VarMapping:
    def __init__(self, domain, range):
        #maps a normal variable to a term containing boolean variables
        self.domain = domain
        self.range = range

    def __repr__(self):
        return repr(self.domain) + "|->" + repr(self.range)

    def __eq__(self, x):
        return (self.domain == x.domain) and (self.range == x.range)

class VarSubstitution:
    def __init__(self, mappings):
        self.mappings = mappings

    def __eq__(self, x):
        mappings1 = self.mappings
        mappings2 = x.mappings
        if(len(mappings1) != len(mappings2)):
            return False

        for mapping1 in mappings1:
            if(not (mapping1 in mappings2)):
                return False

        for mapping2 in mappings2:
            if(not (mapping2 in mappings1)):
                return False

        return True

    def apply_to_term(self, t):
        type = t.get_type()
        if (type == "One_BTerm"):
            return t
        if (type == "Zero_BTerm"):
            return t
        if(type == "Constant_BTerm"):
            return t
        elif (type == "Variable_BTerm"):
            return t
        elif (type == "Var_BTerm"):
            mappings = self.mappings
            for mapping in mappings:
                if(mapping.domain == t):
                    return mapping.range
            return t
        elif (type == "BFuncTerm"):
            args = t.arguments
            func = t.function
            new_args = list(map(self.apply_to_term, args))
            return BFuncTerm(func, new_args)
        elif (type == "Xor_BTerm"):
            args = t.arguments
            b_xor = XorFunction()
            new_args = list(map(self.apply_to_term, args))
            return Xor_BTerm(new_args)
        elif(type == "Mul_BTerm"):
            left = self.apply_to_term(t.left)
            right = self.apply_to_term(t.right)
            return Mul_BTerm(left, right)
        else:
            print("error in apply_to_term")
            return None

    def apply_to_terms(self, terms):
        return list(map(self.apply_to_term, terms))

    def apply_to_dictionary(self, dict):
        for d in dict:
            new_terms = self.apply_to_terms(dict[d])
            dict[d] = new_terms

    def union(self, another):
        return VarSubstitution(self.mappings + another.mappings)

    def compose_with_bool_subst(self, b_subst):
        #new_mappings = []
        sigma = SubstituteTerm()
        for m in self.mappings:
            dom = m.domain
            ran = m.range
            new_ran = b_subst.apply_to_term(ran)

            new_dom = convert_to_Term(dom)
            new_ran = convert_to_Term(new_ran.simplify())
            sigma.add(new_dom, new_ran)

        return sigma
            #new_mapping = VarMapping(dom, new_ran)
            #new_mappings.append(new_mapping)

        #return VarSubstitution(new_mappings)

    def print(self):
        for mapping in self.mappings:
            print(mapping)




class Attacker_term:
    def __init__(self, t, s, b):
        self.term = t
        self.set_of_ints = s
        self.b_sub = b

    def print(self):
        print(self.term)
        print(" | ")
        print(self.set_of_ints)
        print(" | ")
        self.b_sub.print()

    def __eq__(self, x):
        if(type(x) != Attacker_term):
            return False
        else:
            return (self.term == x.term) and (self.set_of_ints == x.set_of_ints) and (self.b_sub == x.b_sub)

class Proof_state:
    def __init__(self, set1, set2, set3):
        #self.combine_done = set1
        self.cancel_done = set1
        self.raw_attacker_terms = set2
        self.all_generated_terms = set3

    def print(self):
        print("cancel_done:")
        for s in self.cancel_done:
            s.print()
            print(" , ")
        print("|")
        print("raw_attacker_terms:")
        for s in self.raw_attacker_terms:
            s.print()
            print(" , ")
        print("|")
        print("all_generated_terms:")
        for s in self.all_generated_terms:
            s.print()
            print(" , ")

def saturate(s):
    (flag1, result1) = apply_cancel_rule(s)
    if(flag1):
        return saturate(result1)
    (flag2, result2) = apply_combine_rule(s)
    if (flag2):
        return saturate(result2)
    return s


def apply_cancel_rule(s):
    #combine_done = s.combine_done
    cancel_done = s.cancel_done
    raw_attacker_terms = s.raw_attacker_terms
    all_generated_terms = s.all_generated_terms

    if(raw_attacker_terms == []):
        return (False, s)

    first_raw_attacker_term = raw_attacker_terms[0].term
    set_of_ints = raw_attacker_terms[0].set_of_ints
    b_sub = raw_attacker_terms[0].b_sub

    type = first_raw_attacker_term.get_type()
    if(type == "Mul_BTerm"):
        dom = get_coefficient(first_raw_attacker_term)
        ran = Zero_BTerm()
        m1 = BMapping(dom, ran)
        sub = BSubstitution([m1])

        (composable, new_b_sub) = sub.compose(b_sub)
        if (not composable):
            print("error in applying the cancel rule")
        new_attacker_term = Attacker_term(Zero_BTerm(), set_of_ints, new_b_sub)
        cancel_done.append(new_attacker_term)
        all_generated_terms.append(new_attacker_term)
        new_state = Proof_state(cancel_done, raw_attacker_terms, all_generated_terms)
        return (True, new_state)
    if (type != "Xor_BTerm"):
        cancel_done.append(raw_attacker_terms[0])
        raw_attacker_terms.remove(raw_attacker_terms[0])
        new_state = Proof_state(cancel_done, raw_attacker_terms, all_generated_terms)
        return (True, new_state)

    arguments = first_raw_attacker_term.arguments
    number_of_arguments = len(arguments)
    for i in range(0, number_of_arguments):
        first_cancelled_term = arguments[i]
        if (not (is_maximal(first_cancelled_term, arguments))):
            continue
        for j in range(i + 1, number_of_arguments):
            second_cancelled_term = arguments[j]
            if (not (is_maximal(second_cancelled_term, arguments))):
                continue
            if (not over_lapping_f_depth(first_cancelled_term, second_cancelled_term)):
                continue
            (flag, subs) = Boolean_unify(first_cancelled_term, second_cancelled_term)
            if (flag == False):
                continue

            new_attacker_terms = []
            for sub in subs:
                new_term = sub.apply_to_term(first_raw_attacker_term)
                new_term = new_term.simplify()
                (composable, new_b_sub) = sub.compose(b_sub)
                if (not composable):
                    print("error in applying the cancel rule")
                new_attacker_term = Attacker_term(new_term, set_of_ints, new_b_sub)

                if (not (new_attacker_term in all_generated_terms)):
                    all_generated_terms.append(new_attacker_term)
                    new_attacker_terms.append(new_attacker_term)

            if (new_attacker_terms == []):
                continue
            else:
                raw_attacker_terms = raw_attacker_terms + new_attacker_terms
                new_state = Proof_state(cancel_done, raw_attacker_terms, all_generated_terms)
                return (True, new_state)

    cancel_done.append(raw_attacker_terms[0])
    raw_attacker_terms.remove(raw_attacker_terms[0])
    new_state = Proof_state(cancel_done, raw_attacker_terms, all_generated_terms)
    return (True, new_state)

def apply_combine_rule(s):
    #combine_done = s.combine_done
    cancel_done = s.cancel_done
    raw_attacker_terms = s.raw_attacker_terms
    all_generated_terms = s.all_generated_terms

    #if(cancel_done == []):
    #    return (False, s)



    for index_of_first_term in range(0, len(cancel_done)):
        first_attack_term = cancel_done[index_of_first_term]
        term1 = first_attack_term.term
        set_of_ints1 = first_attack_term.set_of_ints
        b_sub1 = first_attack_term.b_sub

        for index_of_second_term in range(index_of_first_term + 1, len(cancel_done)):
            second_attack_term = cancel_done[index_of_second_term]
            term2 = second_attack_term.term
            set_of_ints2 = second_attack_term.set_of_ints
            b_sub2 = second_attack_term.b_sub

            #get list1 and list2 ready
            if(term1.get_type() != "Xor_BTerm"):
                list1 = [term1]
            else:
                list1 = term1.arguments
            if (term2.get_type() != "Xor_BTerm"):
                list2 = [term2]
            else:
                list2 = term2.arguments

            for i in range(0, len(list1)):
                candidate_summand1 = list1[i]
                if (not (is_maximal(candidate_summand1, list1))):
                    continue
                for j in range(0, len(list2)):
                    candidate_summand2 = list2[j]
                    if (not (is_maximal(candidate_summand2, list2))):
                        continue
                    if (not over_lapping_f_depth(candidate_summand1, candidate_summand2)):
                        continue
                    set_of_ints3 = set_of_ints1 & set_of_ints2
                    if(set_of_ints3 != set()):
                        continue

                    ########################################
                    (flag, subs) = Boolean_unify(candidate_summand1, candidate_summand2)
                    if (flag == False):
                        continue

                    new_attacker_terms = []
                    for sub in subs:
                        new_term = Xor_BTerm(list(list1) + list(list2))
                        new_term = sub.apply_to_term(new_term)
                        new_term = new_term.simplify()
                        (composable, new_b_sub) = sub.compose(b_sub1)
                        if (not composable):
                            print("error in applying the cancel rule")
                        (composable, new_b_sub) = new_b_sub.compose(b_sub2)
                        if (not composable):
                            print("error in applying the cancel rule")
                        new_attacker_term = Attacker_term(new_term, set_of_ints1 | set_of_ints2, new_b_sub)

                        if (not (new_attacker_term in all_generated_terms)):
                            all_generated_terms.append(new_attacker_term)
                            new_attacker_terms.append(new_attacker_term)

                    if (new_attacker_terms == []):
                        continue
                    else:
                        raw_attacker_terms = raw_attacker_terms + new_attacker_terms
                        new_state = Proof_state(cancel_done, raw_attacker_terms, all_generated_terms)
                        return (True, new_state)
                    #######################################

    #If the combine rule cannot be applied between 1st term and any other term,
    #Move 1st term from cancel_done to combine_done
    #combine_done.append(first_attack_term)
    #cancel_done.remove(first_attack_term)
    #new_state = Proof_state(combine_done, cancel_done, raw_attacker_terms, all_generated_terms)
    return (False, s)

global_boolean_var_counter = 0

def gen_new_boolean_var():
    global global_boolean_var_counter
    global_boolean_var_counter = global_boolean_var_counter + 1
    return Variable_BTerm("b" + str(global_boolean_var_counter))

class XOR_rooted_security:
    def __init__(self, terms, constraints):
        #normal terms
        #"constraints" is a dictionary.
        #For each variable x, it contains a list of avaialable terms s
        #x can be the xor of any subset of s
        self.terms = terms
        self.constraints = constraints

    def get_smallest_var(self):
        for x in self.constraints:
            smallest = True
            for y in self.constraints:
                if(y.symbol < x.symbol):
                    smallest = False
            if(smallest):
                return x
        print("error in get_smallest_var")

    def gen_var_substitution(self):
        for x in self.constraints:
            original_terms = list(map(remove_var_not_under_f, self.constraints[x]))
            self.constraints[x] = list(map(convert_to_BTerm, original_terms))

        final_subst = VarSubstitution([])
        while(len(self.constraints) != 0):
            smallest_var = self.get_smallest_var()
            list_of_terms = self.constraints[smallest_var]
            args = []

            for term in list_of_terms:
                new_bool_var = gen_new_boolean_var()
                if(term.get_type() == "Xor_BTerm"):
                    for arg in term.arguments:
                        args.append(Mul_BTerm(new_bool_var, arg))
                else:
                    args.append(Mul_BTerm(new_bool_var, term))

            d = convert_to_BTerm(smallest_var)
            r = Xor_BTerm(args)
            new_mapping = VarMapping(d, r)
            new_subst = VarSubstitution([new_mapping])

            self.constraints.pop(smallest_var)
            new_subst.apply_to_dictionary(self.constraints)

            final_subst = final_subst.union(new_subst)
            self.subst = final_subst

    def gen_proof_state(self):
        terms = list(map(convert_to_BTerm, self.terms))

        self.gen_var_substitution()
        subst = self.subst
        attacker_terms = []
        empty_subst = BSubstitution([])

        for i in range(0, len(terms)):
            a_term = subst.apply_to_term(terms[i])
            attacker_term = Attacker_term(a_term, {i}, empty_subst)
            attacker_terms.append(attacker_term)

        all_generated_terms = deepcopy(attacker_terms)

        return Proof_state([], attacker_terms, all_generated_terms)

    def solve(self):
        s = self.gen_proof_state()
        s = saturate(s)
        cancel_done = s.cancel_done

        i = 1
        result = []
        for t in cancel_done:
            term = t.term
            set_of_ints = t.set_of_ints
            b_sub = t.b_sub
            if(term == Zero_BTerm()):
                #print("Attack number", end = " ")
                #print(i)
                #print("Take xor of terms:", end = " ")
                #print(set_of_ints)
                #print("Using the following substitution:")
                real_subst = self.subst.compose_with_bool_subst(b_sub)
                result.append(real_subst)
                #print(real_subst)
                #print("\n")
                i = i + 1
        if(i == 1):
            return None
        else:
            return result


