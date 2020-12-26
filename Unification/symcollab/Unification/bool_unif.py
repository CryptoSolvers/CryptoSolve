import copy
import functools

from copy import deepcopy
from symcollab.xor.xorhelper import *

class BFunction:
    def __init__(self, symbol : str, arity : int):
        self.symbol = symbol
        self.arity = arity
    def __call__(self, *args):
        return BFuncTerm(self, args)
    def __eq__(self, x):
        return (self.symbol == x.symbol) and (self.arity == x.arity)

class XorFunction:
    def __init__(self):
        pass
    def __call__(self, *args):
        return Xor_BTerm(args)

class BTerm:
    def __init__(self):
        pass

    def get_type(self):
        return self.type

    def __eq__(self, x):
        pass

    def simplify(self):
        type = self.get_type()
        if (type == "One_BTerm"):
            return self
        if (type == "Zero_BTerm"):
            return self
        if (type == "Constant_BTerm"):
            return self
        elif (type == "Variable_BTerm"):
            return self
        elif (type == "BFuncTerm"):
            args = self.arguments
            func = self.function

            simplified_args = []
            for arg in self.arguments:
                simplified_args.append(arg.simplify())

            return BFuncTerm(func, simplified_args)
        elif (type == "Xor_BTerm"):
            def h(t):
                h_type = t.get_type()
                if (h_type == "Xor_BTerm"):
                    return t.arguments
                else:
                    return [t]

            simplified_args = []
            for arg in self.arguments:
                simplified_args.append(arg.simplify())
            simplified_args = list(map(h, simplified_args))
            new_args = functools.reduce(lambda x, y: x + y, simplified_args)

            result = []
            for new_arg in new_args:
                if(new_arg == Zero_BTerm()):
                    pass
                elif(new_arg in result):
                    result.remove(new_arg)
                else:
                    result.append(new_arg)

            if(len(result) > 0):
                return Xor_BTerm(result)
            else:
                return Zero_BTerm()
        elif (type == "Mul_BTerm"):
            new_left = self.left.simplify()
            new_right = self.right.simplify()
            if((new_left == Zero_BTerm()) or (new_right == Zero_BTerm())):
                return Zero_BTerm()
            elif(new_left == One_BTerm()):
                return new_right
            elif(new_right == One_BTerm()):
                return new_left
            else:
                return Mul_BTerm(new_left, new_right)
        else:
            print(type)
            print("error in simplify")
            return None

class Constant_BTerm(BTerm):
    def __init__(self, name):
        self.name = name
        self.type = "Constant_BTerm"

    def __repr__(self):
        return self.name

    def __eq__(self, x):
        return (self.type == x.type) and (self.name == x.name)

class Zero_BTerm(Constant_BTerm):
    def __init__(self):
        self.type = "Zero_BTerm"

    def __repr__(self):
        return "0"

    def __eq__(self, x):
        return (x.get_type() == "Zero_BTerm")

class One_BTerm(Constant_BTerm):
    def __init__(self):
        self.type = "One_BTerm"

    def __repr__(self):
        return "1"

    def __eq__(self, x):
        return (x.get_type() == "One_BTerm")

class Variable_BTerm(BTerm):
    #Boolean variables
    def __init__(self, name):
        self.name = name
        self.type = "Variable_BTerm"

    def __repr__(self):
        return self.name

    def __eq__(self, x):
        return (self.type == x.get_type()) and (self.name == x.name)

class Var_BTerm(BTerm):
    #real variables that occur in the MOO programs
    def __init__(self, name):
        self.name = name
        self.type = "Var_BTerm"

    def __repr__(self):
        return self.name

    def __eq__(self, x):
        return (self.type == x.get_type()) and (self.name == x.name)

