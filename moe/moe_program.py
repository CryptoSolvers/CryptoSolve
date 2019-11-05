#!/usr/bin/env python3
from moe import *
from Unification import *

##
### Welcome Message
##
print("Welcome to the MOE Tool")
print("We've exposed the MOE function for you to use\n")

print("Arguments:")
print("unif: The unification algorithm to use")
print("chaining: The function defining how blocks are chained together")
print("schedule: (str) 'every' or 'end'")
print("length_bound: (int) the bound on the length of interactions between advesary and oracle")
print("session_bound: (int) the bound on the number of concurrent sessions allowed\n")

print("Ex: MOE(unif = unif, chaining = CipherBlockChaining, schedule = 'every', length_bound = 10, session_bound = 1)\n")

print("For help, type help(argument_name) where argument_name is a string")
print("Ex: help('unif')")


##
### Help Function
##
def help(argument):
    if argument == 'unif':
        print("Available unification algorithms:")
        print("  'unif' for Syntactic Unification")
        print("  'ac_unify' for AC Unification")
        print("  'p_unif' for P Unification")
        print("  'xor_unification' for XOR Unification")
    elif argument == "chaining":
        print("Note that no quotes are needed for chaining functions.")
        print("Available Chaining Functions:")
        print("  CipherBlockChaining : Cipher Block Chaining")
        print("  PropogatingCBC  : Propogating Cipher Block Chaining")
        print("  CipherFeedback : Cipher Feedback")
        print("  HashCBC : Hash Cipher Block Chaining")
        print("Currently planned but not implemented chaining functions:")
        print("  OutputFeedback : Output Feedback")
        print("  CounterMode : Counter Mode")
        print("  AccumulatedBlockCiper : Accumulated Block Cipher")
        print("  DoubleHashCBC : Double Hash Cipher Block Chaining")
    elif argument == "schedule":
        print("Available schedules:")
        print("  'every' the oracle will send a frame everytime the adversary sends a message")
        print("  'end' the oracle will only send a frame when the advesary marks the end of an interaction")
    elif argument == "length_bound":
        print("An integer argument bounding the length of interactions between the adversary and the oracle")
    elif argument == "session_bound":
        print("Currently not implemented")
        print("An integer argument bounding the number of concurrent session allowed")
    else:
        print("Argument '%s' is not an argument of MOE" % argument)
        print("Arguments of MOE: unif, chaining, schedule, length_bound, session_bound")


##
### Begin Tool
##

from xor.xorhelper import *
from xor.structure import *
from Unification.p_unif import p_unif

def pairwise(xs):
    result = []
    for i, x in enumerate(xs):
        for y in xs[(i+1):]:
            print(Equation(x, y))
            result.append(Equation(x, y))
    return result

def any_unifiers(unifiers : List[SubstituteTerm]) -> bool:
    """Searches a list of unifiers to see if any of them have an entry"""
    for u in unifiers:
        if len(u) > 0:
            return True
    return False

def MOE(unif = unif, chaining = CipherBlockChaining, schedule = 'every', length_bound = 10, session_bound = 1):
    m = MOESession(chaining, schedule=schedule)
    sid = 0
    m.rcv_start(sid)
    constraints = {}
    xor_zero = Zero()

    # Start interactions
    for i in range(1, length_bound + 1):
        x = Variable("x_" + str(i))
        # Update constraints
        if i == 1:
            constraints[x] = [m.IV[sid], xor_zero]
        else:
            last_x = Variable("x_" + str(i - 1))
            constraints[x] = constraints[last_x] + [last_x] + m.cipher_texts[i - 2]
        
        result = m.rcv_block(sid, x)

        # Try to find unifiers if schedule is every
        if schedule is "every":
            unifiers = p_unif(Equations(pairwise(result.subs.range())), constraints)
            if any_unifiers(unifiers):
                return unifiers
    
    # Stop Interaction
    result = m.rcv_stop(sid)
    # If schedule is end then try to find unifiers now
    if schedule is "end":
        unifiers = p_unif(Equations(pairwise(result.subs.range())), constraints)
        if any_unifiers(unifiers):
                return unifiers

    # If we got this far then no unifiers were found
    print("No unifiers found.")