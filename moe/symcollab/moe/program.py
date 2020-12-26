"""
This module contains the interaction between
an oracle and an adversary formalized by a
MOOProgram.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, List, Optional
from symcollab.algebra import Constant, Term, SubstituteTerm, Variable
from .schedule import MOO_Schedule
from .moo import MOO

__all__ = ['MOOFrame', 'MOOProgram']

@dataclass
class MOOFrame:
    """
    Used by the MOOProgram to contain information about the ciphertext,
    and the substitutions we know about the older ciphertexts.
    """
    message: Term
    substitutions: SubstituteTerm
    
    def __str__(self):
        return str(self.substitutions)

class MOOProgram:
    """
    Describes an interaction between the advesary and the oracle in
    which the advesary sends blocks of plaintext to be encrypted
    and the oracle sends back blocks of ciphertext according
    to some fixed schedule defined by the mode of operation.
    """
    def __init__(self, moo_name: str, schedule_name: str = 'every'):
        chaining_function = MOO.find(moo_name)
        if chaining_function is None:
            raise ValueError(f"Mode of operation {moo_name} is not found.")
        self.chaining_function: Callable = chaining_function

        schedule = MOO_Schedule.find(schedule_name)
        if schedule is None:
            raise ValueError(f"Schedule of name {schedule_name} is not found.")
        self.schedule: Callable = schedule

        self.substitutions: SubstituteTerm = SubstituteTerm()
        self.iteration: int = 0
        # TODO: Maybe consider generating a uuid for the IV, so that
        # it is different across sessions?
        self.nonces: List[Constant] = [Constant("IV")]
        self.plain_texts: List[Term] = list()
        self.cipher_texts: List[Term] = list()
        self.stopped = False

    def rcv_stop(self) -> MOOFrame:
        """
        Advesary's message to the oracle
        that it is done sending plaintext blocks.
        """
        self.stopped = True
        return MOOFrame(
            deepcopy(self.cipher_texts[-1]),
            deepcopy(self.substitutions)
        )

    def rcv_block(self, message: Term) -> Optional[MOOFrame]:
        """
        The adversary gives a plaintext block to the oracle to encrypt.
        Depending on the schedule, the oracle might return back a MOOFrame.
        """
        if self.stopped:
            raise ValueError("Session already stopped.")
        self.iteration += 1
        self.plain_texts.append(message)

        # Create new cipher text variable and map it to the MOO Term
        new_cipher_var = Variable(f"y_{self.iteration}")
        encrypted_block = self.chaining_function(
            self.iteration,
            self.nonces,
            self.plain_texts,
            self.cipher_texts
        )
        self.substitutions.add(new_cipher_var, encrypted_block)
        self.cipher_texts.append(new_cipher_var)

        # If the schedule allows, return a MOO Frame
        if self.schedule(self.iteration):
            return MOOFrame(
                deepcopy(new_cipher_var),
                deepcopy(self.substitutions)
            )
        return None