class BFuncTerm(BTerm):
    def __init__(self, function : BFunction, args):
        self.function = function
        assert len(args) == self.function.arity
        self.arguments = args
        self.type = "BFuncTerm"
    def __repr__(self):
        return self.function.symbol + "(" + ", ".join(map(repr, self.arguments)) + ")"

    def __eq__(self, x):
        cond1 = (self.type == x.get_type()) and (self.function == x.function)
        if(not cond1):
            return False
        cond2 = True
        arity = self.function.arity
        for i in range(0, arity):
            cond2 = cond2 and (self.arguments[i] == x.arguments[i])
        return cond2

class Xor_BTerm(BTerm):
    def __init__(self, args):
        self.arguments = args
        self.type = "Xor_BTerm"
    def __repr__(self):
        return  " xor ".join(map(repr, self.arguments))

    def __eq__(self, x):
        cond1 = (self.type == x.get_type())
        if(not cond1):
            return False
        num1 = len(self.arguments)
        num2 = len(x.arguments)
        cond2 = (num1 == num2)
        if(not cond2):
            return False
        cond3 = True
        for i in range(0, num1):
            cond3 = cond3 and (self.arguments[i] == x.arguments[i])
        return cond3

class Mul_BTerm(BTerm):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.type = "Mul_BTerm"

    def __repr__(self):
        return repr(self.left) + "*" + repr(self.right)

    def __eq__(self, x):
        cond1 = (self.type == x.get_type())
        if (not cond1):
            return False
        return ((self.left == x.left) and (self.right == x.right)) or ((self.left == x.left) and (self.right == x.right))

class BMapping:
    def __init__(self, domain, range):
        #domain consists of Boolean variables, range is {0, 1}
        self.domain = domain
        self.range = range

    def __repr__(self):
        return repr(self.domain) + "|->" + repr(self.range)

    def __eq__(self, x):
        return (self.domain == x.domain) and (self.range == x.range)

class BSubstitution:
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
            xor = XorFunction()
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
        new_terms = []
        for term in terms:
            new_terms.append(self.apply_to_term(term))
        return new_terms

    def compose(self, other):
        #modify self.mappings?
        current = copy.deepcopy(self)
        current_mappings = current.mappings
        other_mappings = other.mappings

        already_exists = False
        for other_mapping in other_mappings:
            other_domain = other_mapping.domain
            for current_mapping in current_mappings:
                if(current_mapping.domain == other_mapping.domain):
                    if(current_mapping.range == other_mapping.range):
                        already_exists = True
                    else:
                        return (False, current)
            if(not already_exists):
                current.mappings.append(other_mapping)
        return (True, current)

    def print(self):
        for mapping in self.mappings:
            print(mapping)

def f_depth(t):
    type = t.get_type()
    if (type == "One_BTerm"):
        return (0, 0)
    if (type == "Zero_BTerm"):
        return (0, 0)
    if (type == "Constant_BTerm"):
        return (0, 0)
    elif (type == "Variable_BTerm"):
        print("error in f_depth1")
        return None
    elif (type == "BFuncTerm"):
        args = t.arguments
        current_low = 0
        current_high = 0
        for arg in args:
            (low, high) = f_depth(arg)
            if(low > current_low):
                current_low = low
            if(high > current_high):
                current_high = high
        return (current_low + 1, current_high + 1)
    elif (type == "Xor_BTerm"):
        range_low = 0
        range_high = 0
        best_low = 0
        over_lapping = False
        for arg in t.arguments:
            (low, high) = f_depth(arg)
            #check if there is overlap
            if((high > range_low) and (low < range_high)):
                over_lapping = True
            #update things properly
            if(high > range_high):
                range_high = high
            if(low < range_low):
                range_low = low
            if(low > best_low):
                best_low = low
        if(over_lapping):
            return (0, range_high)
        else:
            return (best_low, range_high)
    elif (type == "Mul_BTerm"):
        left = t.left
        right = t.right
        if(left.get_type() == "Variable_BTerm"):
            (low, high) = f_depth(right)
            return (0, high)
        if (right.get_type() == "Variable_BTerm"):
            (low, high) = f_depth(left)
            return (0, high)
        print("error in f_depth2")
        return None
    else:
        print("error in f_depth3")
        return None

