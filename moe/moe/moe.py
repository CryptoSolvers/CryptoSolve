import sys
sys.path.append("..")

from algebra import *
from Unification import *
from xor import xor
from copy import deepcopy

# Note: This file isn't the most clear in terms of naming mostly since the requirements are not well understood
# As of December, I've attempted to outline the different functions and classes involved, 
# but likely these have changed by the time you read this.

# A frame is supposed to help you keep track with the interactions between an advesary and an oracle.
# The session id is what is used by the Oracle to keep track of the different messages
# The whole message can be recovered by apply the substition to the message. 
class Frame:
    def __init__(self, session_id : int, message : Term, subs):
        self.session_id = session_id
        self.message = message
        self.subs = subs
    def __str__(self):
        return "[" + str(self.session_id) + ", " + str(self.message) + ", " + str(self.subs) + "]"

# You can think of MOESession as an oracle of sorts.
# However, you have to create an oracle for every different chaining function and schedule that you want to use
# The API is largely taken from "Symbolic Security Criteria for Blockwise Adaptive Secure Modes of Encryption" by Catherine Meadows
class MOESession:
    def __init__(self, chaining_function, schedule : str = "every", custom_moe_string : str = ""):
        self.chaining_function = chaining_function
        self.schedule : str = schedule
        self.custom_moe_string : str = custom_moe_string
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
        self.sessions : List[int] = []
        # The below variables are dictionaries that are indexed by the session id
        self.subs : Dict[int, SubstituteTerm] = {}
        self.iteration : Dict[int, int] = {}
        # IV = Initialization Vector
        self.IV : Dict[int, Constant] = {}
        self.plain_texts : Dict[int, List[Term]] = {}
        self.cipher_texts : Dict[int, List[Term]] = {}
    
    def rcv_start(self, session_id : int):
        if session_id in self.sessions:
            raise ValueError("Session id %s already started" % (str(session_id)))
        self.sessions.append(session_id)
        # Initialize all the session variables
        self.subs[session_id] = SubstituteTerm()
        self.iteration[session_id] = 0
        self.plain_texts[session_id] = []
        self.cipher_texts[session_id] = []
        # TODO: IV should be a random nounce
        # Need to decide how to make it 'random'
        self.IV[session_id] = Constant("r")
    
    def send(self, session_id : int, encrypted_block : SubstituteTerm) -> Frame:
        return Frame(session_id, deepcopy(self.plain_texts[session_id][-1]), deepcopy(encrypted_block) )
    
    def rcv_stop(self, session_id : int) -> Optional[Frame]:
        subs = None
        if self.schedule == "end":
            subs = deepcopy(self.subs[session_id])
        # Remove information about the session from MOE
        del self.subs[session_id]
        del self.iteration[session_id]
        del self.plain_texts[session_id]
        del self.cipher_texts[session_id]
        self.sessions.remove(session_id)
        if self.schedule == "end":
            return self.send(session_id, subs)
        return None

    def rcv_block(self, session_id : int, message : Term) -> Optional[Frame]:
        self.iteration[session_id] += 1
        self.plain_texts[session_id].append(message)

        # Create new cipher text variable and map it to the MOE
        sub_var = Variable("y_" + str(self.iteration[session_id]))
        if(self.chaining_function == CustomMOE):
            encrypted_block = self.chaining_function(self, session_id, self.iteration[session_id], self.custom_moe_string)
        else:
             encrypted_block = self.chaining_function(self, session_id, self.iteration[session_id])
        self.subs[session_id].add(sub_var, encrypted_block)
        self.cipher_texts[session_id].append(sub_var)

        if self.schedule == "every":
            return self.send(session_id, self.subs[session_id])
        return None
    
    # Make sure the iteration number is valid for a given session
    def assertIteration(self, session_id : int, iteration : int):
        assert iteration <= len(self.plain_texts[session_id]) + 1 and iteration >= 0


##
# Modes of Encryptions (MOEs)
##

def CustomMOE(moe, session_id, iteration, moe_string : str):
    moe.assertIteration(session_id, iteration)
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    IV = moe.IV[session_id]
    parser = Parser()
    parser.add(Function("f", 1))
    parser.add(Function("xor", 2))
    parser.add(Variable("P[i]"))
    parser.add(Variable("C[i]"))
    parser.add(Variable("C[i-1]"))
    parser.add(Constant("IV"))
    parser.add(Constant("P[0]"))
    i = iteration - 1
    if i == 0:
        return parser.parse((moe_string.replace("C[i-1]", "IV")).replace("i", "0"))
    return parser.parse(moe_string)

def CipherBlockChaining(moe, session_id, iteration):
    """Cipher Block Chaining"""
    moe.assertIteration(session_id, iteration)
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    IV = moe.IV[session_id]
    f = Function("f", 1)
    i = iteration - 1
    if i == 0:
        return f(
            xor(P[0], IV)
        )
    return f(
        xor(P[i], C[i-1])
    )

def PropogatingCBC(moe, session_id, iteration):
    """Propogating Cipher Block Chaining"""
    moe.assertIteration(session_id, iteration)
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    IV = moe.IV[session_id]
    f = Function("f", 1)
    i = iteration - 1
    if i == 0:
        return f(
            xor(P[0], IV)
        )
    return f(
        xor(
            P[i],
            P[i - 1],
            C[i - 1]
        )
    )

