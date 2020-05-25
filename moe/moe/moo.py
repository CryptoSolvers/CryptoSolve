"""
This module contains Modes of Operations
that can be used by the MOO-Program.
"""
from algebra import Function
from xor import xor

__all__ = ['cipher_block_chaining', 'propogating_cbc', 'hash_cbc', 'cipher_feedback']

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



# Questionable implementations...
# def output_feedback(iteration, nonces, P, C):
#     """Output Feedback"""
#     i = iteration - 1
#     f = Function("f", 1)
#     return xor(
#         f(output_feedback(iteration - 1, nonces, P, C)), 
#         P[i]
#     )

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
# def double_hash_cbc(iteration, nonces, P, C):
#     """Double Hash Cipher Block Chaining"""
#     IV = nonces[0]
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