class Constrained_boolean_term():
    # b1*f(c1)+b2*f(c2), [b3*c3], [b4*f(c4), f(c4)]
    def __init__(self, term, disappeared_terms, dup_pairs):
        self.term = term
        self.disappeared_terms = disappeared_terms
        self.dup_pairs = dup_pairs

    def simplify(self):
        self.term = self.term.simplify()

    def apply_a_subst(self, subst):
        term = self.term
        disappeared_terms = self.disappeared_terms
        dup_pairs = self.dup_pairs
        new_term = subst.apply_to_term(term)
        return Constrained_boolean_term(new_term, disappeared_terms, dup_pairs)

    def print(self):
        print("{", end=" ")

        print(self.term)

        print(" | ", end=" ")

        print("[", end=" ")
        for dis_term in self.disappeared_terms:
            print(dis_term)
        print("]", end=" ")

        print(" | ", end=" ")

        print("[", end=" ")
        for (left, right) in self.dup_pairs:
            print(left, right)
        print("]", end=" ")

        print("}", end=" ")

class Unification_state():
    def __init__(self, constrained_terms, current_subst):
        self.constrained_terms = constrained_terms
        self.current_subst = current_subst
    def print(self):
        for t in self.constrained_terms:
            t.print()
        print(" | ", end = " ")
        self.current_subst.print()
    def simplify(self):
        new_constrained_terms = []
        for t in self.constrained_terms:
            t.simplify()
            if(t.term != Zero_BTerm()):
                new_constrained_terms.append(t)
        self.constrained_terms = new_constrained_terms

    def apply_a_subst(self, subst):
        constrained_terms = self.constrained_terms
        current_subst = self.current_subst
        new_constrained_terms = []
        for t in constrained_terms:
            new_constrained_terms.append(t.apply_a_subst(subst))
        return Unification_state(new_constrained_terms, current_subst)

def disappear(state):
    #Takes a unification state, applies the disappear rule, and returns the new state
    #It focuses on the first constrained term.
    constrained_terms = state.constrained_terms
    current_subst = state.current_subst

    first_term = constrained_terms[0]
    term = first_term.term
    disappeared_terms = first_term.disappeared_terms
    dup_pairs = first_term.dup_pairs

    state2 = copy.deepcopy(state)
    constrained_terms2 = state2.constrained_terms
    current_subst2 = state2.current_subst

    first_term2 = constrained_terms2[0]
    term2 = first_term2.term
    disappeared_terms2 = first_term2.disappeared_terms
    dup_pairs2 = first_term2.dup_pairs

    term_type = term.get_type()
    if(term_type == "Mul_BTerm"):
        left = term.left
        right = term.right

        if(left.get_type() == "Variable_BTerm"):
            b_var = left
            #b_term = right
        elif(right.get_type() == "Variable_BTerm"):
            b_var = right
            #b_term = left
        else:
            print("error1 while applying the disappear rule")
            return (False, state, state)

        allowed = True
        for disappeared_term in disappeared_terms:
            if(term == disappeared_term):
                allowed = False
        if(allowed):
            del constrained_terms[0]

            new_subst = BSubstitution([BMapping(b_var, Zero_BTerm())])
            (flag, return_subst) = current_subst.compose(new_subst)
            return_state1 = Unification_state(constrained_terms, return_subst)
            return_state1 = return_state1.apply_a_subst(new_subst)
            return_state1.simplify()

            disappeared_terms2.append(term2)
            new_first_term = Constrained_boolean_term(term2, disappeared_terms2, dup_pairs2)
            del constrained_terms2[0]
            constrained_terms2.append(new_first_term)
            return_state2 = Unification_state(constrained_terms2, current_subst2)

            return (True, return_state1, return_state2)

    if(term_type == "Xor_BTerm"):
        #Find an allowed mul-term
        #If there isn't any, return false
        arguments = term.arguments

        found_one = False
        for argument in arguments:
            if(argument.get_type() == "Mul_BTerm"):
                allowed = True
                for disappeared_term in disappeared_terms:
                    if (argument == disappeared_term):
                        allowed = False
                if(allowed):
                    found_one = True
                    mul_term = argument
                    break

        if(not found_one):
            return (False, state, state)

        #get a multerm
        left = mul_term.left
        right = mul_term.right

        if (left.get_type() == "Variable_BTerm"):
            b_var = left
            # b_term = right
        elif (right.get_type() == "Variable_BTerm"):
            b_var = right
            # b_term = left
        else:
            print("error2 while applying the disappear rule")
            return (False, state, state)

        new_subst = BSubstitution([BMapping(b_var, Zero_BTerm())])
        (flag, return_subst) = current_subst.compose(new_subst)

        arguments = list(arguments)
        arguments.remove(mul_term)
        if(len(arguments) == 1):
            new_term = arguments[0]
        else:
            new_term = Xor_BTerm(arguments)
        new_first_term = Constrained_boolean_term(new_term, disappeared_terms, dup_pairs)

        del constrained_terms[0]
        constrained_terms.append(new_first_term)
        #disappeared_terms.append(mul_term)

        return_state1 = Unification_state(constrained_terms, return_subst)
        return_state1 = return_state1.apply_a_subst(new_subst)
        return_state1.simplify()

        disappeared_terms2.append(mul_term)
        new_first_term = Constrained_boolean_term(term2, disappeared_terms2, dup_pairs2)
        del constrained_terms2[0]
        constrained_terms2.append(new_first_term)
        return_state2 = Unification_state(constrained_terms2, current_subst2)

        return (True, return_state1, return_state2)

    return (False, state, state)