def CipherFeedback(moe, session_id, iteration):
    """Cipher Feedback"""
    moe.assertIteration(session_id, iteration)
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    IV = moe.IV[session_id]
    i = iteration - 1
    f = Function("f", 1)
    if i == 0:
        return f(IV)
    return xor(
        f(C[i-1]), 
        P[i]
    )

# Questionable implementations...
# def OutputFeedback(moe, session_id, iteration):
#     """Output Feedback"""
#     moe.assertIteration(session_id, iteration)
#     P = moe.plain_texts[session_id]
#     i = iteration - 1
#     xor = Function("xor", 2)
#     f = Function("f", 1)
#     return xor(
#         f(OutputFeedback(moe, session_id, iteration - 1)), 
#         P[i]
#     )

# def CounterMode(moe, session_id, iteration):
#     """Counter Mode"""
#     moe.assertIteration(session_id, iteration)
#     P = moe.plain_texts[session_id]
#     C = moe.cipher_texts[session_id]
#     i = iteration - 1
#     xor = Function("xor", 2)
#     f = Function("f", 1)
#     return xor(
#         f(
#             xor(P[i], C[i-1])
#         ),
#         P[i - 1]
#     )

# Helper function for AccumulatedBlockCiper
def _calcQ(moe, session_id, i):
    P = moe.plain_texts[session_id]
    IV = moe.IV[session_id]
    h = Function("h", 1)
    if i == 0:
        return xor(
            P[0],
            h(IV)
        )
    return xor(
        P[i], 
        h(_calcQ(moe, session_id, i - 1))
    )

# C1 isn't defined yet
# def AccumulatedBlockCipher(moe, session_id, iteration):
#     """Accumulated Block Cipher"""
#     moe.assertIteration(session_id, iteration)
#     C = moe.cipher_texts[session_id]
#     f = Function("f", 1)
#     i = iteration - 2
#     Q = {}
#     Q[i] = _calcQ(moe, session_id, i)
#     Q[i-1] = _calcQ(moe, session_id, i - 1)
#     return xor(
#         f(
#             xor(Q[i], C[i - 1])
#         ),
#         Q[i - 1]
#     )


def HashCBC(moe, session_id, iteration):
    """Hash Cipher Block Chaining"""
    moe.assertIteration(session_id, iteration)
    IV = moe.IV[session_id]
    P = moe.plain_texts[session_id]
    C = moe.cipher_texts[session_id]
    f = Function("f", 1)
    h = Function("h", 1)
    i = iteration - 1
    if i == 0:
        return f(
            xor(
                h(IV),
                P[0]
            )
        )
    return f(
        xor(
            h(C[i - 1]),
            P[i]
        )
    )

# # Don't understand what the || symbol means
# def DoubleHashCBC(moe, session_id, iteration):
#     """Double Hash Cipher Block Chaining"""
#     moe.assertIteration(session_id, iteration)
#     IV = moe.IV[session_id]
#     P = moe.plain_texts[session_id]
#     C = moe.cipher_texts[session_id]
#     f = Function("f", 1)
#     h = Function("h", 1)
#     i = iteration - 2
#     if i == 0:
#         return f(
#             xor(
#                 h(IV), # || goes here
#                 P[0]
#             )
#         )
#     return f(
#         xor(
#             h(C[i-1]),
#             P[i]
#         )
#     )


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
    for u in unifiers:
        if len(u) > 0:
            return True
    return False

def MOE(unif = unif, chaining = CipherBlockChaining, schedule : str = 'every', length_bound : int = 10, session_bound : int = 1, knows_iv : bool = True):
    """Simulate an MOE interaction with specific parameters"""
    m = MOESession(chaining, schedule=schedule)
    sid = 0
    m.rcv_start(sid)
    constraints : Dict[Variable, List[Term]] = dict()
    xor_zero = Zero()

    # Start interactions
    for i in range(1, length_bound + 1):
        x = Variable("x_" + str(i))

        # Update constraints
        if i == 1:
            constraints[x] = [m.IV[sid], xor_zero] if knows_iv else [xor_zero]
        else:
            last_x = Variable("x_" + str(i - 1))
            constraints[x] = constraints[last_x] + [last_x] + [unravel(m.cipher_texts[sid][i - 2], m.subs[sid])]
        
        result = m.rcv_block(sid, x)
        # Try to find unifiers if schedule is every
        if schedule == "every":
            last_ciphertext = unravel(m.cipher_texts[sid][-1], m.subs[sid])
            for ciphertext in m.cipher_texts[sid][:-1]:
                ciphertext = unravel(ciphertext, m.subs[sid])
                if unif == p_unif: # p_xor requires things in an Equations object
                    unifiers = unif(Equations([Equation(last_ciphertext, ciphertext)]), constraints)
                else: # p_syntactic takes left_side, right_side, constraints
                    unifiers = unif(last_ciphertext, ciphertext, constraints)
                # Return right away if we get a unifier
                if any_unifiers(unifiers):
                    return unifiers
    
    # Stop Interaction
    m.rcv_stop(sid)
    # If schedule is end then try to find unifiers now
    if schedule == "end":
        problems = create_unification_problems(result)
        for problem in problems:
            if unif == p_unif:
                unifiers = unif(Equations([problem]), constraints)
            else:
                unifiers = unif(problem.left_side, problem.right_side, constraints)
            if any_unifiers(unifiers):
                return unifiers

    # If we got this far then no unifiers were found
    print("No unifiers found.")
