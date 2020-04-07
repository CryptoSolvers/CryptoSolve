import random
from generator import MOE_Generator
from algebra import *
from functools import reduce

class Filtered_MOE_Generator:
    def __init__(self, max_history:int=2, max_f_depth:int=3, must_start_with_IV:bool=False, must_have_chaining:bool=False):
        self.max_history = max_history
        self.max_f_depth = max_f_depth
        self.must_start_with_IV = must_start_with_IV
        self.must_have_chaining = must_have_chaining
        self.exhausted = False
        self.memo = []
        self.filtered_it=self._construct_iter()
   
    def _check_f_depth(self, t, depth_level=0):
        if isinstance(t, Variable) or isinstance(t, Constant) or isinstance(t, Function):
            return depth_level
        max_depth = 0
        for ti in t.arguments:
            max_depth = max(max_depth, depth(ti, depth_level + int(t.symbol == "f")))
        return max_depth
    
    def get_next_moe(self):
        next_moe = next(self.filtered_it)
        self.memo.append(next_moe)
        return next_moe
    
    def _construct_iter(self):
        #make functions to put in filter to generate iterable
        #function for checking if an moe starts with the IV
        c_iv = lambda t : (Constant("r") in t) if self.must_start_with_IV else True
        
        #function that checks if it has chaining (I promise it works)
        c_chain = lambda t : reduce((lambda x, y: x+y), [int(Variable("C_{i-"+str(a+1)+"}") in t) for a in range(self.max_history)]) > 0 if self.must_have_chaining else True
        
        #function that checks if you've seen it before
        c_not_seen = lambda t: (t not in self.memo)
        
        condition = lambda t : c_not_seen(t) and c_iv(t) and c_chain(t) and self._check_f_depth(t) <= self.max_f_depth
        return iter(filter(condition, MOE_Generator(self.max_history)))






