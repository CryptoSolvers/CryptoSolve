"""
Website for checking that cryptographic
modes of operation are secure.
"""
from functools import partial
from flask import request
from symcollab.moe.website import app
from symcollab.moe.check import moo_check
from .utils import format_substitutions, render_moo_template, \
    restrict_to_range, unif_algo, valid_moo_unif_pair


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Web interface for the moo_check tool."""
    render_page = partial(render_moo_template, 'checker.html')
    if request.method != 'POST':
        return render_page()

    unif_choice = unif_algo.get(request.form.get('unif'))
    if unif_choice is None:
        return render_page(response="TRY AGAIN.")

    chaining_moo = request.form.get('chaining')
    if not valid_moo_unif_pair(chaining_moo, unif_choice):
        return render_page(response="INVALID UNIFICATION AND CHAINING COMBO")

    # Verify security of the mode of operation.
    schedule = request.form.get('schedule')
    length_bound = restrict_to_range(
        int(request.form.get('length_bound')),
        lower_bound=0,
        upper_bound=100
    )
    knows_iv = request.form.get('knows_iv') == "knows_iv"
    invert_check = request.form.get('invert_check') == "invert_check"
    result = moo_check(chaining_moo, schedule, unif_choice, length_bound, knows_iv, invert_check)
    response = ""
    if result.secure:
        response = "MOO IS SECURE: "
        if result.syntactic_result:
            response += "PASSES SYNTACTIC CHECK"
        else:
            response += "NO UNIFIERS FOUND"
    else:
        response = "MOO IS INSECURE. COLLISION WITH SUBSTITUTION(S) " + \
            format_substitutions(result.collisions)
    if result.invert_result:
        response += ", MOO is Invertible"
    else:
        response += ", MOO may not be Invertible"
    return render_page(response=response)
