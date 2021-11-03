"""
Reads the experiment state and provide some summary statistics
"""
from collections import defaultdict, Counter
from enum import Enum
from typing import Dict, Optional
from symcollab.algebra import depth, Term
from symcollab.moe.check import MOOCheckResult
import os.path
import pickle

MOO_FILE = "1.pickle"

moo_tested: Optional[Dict[Term, Optional[MOOCheckResult]]] = None

# Read current state from file if it exists
if os.path.isfile(MOO_FILE):
    print("Reading file:", MOO_FILE)
    with open(MOO_FILE, "rb") as reader:
        picked_state = reader.read()
        _, moo_tested = pickle.loads(picked_state)
else:
    print(f"No save file '{MOO_FILE}' exists.")

if moo_tested is None:
    moo_tested = dict()

class SecurityResult(Enum):
    PASS = 1
    FAIL = 2
    UNKNOWN = 3
    RECURSION_ERROR = 4
    TYPE_ERROR = 5

# Gather statistics on whether MOOs are
# secure based on depth level
depth_statistics = defaultdict(Counter)

for moo, result in moo_tested.items():
    moo_depth = depth(moo)
    moo_result = SecurityResult.UNKNOWN
    if isinstance(result, MOOCheckResult):
        moo_result = SecurityResult.PASS if result.secure else SecurityResult.FAIL
    if isinstance(result, RecursionError):
        moo_result = SecurityResult.RECURSION_ERROR
    if isinstance(result, TypeError):
        moo_result = SecurityResult.TYPE_ERROR
    depth_statistics[moo_depth][moo_result] += 1

for depth in depth_statistics:
    print("Depth:", depth)
    print(depth_statistics[depth])
    print("=================")


# Print MOOs that we found are secure
print("")
print("SECURE MOOS:")
for moo, result in moo_tested.items():
    if isinstance(result, MOOCheckResult) and result.secure:
        print(moo)

# Print MOOs that triggered a RecursionError
print("")
print("RECURSION ERROR MOOS:")
for moo, result in moo_tested.items():
    if isinstance(result, RecursionError):
        print(moo)

print("")
print("MOOS THAT NEEDED MORE THAN 3 ITERATIONS TO SHOW COLLISION")
for moo, result in moo_tested.items():
    if isinstance(result, MOOCheckResult) and not result.secure:
        if result.iterations_needed > 3:
            print(moo)
