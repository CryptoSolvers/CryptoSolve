import random
from generator import MOE_Generator
from algebra import depth, Constant, Variable
from functools import reduce

class Filtered_MOE_Generator:
    def __init__(self, max_history:int=2, max_f_depth:int=3, must_start_with_IV:bool=False, must_have_chaining:bool=False):
        self.max_history = max_history
        self.max_f_depth = max_f_depth
        self.must_start_with_IV = must_start_with_IV
        self.must_have_chaining = must_have_chaining
        self.exhausted = False
        self.filtered_it=self._construct_iter()
    
    def get_next_moe(self):
        if(not self.exhausted):
            next_moe = next(self.filtered_it)
            if(depth(next_moe) <= self.max_f_depth):
                return next_moe
            self.exhausted = True
        #print("Exhausted all MOEs.")
        return None
    
    def restart(self):
        self.filtered_it = self._construct_iter()
    
    def _construct_iter(self):
        #make functions to put in filter to generate iterable
        #function for checking if an moe starts with the IV
        c_iv = lambda t : (Constant("r") in t) if self.must_start_with_IV else True
        #function that checks if it has chaining (I promise it works)
        c_chain = lambda t : reduce((lambda x, y: x+y), [int(Variable("C_{i-"+str(a+1)+"}") in t) for a in range(self.max_history)]) > 0 if self.must_have_chaining else True
        condition = lambda t : c_iv(t) and c_chain(t)
        return iter(filter(condition, MOE_Generator(self.max_history)))