def get_real_term(t):
    type = t.get_type()
    if(type != "Mul_BTerm"):
        return t
    else:
        left = t.left
        right = t.right
        if(left.get_type() == "Variable_BTerm"):
            return right
        else:
            return left

def get_coefficient(t):
    #t: b*c ==> returns (true, b)
    #t: c ==> return (false, c)
    type = t.get_type()
    if (type != "Mul_BTerm"):
        return (False, t)
    else:
        left = t.left
        right = t.right
        if (left.get_type() == "Variable_BTerm"):
            return (True, left)
        else:
            return (True, right)

def constant_or_function(t1, t2):
    #returns true or false
    #t1: c, t2: c ==> true
    #t1: f(c1), t2: f(c2) ==> true
    #t1: b*c, t2: c ==> true
    #t1: b*f(c1), t2: f(c2) ==> true
    #t1: c, t2: b*f(c) ==> false

    real_term1 = get_real_term(t1)
    real_term2 = get_real_term(t2)
    type1 = real_term1.get_type()
    type2 = real_term2.get_type()

    if(type1 == type2):
        if(type1 == "Constant_BTerm"):
            return (real_term1 == real_term2)
        if(type1 == "BFuncTerm"):
            return True
        return False

    return False

def duplicate(state):
    constrained_terms = state.constrained_terms
    current_subst = state.current_subst

    first_constrained_term = constrained_terms[0]
    term = first_constrained_term.term
    disappeared_terms = first_constrained_term.disappeared_terms
    dup_pairs = first_constrained_term.dup_pairs

    state2 = copy.deepcopy(state)
    constrained_terms2 = state2.constrained_terms
    current_subst2 = state2.current_subst

    first_constrained_term2 = constrained_terms2[0]
    term2 = first_constrained_term2.term
    disappeared_terms2 = first_constrained_term2.disappeared_terms
    dup_pairs2 = first_constrained_term2.dup_pairs

    term_type = term.get_type()
    if(term_type != "Xor_BTerm"):
        return (False, state, state)

    found = False
    arguments = term.arguments
    first_summand = arguments[0]
    for i in range(1, len(arguments)):
        if(constant_or_function(first_summand, arguments[i])):
            first = first_summand
            second = arguments[i]

            allowed = True
            for dup_pair in dup_pairs:
                (fst, snd) = dup_pair
                if((first == fst and second == snd) or (first == snd and second == fst)):
                    allowed = False
                    break

            if(allowed):
                found = True
                break

    if(not found):
        return (False, state, state)

    #found "first" and "second"
    t1 = get_real_term(first)
    (flag1, b1) = get_coefficient(first)
    t2 = get_real_term(second)
    (flag2, b2) = get_coefficient(second)
    if(t1.get_type() == "Constant_BTerm" or t1.get_type() == "BFuncTerm"):
        #construct a new first_constrained_term
        arguments = list(term.arguments)
        arguments.remove(first)
        arguments.remove(second)
        if(len(arguments) == 0):
            new_term = Zero_BTerm
        elif(len(arguments) == 1):
            new_term = arguments[0]
        else:
            new_term = Xor_BTerm(arguments)

        #construct a new boolean substitution
        list_of_mappings = []
        if(flag1):
            mapping1 = BMapping(b1, One_BTerm())
            list_of_mappings.append(mapping1)
        if(flag2):
            mapping2 = BMapping(b2, One_BTerm())
            list_of_mappings.append(mapping2)
        new_subst = BSubstitution(list_of_mappings)

        new_first_constrained_term = Constrained_boolean_term(new_term, disappeared_terms, dup_pairs)
        del constrained_terms[0]
        if(len(arguments) != 0):
            constrained_terms.append(new_first_constrained_term)

        if(t1.get_type() == "BFuncTerm"):
            #construct decomposed_constrained_term

            #assuming that f is of arity 1
            decomposed_term = (Xor_BTerm([t1.arguments[0], t2.arguments[0]])).simplify()

            decomposed_constrained_term = Constrained_boolean_term(decomposed_term, [], [])
            constrained_terms.append(decomposed_constrained_term)

        (flag, return_subst) = current_subst.compose(new_subst)
        return_state1 = Unification_state(constrained_terms, return_subst)
        return_state1 = return_state1.apply_a_subst(new_subst)
        return_state1.simplify()

        dup_pairs2.append((first, second))
        new_first_constrained_term = Constrained_boolean_term(term2, disappeared_terms2, dup_pairs2)
        del constrained_terms2[0]
        constrained_terms2.append(new_first_constrained_term)
        return_state2 = Unification_state(constrained_terms2, current_subst2)

        return (True, return_state1, return_state2)
    else:
        print("error in duplicate function")

