"""
Different utility functions to make
displaying data easier.
"""
from functools import partial
from typing import List, Union
from flask import render_template, Markup
from symcollab.algebra import SubstituteTerm
from symcollab.Unification.unif import unif
from symcollab.Unification.p_syntactic import p_syntactic
from symcollab.Unification.ac_unif import ac_unify
from symcollab.Unification.p_unif import p_unif
from symcollab.Unification.xor_rooted_unif import XOR_rooted_security

navigation = [
    dict(href='/', caption='Tool'),
    dict(href='/program', caption='Simulation'),
    dict(href='/custom', caption='Custom'),
    dict(href='/random', caption='Random')
]

unif_algo = dict(
    unif=unif,
    ac_unify=ac_unify,
    p_unif=p_unif,
    p_syntactic=p_syntactic,
    xor_rooted_security=XOR_rooted_security
)

def format_substitutions(subs: Union[SubstituteTerm, List[SubstituteTerm]]):
    """
    Create a nicely formatted HTML representation of a singular or list of
    substitutions.
    """
    text = ""
    if isinstance(subs, SubstituteTerm):
        term_str = str(subs)
        for line in term_str.split('\n'):
            text += Markup.escape(line) + Markup('<br />')
        text += Markup('<br />')
        return text
    for term in subs:
        term_str = str(term)
        for line in term_str.split('\n'):
            text += Markup.escape(line) + Markup('<br />')
        text += Markup('<br />')
    return text

def restrict_to_range(x: int, lower_bound: int, upper_bound: int):
    """
    Takes an integer x and restricts its range by the following:
    - If x is above the upper_bound, make x the upper_bound.
    - If x is below the lower_bound, make x the lower_bound.
    - Otherwise leave x the same.
    """
    return min(max(x, lower_bound), upper_bound)


def valid_moo_unif_pair(moo_string: str, unif_choice) -> bool:
    """
    Responds true if the unification algorithm chosen
    and the mode of operation chosen are compatible.
    """
    if unif_choice != p_unif and unif_choice != XOR_rooted_security:
        return True
    if unif_choice == p_unif:
        supported_chaining = ['cipher_block_chaining', 'propogating_cbc', 'hash_cbc']
    else: # XOR_rooted_security
        supported_chaining = ['cipher_feedback', 'output_feedback']
    return moo_string in supported_chaining


render_moo_template = partial(render_template, title="MOO Tool", navigation=navigation)
