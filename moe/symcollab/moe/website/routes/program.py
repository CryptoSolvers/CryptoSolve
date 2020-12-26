"""
Website that walks through the interactions in a
MOO Program.
"""
from typing import Dict
from uuid import uuid4
from flask import request, session
from symcollab.moe.program import MOOProgram
from symcollab.moe.website import app
from symcollab.algebra import Variable
from .utils import render_moo_template

@app.route('/program', methods=['GET', 'POST'])
def program():
    """
    Webpage that walks the user through an interaction between
    the adversary and the oracle.
    """
    if request.method != "POST":
        # If you step away from the simulation, destroy the previous session
        if 'uid' in session and session['uid'] in moo_sessions.keys():
            del moo_sessions[session['uid']]
            session.pop('uid', None)
        return render_moo_template('program_create.html')

    # If a MOOProgram is already in session....
    if 'uid' in session and session['uid'] in moo_sessions.keys():
        uid = session['uid']
        moo_session: MOOProgram = moo_sessions[uid]
        if 'next' in request.form:
            plaintext = Variable("x_" + str(moo_session.iteration))
            ciphertext = moo_session.rcv_block(plaintext)
            response = str(ciphertext) if ciphertext is not None else "Sent " + str(plaintext)
            return render_moo_template('program.html', response=response)
        if 'end' in request.form:
            ciphertext = moo_session.rcv_stop()
            del moo_sessions[uid]
            session.pop('uid', None)
            response = str(ciphertext) if ciphertext is not None else None
            if response is None:
                return render_moo_template('program_create.html')
            return render_moo_template('program.html', response=response)

    # If we are creating a session of a MOOProgram....
    if 'chaining' in request.form and 'schedule' in request.form:
        # Create new session
        chaining_moo = request.form.get('chaining')
        schedule = request.form.get('schedule')
        moo_session = MOOProgram(chaining_moo, schedule)
        # Send an initial message
        plaintext = Variable("x_" + str(moo_session.iteration))
        ciphertext = moo_session.rcv_block(plaintext)
        # Set up a userid and save the moo_session
        session['uid'] = uuid4()
        moo_sessions[session['uid']] = moo_session
        response = str(ciphertext) if ciphertext is not None else "Sent " + str(plaintext)
        return render_moo_template('program.html', response=response)

    return render_moo_template('program_create.html')

moo_sessions: Dict[str, MOOProgram] = dict()
