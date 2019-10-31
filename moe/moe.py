import sys
sys.path.append("..")

from algebra import *
from xor import xor
from copy import deepcopy

class Frame:
    def __init__(self, session_id : int, message : Term, subs):
        self.session_id = session_id
        self.message = message
        self.subs = subs
    def __str__(self):
        return "[" + str(self.session_id) + ", " + str(self.message) + ", " + str(self.subs) + "]"

class MOESession:
    def __init__(self, chaining_function, schedule : str = "every"):
        self.chaining_function = chaining_function
        self.schedule : str = schedule
        self.sessions : List[int] = []
        self.subs : Dict[int, SubstituteTerm] = {}
        self.iteration : Dict[int, int] = {}
        self.IV : Dict[int, Constant] = {}
        self.plain_texts : Dict[int, List[Term]] = {}
        self.cipher_texts : Dict[int, List[Term]] = {}
    
    def rcv_start(self, session_id : int):
        if session_id in self.sessions:
            raise ValueError("Session id %s already started" % (str(session_id)))
        self.sessions.append(session_id)
        self.subs[session_id] = SubstituteTerm()
        self.iteration[session_id] = 0
        self.plain_texts[session_id] = []
        self.cipher_texts[session_id] = []
        self.IV[session_id] = Constant("r")
    
    def send(self, session_id : int, encrypted_block : SubstituteTerm) -> Frame:
        return Frame(session_id, deepcopy(self.plain_texts[session_id][-1]), deepcopy(encrypted_block) )
    
    def rcv_stop(self, session_id : int) -> Optional[Frame]:
        if self.schedule == "end":
            return self.send(session_id, self.subs[session_id])
        # Remove information about the session from MOE
        del self.subs[session_id]
        del self.iteration[session_id]
        del self.plain_texts[session_id]
        del self.cipher_texts[session_id]
        return None

    def rcv_block(self, session_id : int, message : Term) -> Optional[Frame]:
        self.iteration[session_id] += 1
        self.plain_texts[session_id].append(message)
        encrypted_block = self.chaining_function(self, session_id, self.iteration[session_id])
        sub_var = Variable("y_" + str(self.iteration[session_id]))
        self.subs[session_id].add(sub_var, encrypted_block)
        self.cipher_texts[session_id].append(sub_var)
        if self.schedule == "every":
            return self.send(session_id, self.subs[session_id])
        return None
    
    def assertIteration(self, session_id : int, iteration : int):
        assert iteration <= len(self.plain_texts[session_id]) + 1 and iteration >= 0


def CipherBlockChaining(moe, session_id, iteration):
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
# def AccumulatedBlockCiper(moe, session_id, iteration):
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


def MOEInteraction(chaining_function, num_interactions):
    p = MOESession(chaining_function, schedule="end")
    p.rcv_start(1)
    for i in range(0, num_interactions - 1):
        p.rcv_block(1, Variable("x_" + str(i + 1)))
    return p.rcv_stop(1)