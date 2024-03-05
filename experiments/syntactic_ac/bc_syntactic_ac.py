"""
Experiments for the Boudet
and Contejean paper
"""
from ac_benchmarks import benchmarks
from symcollab.Unification.syntactic_ac_unification import (
    synt_ac_unif, enable_recording, get_timings, set_verbose
)
from symcollab.Unification.equiv import syntactic_equal


SOLUTION_BOUND = 100

set_verbose(False)
enable_recording()

results = []

for benchmark in benchmarks:
    print("Running:", benchmark)
    solutions = synt_ac_unif(benchmark, SOLUTION_BOUND)
    timings = get_timings()
    assert len(solutions) == len(timings)
    results.append((solutions, timings))

# print(results)

UNIQUE_SOLUTION_BOUND = 20
results2 = []

print("Computing unique solutions...")
for j, (solutions, timings) in enumerate(results):
    assert len(solutions) >= 1 and len(timings) >= 1
    assert len(solutions) == len(timings)
    solutions_list = list(solutions)
    unique_solutions = [solutions_list[0]]
    unique_timings = [timings[0]]

    for i in range(1, len(solutions_list)):
        if all((not syntactic_equal(solutions_list[i], us) for us in unique_solutions)):
            unique_solutions.append(solutions_list[i])
            unique_timings.append(timings[i])
            if len(unique_solutions) >= UNIQUE_SOLUTION_BOUND:
                break
    
    if len(unique_solutions) < UNIQUE_SOLUTION_BOUND:
        print(f"[WARNING] Only {len(unique_solutions)} unique solutions found for benchmark problem {j}.")

    print(f"Time spent for one: {unique_timings[0]}")
    print(f"Time spent for all: {unique_timings[-1]}")
    results2.append((unique_solutions, unique_timings))

# print(results2)
