import random
from generator import MOE_Generator
from algebra import depth, Constant, Variable


def get_rand_moe_generator(f_depth:int=2, starts_with_IV:bool=True, chaining:bool=True):
    c_depth = lambda t : depth(t) <= f_depth
    c_iv = lambda t : (Constant("r") in t) if starts_with_IV else True
    c_chain1 = lambda t : (Variable("C_{i-1}") in t) if chaining else True
    c_chain2 = lambda t : (Variable("C_{i-2}") in t) if chaining else True
    c_chain3 = lambda t : (Variable("C_{i-3}") in t) if chaining else True
    condition = lambda t : c_depth(t) and c_iv(t) and (c_chain1(t) or c_chain2(t) or c_chain3(t))
    #print(filter(condition, MOE_Generator()))
    return iter(filter(condition, MOE_Generator()))

