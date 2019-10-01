import sys
sys.path.append("..")

from algebra import *
from xor import xor
from copy import deepcopy

class Frame:
    def __init__(self, session_id, message, subs):
        self.session_id = session_id
        self.message = message
        self.subs = subs
    def __str__(self):
        return "[" + str(self.session_id) + ", " + str(self.message) + ", " + str(self.subs) + "]"

class PRR:
    def __init__(self, chaining_function, schedule = "every"):
        self.chaining_function = chaining_function
        self.schedule = schedule
        self.sessions = []
        self.subs = {}
        self.iteration = {}
        self.plain_texts = {}
        self.cipher_texts = {}
    
    def rcv_start(self, session_id):
        if session_id in self.sessions:
            raise ValueError("Session id %s already started" % (str(session_id)))
        self.sessions.append(session_id)
        self.subs[session_id] = SubstituteTerm()
        self.iteration[session_id] = 0
        self.plain_texts[session_id] = []
        self.cipher_texts[session_id] = []
    
    def send(self, session_id, encrypted_block):
        return Frame(session_id, deepcopy(self.plain_texts[session_id][-1]), deepcopy(encrypted_block) )
    
    def rcv_stop(self, session_id):
        if self.schedule == "end":
            return self.send(session_id, self.subs[session_id])
        # Remove information about the session from PRR
        del self.subs[session_id]
        del self.iteration[session_id]
        del self.plain_texts[session_id]
        del self.cipher_texts[session_id]

    def rcv_block(self, session_id, message):
        self.iteration[session_id] += 1
        self.plain_texts[session_id].append(message)
        if self.iteration[session_id] == 1:
            self.subs[session_id].add(Variable("y_1"), message)
        else:
            encrypted_block = self.chaining_function(self, session_id, self.iteration[session_id])
            self.cipher_texts[session_id].append(encrypted_block)
            self.subs[session_id].add(Variable("y_" + str(self.iteration[session_id])), encrypted_block)
            if self.schedule == "every":
                return self.send(session_id, self.subs[session_id])
    
    def assertIteration(self, session_id, iteration):
        assert iteration <= len(self.plain_texts[session_id]) and iteration >= 0


def CipherBlockChaining(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    P = prr.plain_texts[session_id]
    C = prr.cipher_texts[session_id]
    f = Function("f", 1)
    i = iteration - 1
    if i == 1:
        return f(
            xor(P[1], P[0])
        )
    return f(
        xor(P[i], C[i-2])
    )


def PropogatingCBC(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    P = prr.plain_texts[session_id]
    C = prr.cipher_texts[session_id]
    f = Function("f", 1)
    i = iteration - 1 
    if i == 1:
        return f(
            xor(P[1], P[0])
        )
    return f(
        xor(
            P[i],
            P[i - 1],
            C[i - 2]
        )
    )


def CipherFeedback(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    P = prr.plain_texts[session_id]
    C = prr.cipher_texts[session_id]
    i = iteration - 1
    f = Function("f", 1)
    if i == 1:
        return f(P[0])
    return xor(
        f(C[i-2]), 
        P[i]
    )

# Questionable implementations...
# def OutputFeedback(prr, session_id, iteration):
#     prr.assertIteration(session_id, iteration)
#     P = prr.plain_texts[session_id]
#     i = iteration - 1
#     xor = Function("xor", 2)
#     f = Function("f", 1)
#     return xor(
#         f(OutputFeedback(prr, session_id, iteration - 1)), 
#         P[i]
#     )

# def CounterMode(prr, session_id, iteration):
#     prr.assertIteration(session_id, iteration)
#     P = prr.plain_texts[session_id]
#     C = prr.cipher_texts[session_id]
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
def _calcQ(prr, session_id, i):
    P = prr.plain_texts[session_id]
    h = Function("h", 1)
    if i == 1:
        return xor(
            P[1],
            h(P[0])
        )
    return xor(
        P[i], 
        h(_calcQ(prr, session_id, i - 1))
    )

def AccumulatedBlockCiper(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    C = prr.cipher_texts[session_id]
    f = Function("f", 1)
    i = iteration - 1
    Q = {}
    Q[i] = _calcQ(prr, session_id, i)
    Q[i-1] = _calcQ(prr, session_id, i - 1)
    return xor(
        f(
            xor(Q[i], C[i - 2])
        ),
        Q[i - 1]
    )


def HashCBC(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    P = prr.plain_texts[session_id]
    C = prr.cipher_texts[session_id]
    f = Function("f", 1)
    h = Function("h", 1)
    i = iteration - 1
    if i == 1:
        return f(
            xor(
                h(P[0]),
                P[1]
            )
        )
    return f(
        xor(
            h(C[i - 2]),
            P[i]
        )
    )

def DoubleHashCBC(prr, session_id, iteration):
    prr.assertIteration(session_id, iteration)
    P = prr.plain_texts[session_id]
    C = prr.cipher_texts[session_id]
    f = Function("f", 1)
    h = Function("h", 1)
    i = iteration - 1
    if i == 1:
        return f(

        )
    return f(
        xor(
            h(C[i-2]),
            P[i]
        )
    )


def PRRInteraction(chaining_function, num_interactions):
    p = PRR(chaining_function, schedule="end")
    p.rcv_start(1)
    p.rcv_block(1, Constant("r"))
    for i in range(1, num_interactions + 1):
        p.rcv_block(1, Variable("x_" + str(i)))
    return p.rcv_stop(1)