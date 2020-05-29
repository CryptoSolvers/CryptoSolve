from collections import defaultdict
from algebra import Term, Parser, Function, Variable, Constant, SubstituteTerm, Equation
from xor import xor
from copy import deepcopy
from typing import Dict, List, Optional, Callable
from .moo import *

# Note: This file isn't the most clear in terms of naming mostly since the requirements are not well understood
# As of December, I've attempted to outline the different functions and classes involved, 
# but likely these have changed by the time you read this.

# A frame is supposed to help you keep track with the interactions between an advesary and an oracle.
# The session id is what is used by the Oracle to keep track of the different messages
# The whole message can be recovered by apply the substition to the message. 
class Frame:
    def __init__(self, session_id: int, message: Term, subs):
        self.session_id = session_id
        self.message = message
        self.subs = subs
    def __str__(self):
        return "[" + str(self.session_id) + ", " + str(self.message) + ", " + str(self.subs) + "]"

# You can think of MOESession as an oracle of sorts.
# However, you have to create an oracle for every different chaining function and schedule that you want to use
# The API is largely taken from "Symbolic Security Criteria for Blockwise Adaptive Secure Modes of Encryption" by Catherine Meadows
class MOESession:
    def __init__(self, chaining_function, schedule: str = "every", custom_moe_string: str = ""):
        self.chaining_function = chaining_function
        self.schedule: str = schedule
        self.custom_moe_string: str = custom_moe_string
        if(self.chaining_function == CustomMOE):
            parser = Parser()
            parser.add(Function("f", 1))
            parser.add(Function("xor", 2))
            parser.add(Variable("P[i]"))
            parser.add(Variable("C[i]"))
            parser.add(Variable("C[i-1]"))
            parser.add(Constant("IV"))
            parser.add(Constant("P[0]"))
            parser.parse(custom_moe_string)
        self.sessions: List[int] = []
        # The below variables are dictionaries that are indexed by the session id
        self.subs: Dict[int, SubstituteTerm] = {}
        self.iteration: Dict[int, int] = {}
        self.nonces: Dict[int, List[Constant]] = defaultdict(list)
        self.plain_texts: Dict[int, List[Term]] = defaultdict(list)
        self.cipher_texts: Dict[int, List[Term]] = defaultdict(list)
    
    def rcv_start(self, session_id : int):
        if session_id in self.sessions:
            raise ValueError("Session id %s already started" % (str(session_id)))
        self.sessions.append(session_id)
        # Initialize all the session variables
        self.subs[session_id] = SubstituteTerm()
        self.iteration[session_id] = 0
        # TODO: IV should be a random nounce
        # Need to decide how to make it 'random'
        self.nonces[session_id].append(Constant("r"))
    
    def send(self, session_id: int, last_plaintext: Term, encrypted_blocks: SubstituteTerm) -> Frame:
        return Frame(session_id, last_plaintext, encrypted_blocks)
    
    def rcv_stop(self, session_id: int) -> Optional[Frame]:
        subs = None
        if self.schedule == "end":
            subs = deepcopy(self.subs[session_id])
            last_plaintext = deepcopy(self.plain_texts[session_id][-1])
        # Remove information about the session from MOE
        del self.subs[session_id]
        del self.iteration[session_id]
        del self.plain_texts[session_id]
        del self.cipher_texts[session_id]
        self.sessions.remove(session_id)
        if self.schedule == "end":
            return self.send(session_id, last_plaintext, subs)
        return None

    def rcv_block(self, session_id: int, message: Term) -> Optional[Frame]:
        if session_id not in self.sessions:
            raise ValueError(f"Session id {session_id} not found. Please call rcv_start first.")
        self.iteration[session_id] += 1
        self.plain_texts[session_id].append(message)

        # Create new cipher text variable and map it to the MOE
        sub_var = Variable("y_" + str(self.iteration[session_id]))
        if(self.chaining_function == CustomMOE):
            encrypted_block = self.chaining_function(self, session_id, self.iteration[session_id], self.custom_moe_string)
        else:
            encrypted_block = self.chaining_function(
                self.iteration[session_id],
                self.nonces[session_id],
                self.plain_texts[session_id],
                self.cipher_texts[session_id]
            )
        self.subs[session_id].add(sub_var, encrypted_block)
        self.cipher_texts[session_id].append(sub_var)

        if self.schedule == "every":
            return self.send(session_id, self.plain_texts[session_id][-1], self.subs[session_id])
        return None



##
# Modes of Encryptions (MOEs)
##

def CustomMOE(moe, session_id, iteration, moe_string : str):
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    IV = moe.nonces[session_id][0]
    parser = Parser()
    parser.add(Function("f", 1))
    parser.add(xor)
    parser.add(Variable("P[i]"))
    parser.add(Variable("C[i]"))
    parser.add(Variable("C[i-1]"))
    parser.add(Constant("IV"))
    parser.add(Constant("P[0]"))
    i = iteration - 1
    t = parser.parse(moe_string)
    return _recursive_custom_moe_replacer(t, i, P, C, IV)