def b_unify(state):
    #This is a helper function.
    state.simplify()
    constrained_terms = state.constrained_terms
    current_subst = state.current_subst

    if(constrained_terms == []):
        return (True, [current_subst])

    (flag, s1, s2) = disappear(state)
    if(flag):
        (flag1, result1) = b_unify(s1)
        (flag2, result2) = b_unify(s2)
        flag3 = flag1 or flag2
        result3 = []
        if(flag1):
            result3 = result3 + result1
        if (flag2):
            result3 = result3 + result2
        return (flag3, result3)

    (flag, s1, s2) = duplicate(state)
    if (flag):
        (flag1, result1) = b_unify(s1)
        (flag2, result2) = b_unify(s2)
        flag3 = flag1 or flag2
        result3 = []
        if (flag1):
            result3 = result3 + result1
        if (flag2):
            result3 = result3 + result2
        return (flag3, result3)

    return (False, [])

def Boolean_unify(term1, term2):
    new_term = Xor_BTerm([term1, term2])
    new_term = new_term.simplify()
    c_term = Constrained_boolean_term(new_term, [], [])
    subst = BSubstitution([])
    s = Unification_state([c_term], subst)
    (flag, solutions) = b_unify(s)
    if(flag):
        solutions = refine_solutions(solutions)
    return (flag, solutions)

def refine_solutions(solutions):
    def same_solution(sol1, sol2):
        (flag, sol3) = sol1.compose(sol2)
        return (flag and len(sol1.mappings) == len(sol2.mappings) and len(sol2.mappings) == len(sol3.mappings))
    new_solutions = []
    for sol in solutions:
        no_dup = True
        for new_sol in new_solutions:
            if(same_solution(sol, new_sol)):
                no_dup = False
        if(no_dup):
            new_solutions.append(sol)
    return new_solutions











