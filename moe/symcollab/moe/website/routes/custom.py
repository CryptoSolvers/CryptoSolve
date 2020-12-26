"""
Webpage for checking that user supplied
cryptographic modes of operation are secure.
"""
from functools import partial
from flask import request
from symcollab.algebra import Variable, Function, Constant, Parser, Term, FuncTerm
from symcollab.moe.website import app
from symcollab.moe.check import moo_check
from symcollab.moe.custom import CustomMOO
from symcollab.Unification.p_unif import p_unif
from symcollab.Unification.xor_rooted_unif import XOR_rooted_security
from symcollab.xor import xor
from .utils import format_substitutions, render_moo_template, \
    restrict_to_range, unif_algo

@app.route('/custom', methods=['GET', 'POST'])
def custom():
    """
    A way to check a custom mode of operation
    for security.
    """
    render_page = partial(render_moo_template, 'custom.html')
    if request.method != 'POST':
        return render_page()

    unif_choice = unif_algo.get(request.form.get('unif'))
    if unif_choice is None:
        return render_page(response="TRY AGAIN.")

    chaining_moo = _temporary_parser(request.form.get('cmoe'))
    if not _valid_moo_unif_pair(chaining_moo, unif_choice):
        return render_page(response="INVALID UNIFICATION AND CHAINING COMBO")

    registered_moo = CustomMOO(chaining_moo)

    schedule = request.form.get('schedule')
    length_bound = restrict_to_range(
        int(request.form.get('length_bound')),
        lower_bound=0,
        upper_bound=100
    )
    knows_iv = request.form.get('knows_iv') == "knows_iv"
    invert_check = request.form.get('invert_check') == "invert_check"
    result = moo_check(registered_moo.name, schedule, unif_choice, length_bound, knows_iv, invert_check)
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

# TODO: Replace with a more robust parser
def _temporary_parser(moo_string: str) -> Term:
    """
    A temporary parser to parse a user
    supplied cryptographic mode of operation.
    This function is limited in what it can parse.
    """
    parser = Parser()
    parser.add(Function("f", 1))
    parser.add(xor)
    parser.add(Variable("P[i]"))
    parser.add(Variable("C[i]"))
    parser.add(Variable("C[i-1]"))
    parser.add(Constant("r"))
    parser.add(Constant("P[0]"))
    return parser.parse(moo_string)

def _valid_moo_unif_pair(moo: Term, unif_choice) -> bool:
    """
    Responds true if the unification algorithm chosen
    and the chaining method chosen are compatible.
    """
    if unif_choice != p_unif and unif_choice != XOR_rooted_security:
        return True
    if not isinstance(moo, FuncTerm) or moo.function.arity < 1:
        return False
    if unif_choice == p_unif:
        return moo.function == Function("f", 1)
    # XOR_rooted_security
    return moo.function == xor
