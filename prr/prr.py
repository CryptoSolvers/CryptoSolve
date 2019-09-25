import sys
sys.path.append("..")

from algebra import *
from copy import deepcopy

class PRR:
    def __init__(self, session_id, initial_nounce, chaining_function, schedule = "every"):
        self.session_id = session_id
        self.initial_nounce = initial_nounce
        self.chaining_function = chaining_function
        self.subs = SubstituteTerm()
        self.iteration = 1
        self.schedule = schedule
        self.subs.add(Variable("y_" + str(self.iteration)), self.initial_nounce)
        self.plain_texts = []
        self.cipher_texts = [self.initial_nounce]

    def send(self, message):
        self.plain_texts.append(message)
        new_term = self.chaining_function(self, self.iteration)
        self.cipher_texts.append(new_term)
        self.iteration = self.iteration + 1
        self.subs.add(Variable("y_" + str(self.iteration)), new_term)
        if self.schedule == "every":
            return [self.session_id, message, deepcopy(self.subs)]
    
    def assertIteration(self, iteration):
        assert iteration <= len(self.plain_texts) and iteration <= len(self.cipher_texts) and iteration >= 0


def CipherBlockChaining(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    return f(
        xor(P[i], C[i])
    )


def PropogatingCBC(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    return f(
        xor(
            xor(P[i], P[i-1]), 
            C[i]
        )
    )


def CipherFeedback(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    return xor(f(C[i]), P[i])

def OutputFeedback(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    return xor(
        f(OutputFeedback(prr, iteration - 1)), 
        P[i]
    )

def CounterMode(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    return xor(
        f(
            xor(P[i], C[i])
        ),
        P[i - 1]
    )

# Helper function for AccumulatedBlockCiper
def _calcQ(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    i = iteration - 1
    xor = Function("xor", 2)
    h = Function("h",1)
    if iteration == 1:
        return xor(
            P[0],
            h(prr.initial_nounce)
        )
    else:
        return xor(
            P[i], 
            h(_calcQ(prr, iteration - 1))
        )

def AccumulatedBlockCiper(prr, iteration):
    prr.assertIteration()
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    Q = _calcQ(prr, iteration)
    return xor(
        f(
            xor(Q, C[i])
        ),
        _calcQ(prr, iteration - 1)
    )


def HashCBC(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    h = Function("h",1)
    return f(
        xor(
            h(C[i]),
            P[i]
        )
    )

def DoubleHashCBC(prr, iteration):
    prr.assertIteration()
    P = prr.plain_texts
    C = prr.cipher_texts
    i = iteration - 1
    xor = Function("xor", 2)
    f = Function("f", 1)
    h = Function("h",1)
    return f(
        xor(
            h(C[i]),
            P[i]
        )
    )
