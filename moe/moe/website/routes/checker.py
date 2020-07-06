"""
Website for checking that cryptographic
modes of operation are secure.
"""
from functools import partial
from flask import request
from moe.website import app
from moe.check import moo_check
from Unification.p_unif import p_unif
from Unification.xor_rooted_unif import XOR_rooted_security
from .utils import format_substitutions, render_moo_template, unif_algo


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Web interface for the moo_check tool."""
    render_page = partial(render_moo_template, 'tool.html')
    if request.method != 'POST':
        return render_page()

    unif_choice = unif_algo.get(request.form.get('unif'))
    if unif_choice is None:
        return render_page(response="TRY AGAIN.")

    chaining_moo = request.form.get('chaining')
    if not _valid_unif_chaining(unif_choice, chaining_moo):
        return render_page(response="INVALID UNIFICATION AND CHAINING COMBO")

    # Verify security of the mode of operation.
    schedule = request.form.get('schedule')
    length_bound = _restrict_to_range(
        int(request.form.get('length_bound')),
        lower_bound=0,
        upper_bound=100
    )
    knows_iv = request.form.get('knows_iv') == "knows_iv"
    result = moo_check(chaining_moo, schedule, unif_choice, length_bound, knows_iv)
    response = format_substitutions(result) if result is not None else "NO UNIFIERS FOUND"
    return render_page(response=response)


def _restrict_to_range(x: int, lower_bound: int, upper_bound: int):
    """
    Takes an integer x and restricts its range by the following:
    - If x is above the upper_bound, make x the upper_bound.
    - If x is below the lower_bound, make x the lower_bound.
    - Otherwise leave x the same.
    """
    return min(max(x, lower_bound), upper_bound)


def _valid_unif_chaining(unif_choice, chaining_moo: str) -> bool:
    """
    Responds true if the unification algorithm chosen
    and the chaining method chosen are not compatible.
    """
    if unif_choice != p_unif and unif_choice != XOR_rooted_security:
        return True
    if unif_choice == p_unif:
        supported_chaining = ['cipher_block_chaining', 'propogating_cbc', 'hash_cbc']
    else: # XOR_rooted_security
        supported_chaining = ['cipher_feedback', 'output_feedback']
    return chaining_moo in supported_chaining
