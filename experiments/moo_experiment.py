"""
Code for running experiments.
Able to pick up where it left off.
"""
from copy import deepcopy
from typing import Dict, Optional, Union
from symcollab.algebra import Term
from symcollab.moe import CustomMOO, MOOGenerator, moo_check
from symcollab.moe.check import MOOCheckResult
from symcollab.Unification.constrained.p_unif import p_unif
from symcollab.Unification.constrained.xor_rooted_unif import XOR_rooted_security
from symcollab.xor.xor import XorTerm
import os.path
import pickle
import signal
import sys
import traceback


# Save after checking x MOOs
SAVE_EVERY: int = 1
MOO_FILE = "saved_moo_experiments_v3.pickle"

last_mgen: Optional[MOOGenerator] = None
mgen: Optional[MOOGenerator] = None
moo_tested: Optional[Dict[Term, Union[MOOCheckResult, Exception]]] = None

print("MOO Save File:", MOO_FILE)

# Read current state from file if it exists
if os.path.isfile(MOO_FILE):
    print("Reading current state")
    with open(MOO_FILE, "rb") as reader:
        picked_state = reader.read()
        last_mgen, moo_tested = pickle.loads(picked_state)


if moo_tested is None:
    moo_tested = dict()

if last_mgen is None:
    last_mgen = MOOGenerator()

def save_current_state():
    """
    Saves current MOO Generator iterator and
    the dictionary of results
    """
    global last_mgen
    global moo_tested
    picked_state = pickle.dumps((last_mgen, moo_tested))
    with open(MOO_FILE, "wb") as writer:
        writer.write(picked_state)
    print("Saved:", MOO_FILE)




def sigint_handler(a, b):
    """
    Code that runs when an interrupt (CTRL-C) is
    received. It saves the current state of the
    MOO generator and MOOs tested.
    """
    print("Interrupt signal received. Saving current state...")
    save_current_state()
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)

i = 0
while True:
    mgen = deepcopy(last_mgen)
    t = next(mgen)
    print("Testing MOO", t, "... ",end="")
    tm = CustomMOO(t)

    try:
        if isinstance(t, XorTerm):
            check_result = moo_check(tm.name, 'every', XOR_rooted_security, 3, True, True)
        else:
            check_result = moo_check(tm.name, 'every', p_unif, 3, True, True)

        print(f"Secure: {check_result.secure}, Invertible: {check_result.invert_result}")
        moo_tested[t] = check_result

    except Exception as e:
        print("FAIL")
        print(traceback.format_exc())
        moo_tested[t] = e

    i += 1
    if i == SAVE_EVERY:
        save_current_state()
        i = 0

    last_mgen = mgen
