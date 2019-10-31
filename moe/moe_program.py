#!/usr/bin/env python3
from moe import *
from Unification import *



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


###
# CipherBlockChaining(moe, session_id, iteration):
# PropogatingCBC(moe, session_id, iteration):
# CipherFeedback(moe, session_id, iteration):
# HashCBC(moe, session_id, iteration):
# OutputFeedback(moe, session_id, iteration): NOT IMPLEMENTED
# CounterMode(moe, session_id, iteration): NOT IMPLEMENTED
# AccumulatedBlockCiper(moe, session_id, iteration): NOT IMPLEMENTED
# DoubleHashCBC(moe, session_id, iteration): NOT IMPLEMENTED
###



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

def pairwise(xs):
    result = []
    for i, x in enumerate(xs):
        for y in xs[(i+1):]:
            result.append((x, y))
    return result

def MOE(unif = unif, chaining = CipherBlockChaining, schedule = 'every', length_bound = 10, session_bound = 1):
    m = MOESession(chaining, schedule=schedule)
    sid = 0
    m.rcv_start(sid)
    for i in range(length_bound):
        x = Variable("x_" + str(i))
        result = m.rcv_block(sid, x)
        if schedule is "every":
            for l, r in pairwise(result.subs.range()):
                unifiers = unif(l, r)
                if unifiers is not False:
                    return unifiers
    result = m.rcv_stop(sid)
    if schedule is "end":
        for l, r in pairwise(result.subs.range()):
            unifiers = unif(l, r)
            if unifiers is not False:
                return unifiers
    print("No unifiers found.")