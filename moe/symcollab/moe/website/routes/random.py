"""
Webpage to generate and check cryptographic
modes of operation.
"""
from typing import List
from flask import request, Markup
from symcollab.algebra import Term
from symcollab.moe.filtered_generator import FilteredMOOGenerator
from symcollab.moe.custom import CustomMOO
from symcollab.moe.check import moo_check
from symcollab.moe.website import app
from .utils import unif_algo, restrict_to_range, render_moo_template

@app.route('/random', methods=['GET'])
def random():
    # If no arguments are supplied, present the page
    # without computing random terms.
    if len(request.args) == 0:
        return render_moo_template(
            'random.html',
            chaining="No",
            iv="No",
            bound=6,
            moenum=4,
            sectest="Yes",
        )

    # Grab parameters from URL
    chaining_required = request.args.get("chaining", "Yes") == "Yes"
    iv_required = request.args.get("iv", "Yes") == "Yes"
    invert_check = request.args.get('invert_check', "Yes") == "Yes"
    f_bound = int(request.args.get("bound", 1))
    security_required = request.args.get("sectest", "Yes") == "Yes"
    unif_choice = unif_algo.get(request.args.get('unif'))
    schedule = request.args.get('schedule')
    length_bound = restrict_to_range(
        int(request.form.get('length_bound', 1)),
        lower_bound=0,
        upper_bound=100
    )
    moo_bound = restrict_to_range(
        int(request.args.get("moenum", 1)),
        lower_bound=1,
        upper_bound=100
    )
    knows_iv = request.form.get('knows_iv') == "knows_iv"

    # Generate random modes of operation
    filtered_gen = FilteredMOOGenerator(
        max_history=1,
        max_f_depth=f_bound,
        requires_iv=iv_required,
        requires_chaining=chaining_required
    )
    #print("MOO Bound", moo_bound)
    moo_list = (next(filtered_gen) for i in range(moo_bound))
    response = "The follow MOO were tested:" + Markup("<br />")
    # Check security of the modes of operation
    moo_safe_list: List[Term] = list()
    for random_moo_term in moo_list:
        #print("Considering...", random_moo_term)
        response += Markup.escape(str(random_moo_term)) + Markup('<br />')
        cm = CustomMOO(random_moo_term)
        moo_result = moo_check(cm.name, schedule, unif_choice, length_bound, knows_iv, invert_check)
        if moo_result.secure:
            moo_safe_list.append(random_moo_term)

    # Communicate to the user the results
    #if len(moo_safe_list) == 0:
    #    response = "No Safe MOOs Found. The follow MOO were tested:" + Markup("<br />")
    #    response += format_term_list(moo_list)
    #else:
    #    response = "Safe MOOs Found. The following MOO(s) pass the security Test:" + Markup("<br />")
    #    response += format_term_list(moo_safe_list)
    
    
    response += "The following MOO(s) pass the security Test:" + Markup("<br />")
    response += format_term_list(moo_safe_list)

    return render_moo_template(
        'random.html',
        chaining="Yes" if chaining_required else "No",
        iv="Yes" if iv_required else "No",
        bound=f_bound,
        moenum=moo_bound,
        sectest="Yes" if security_required else "No",
        response=response
    )

def format_term_list(term_list: List[Term]) -> str:
    """Formats a list of terms to be readable through HTML"""
    text = ""
    for term in term_list:
        text += Markup.escape(str(term)) + Markup('<br />')
    return text
