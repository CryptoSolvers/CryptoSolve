import random
from generator import MOE_Generator
from algebra import depth, Constant, Variable


def generate_moe_iterable(f_depth:int=2, starts_with_IV:bool=True, chaining:bool=True):
    c_depth = lambda t : depth(t) == f_depth
    c_iv = lambda t : (Constant("r") in t) == starts_with_IV
    c_chain = lambda t : (Variable("C_{i-1}") in t) == chaining
    condition = lambda t : c_depth(t) and c_iv(t) and c_chain(t)
    #print(filter(condition, MOE_Generator()))
    return iter(filter(condition, MOE_Generator()))

