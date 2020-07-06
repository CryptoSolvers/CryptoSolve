"""
Different utility functions to make
displaying data easier.
"""
from functools import partial
from typing import List, Union
from flask import render_template, Markup
from algebra import SubstituteTerm
from Unification.unif import unif
from Unification.p_syntactic import p_syntactic
from Unification.ac_unif import ac_unify
from Unification.p_unif import p_unif
from Unification.xor_rooted_unif import XOR_rooted_security

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


render_moo_template = partial(render_template, title="MOO Tool", navigation=navigation)
