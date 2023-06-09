"""
Module used to create custom modes of operation.
"""
from typing import List, Optional
from symcollab.algebra import Constant, get_vars, SubstituteTerm, Term
from .moo import MOO

__all__ = ['CustomMOO']

class CustomMOO:
    """
    Create and register a custom mode of operation from a term.
    
    Parameters
    ----------
    term: Term 
        Term representing the recursive definition
        of a mode of operation
    
    moo_name: Optional[str]
        Name to associate with this custom mode of operation.
        By default, it names it based on the string that the
        term produces.

    Examples
    --------
    >>> P = Variable("P[i]")
    >>> C1 = Variable("C[i-1]")
    >>> f = Function("f", 1)
    >>> t = xor(f(xor(P, f(C1))), f(C1))
    >>> tm = CustomMOO(t)
    >>> M=moo_check(tm.name, 'every', XOR_rooted_security, 3, True, True)
    """
    def __init__(self, term: Term, moo_name: Optional[str] = None):
        self.term = term
        self.name = str(term) if moo_name is None else moo_name
        MOO.register(self.name, self.__call__)

    def __call__(self, iteration: int, nonces: List[Constant],
                 P: List[Term], C: List[Term]):
        IV = nonces[0]
        i = iteration - 1
        # Create substitution between symbolic plain and cipher texts
        # and the symbolic instantiations of them in MOOProgram
        sigma = SubstituteTerm()
        subterms = get_vars(self.term)
        for subterm in subterms:
            if subterm.symbol[0] == "P":
                if '-' not in subterm.symbol:
                    # Assume we mean current plaintext
                    sigma.add(subterm, P[-1])
                else:
                    j = int(subterm.symbol[4:-1])
                    if j > i:
                        # If we request for a cipher block that doesn't exist yet
                        # due to the current session length
                        # then map the subterm to a different nounce
                        #sigma.add(subterm, Constant(IV.symbol + f"_{j}"))
                        sigma.add(subterm, Constant(IV.symbol))
                    else:
                        sigma.add(subterm, P[-j])
            elif subterm.symbol[0] == "C":
                j = int(subterm.symbol[4:-1])
                if j > i:
                    # If we request for a cipher block that doesn't exist yet
                    # due to the current session length
                    # then map the subterm to a different nounce
                    #sigma.add(subterm, Constant(IV.symbol + f"_{j}"))
                    sigma.add(subterm, Constant(IV.symbol))
                else:
                    sigma.add(subterm, C[-j])
        return self.term * sigma
