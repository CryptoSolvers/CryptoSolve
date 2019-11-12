#!/usr/bin/env python3
from moe import *

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
        print("  'p_syntactic' for P Syntactic Unification")
        print("  'p_unif' for P XOR Unification")
        print("Currently planned but not implemeneted unification algorithms:")
        print("  'p_ac' for P-AC Unification")
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