#temporary function to assist parser in the CustomMOE function
def _recursive_custom_moe_replacer(t, i, P, C, IV):
    if i < 0:
        i = 0
    if isinstance(t, FuncTerm):
        temp_terms = list(t.arguments)
        for arg_index in range(len(temp_terms)):
            inner_term = temp_terms[arg_index]
            if isinstance(inner_term, FuncTerm):
                temp_terms[arg_index] = _recursive_custom_moe_replacer(inner_term, i, P, C, IV)
            elif "P" in inner_term.symbol:
                if "0" in inner_term.symbol:
                    temp_terms[arg_index] = P[0]
                else:
                    temp_terms[arg_index] = P[i]
            elif "C" in inner_term.symbol:
                if len(inner_term.symbol) > 4:
                    if i-1 < 0:
                        temp_terms[arg_index] = IV
                    else:
                        temp_terms[arg_index] = C[i-1]
                else:
                    if i < 0:
                        temp_terms[arg_index] = IV
                    else:
                        temp_terms[arg_index] = C[i]
            elif "IV" in inner_term.symbol:
                temp_terms[arg_index] = IV
        t.arguments = temp_terms
    return t




# Runs through a certain number of interactions between the oracle and the advesary
def MOEInteraction(chaining_function, num_interactions):
    """For num_interactions, have the advseary send a block to the oracle"""
    p = MOESession(chaining_function, schedule="end")
    p.rcv_start(1)
    for i in range(0, num_interactions - 1):
        p.rcv_block(1, Variable("x_" + str(i + 1)))
    return p.rcv_stop(1)


##
### Begin Tool
##

from xor.xorhelper import *
from xor.structure import *
from Unification.p_unif import p_unif
from Unification.p_syntactic import p_syntactic

def pairwise(xs) -> List[Equation]:
    """Return a list of equtions where terms are paired up from a list"""
    result = []
    for i, x in enumerate(xs):
        for y in xs[(i+1):]:
            result.append(Equation(x, y))
    return result

def unravel(t : Term, s : SubstituteTerm) -> Term:
    """Apply a substitution until you can't"""
    while t != t * s:
        t = t * s
    return t

def create_unification_problems(result : Frame) -> List[Equation]:
    """Return a list of pairwise equations from a frame"""
    result_range = result.subs.range()
    reduced_range = []
    for r in result_range:
        reduced_range.append(unravel(r, result.subs))
    return pairwise(reduced_range)


def any_unifiers(unifiers : List[SubstituteTerm]) -> bool:
    """Searches a list of unifiers to see if any of them have an entry"""
    if unifiers == False:
        return False
    """Added this if because for p_syntactic we get a single mgu not a list of mgu"""
    if isinstance(unifiers, SubstituteTerm):
        if len(unifiers) == 0:
            return False
        else:
            return True
    for u in unifiers:
        if len(u) > 0:
            return True
    return False

def MOE(unif_algo: Callable = p_unif, chaining: Callable = cipher_block_chaining,
        schedule: str = 'every', length_bound: int = 10, session_bound: int = 1,
        knows_iv: bool = True, moe_string: str = "none"):
    """Simulate an MOE interaction with specific parameters"""
    m = MOESession(chaining, schedule, moe_string)
    sid = 0
    m.rcv_start(sid)
    constraints: Dict[Variable, List[Term]] = dict()
    xor_zero = Zero()

    # Start interactions
    for i in range(1, length_bound + 1):
        x = Variable("x_" + str(i))

        # Update constraints
        if i == 1:
            constraints[x] = [m.nonces[sid][0], xor_zero] if knows_iv else [xor_zero]
        else:
            last_x = Variable("x_" + str(i - 1))
            constraints[x] = constraints[last_x] + [last_x] + [unravel(m.cipher_texts[sid][i - 2], m.subs[sid])]
        
        result = m.rcv_block(sid, x)
        # Try to find unifiers if schedule is every
        if schedule == "every":
            last_ciphertext = unravel(m.cipher_texts[sid][-1], m.subs[sid])
            for ciphertext in m.cipher_texts[sid][:-1]:
                ciphertext = unravel(ciphertext, m.subs[sid])
                print(ciphertext)
                if unif_algo == p_unif: # p_xor requires things in an Equations object
                    unifiers = unif_algo(Equations([Equation(last_ciphertext, ciphertext)]), constraints)
                else: # p_syntactic takes left_side, right_side, constraints
                    unifiers = unif_algo(last_ciphertext, ciphertext, constraints)
                # Return right away if we get a unifier
                if any_unifiers(unifiers):
                    return unifiers
    
    # Stop Interaction
    result = m.rcv_stop(sid)
    # If schedule is end then try to find unifiers now
    if schedule == "end":
        problems = create_unification_problems(result)
        for problem in problems:
            if unif_algo == p_unif:
                unifiers = unif_algo(Equations([problem]), constraints)
            else:
                unifiers = unif_algo(problem.left_side, problem.right_side, constraints)
            if any_unifiers(unifiers):
                return unifiers

    # If we got this far then no unifiers were found
    print("No unifiers found.")
