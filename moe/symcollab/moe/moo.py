"""
This module contains Modes of Operations
that can be used by the MOO-Program.
"""
from symcollab.algebra import Function
from symcollab.xor import xor
from .callable_registry import CallableRegistry

__all__ = ['MOO']

MOO = CallableRegistry(enforce_arity=4)

@MOO.register('cipher_block_chaining')
def cipher_block_chaining(iteration, nonces, P, C):
    """Cipher Block Chaining"""
    IV = nonces[0]
    f = Function("f", 1)
    i = iteration - 1
    if i == 0:
        return f(
            xor(P[0], IV)
        )
    return f(
        xor(P[i], C[i-1])
    )

@MOO.register('propogating_cbc')
def propogating_cbc(iteration, nonces, P, C):
    """Propogating Cipher Block Chaining"""
    IV = nonces[0]
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

@MOO.register('hash_cbc')
def hash_cbc(iteration, nonces, P, C):
    """Hash Cipher Block Chaining"""
    IV = nonces[0]
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

@MOO.register('cipher_feedback')
def cipher_feedback(iteration, nonces, P, C):
    """Cipher Feedback"""
    IV = nonces[0]
    i = iteration - 1
    f = Function("f", 1)
    if i == 0:
        return f(IV)
    return xor(
        f(C[i-1]),
        P[i]
    )

@MOO.register('output_feedback')
def output_feedback(iteration, nonces, P, _):
    """Output Feedback"""
    IV = nonces[0]
    i = iteration - 1
    f = Function("f", 1)
    keystream = f(IV)
    for _ in range(i):
        keystream = f(keystream)
    return xor(P[i], keystream)
    
    
# Helper function for AccumulatedBlockCiper with h identity
def _calcQI(i, nonces, P, C):
    h = Function("h", 1)
    if i == 0:
        return P[0]
    return xor(
        P[i],
        h(_calcQI(i - 1, nonces, P, C))
    )    

#Error in the Def? What is Y_0? Need to ask Cathy.
#Accumulated Block Cipher but with h as identity
@MOO.register('abc_h_identity')
def abc_h_identity(iteration, nonces, P, C):
    """ABC H IDENTITY"""
    IV = nonces[0]
    i = iteration - 1
    f = Function("f", 1)
    Q = {}
    if i > 0:
        Q[i] = _calcQI(i, nonces, P, C)
        Q[i-1] = _calcQI(i - 1, nonces, P, C)
    
    keystream = f(IV)
    if i == 0:
        return IV
    return xor(f(xor(Q[i], C[i-1])),Q[i-1])

# Implementations we haven't developed theory around yet...
# Also the commented out implementations are questionable.
# @MOO.register('counter_mode')
# def counter_mode(iteration, nonces, P, C):
#     """Counter Mode"""
#     i = iteration - 1
#     f = Function("f", 1)
#     return xor(
#         f(
#             xor(P[i], C[i-1])
#         ),
#         P[i - 1]
#     )

# Helper function for AccumulatedBlockCiper
# def _calcQ(i, nonces, P, C):
#     IV = nonces[0]
#     h = Function("h", 1)
#     if i == 0:
#         return xor(
#             P[0],
#             h(IV)
#         )
#     return xor(
#         P[i],
#         h(_calcQ(i - 1, nonces, P, C))
#     )

# # C1 isn't defined yet
# @MOO.register('accumulated_block_cipher')
# def accumulated_block_cipher(iteration, nonces, P, C):
#     """Accumulated Block Cipher"""
#     f = Function("f", 1)
#     i = iteration - 2
#     Q = {}
#     Q[i] = _calcQ(i, nonces, P, C)
#     Q[i-1] = _calcQ(i - 1, nonces, P, C)
#     return xor(
#         f(
#             xor(Q[i], C[i - 1])
#         ),
#         Q[i - 1]
#     )

# # Don't understand what the || symbol means
# @MOO.register('double_hash_cbc')
# def double_hash_cbc(iteration, nonces, P, C):
#     """Double Hash Cipher Block Chaining"""
#     IV = nonces[0]
#     f = Function("f", 1)
#     h = Function("h", 1)
#     i = iteration - 2
#     if i == 0:
#         return f(
#             xor(
#                 h(IV), # || (concatenation) goes here
#                 P[0]
#             )
#         )
#     return f(
#         xor(
#             h(C[i-1]),
#             P[i]
#         )
#     )
