"""
Experiments for the
new syntactic ac algorithm
by K Cornell, A.M Marshall
and B Rozek.
"""
from ac_benchmarks import benchmarks
from symcollab.Unification.syntactic_ac_unif_2 import (
    synt_ac_unif2, enable_recording, get_timings, set_verbose
)

SOLUTION_BOUND = 100

set_verbose(False)
enable_recording()

results = []

for benchmark in benchmarks:
    print("Running:", benchmark)
    solutions = synt_ac_unif2(benchmark, SOLUTION_BOUND)
    timings = get_timings()
    assert len(solutions) == len(timings)
    results.append((solutions, timings))

print(results)

# TODO: Post-hoc filter of results until we get to 20 unique
# solutions