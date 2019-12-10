from moe.website import app
from moe import *
from Unification import *
from Unification.p_unif import p_unif
from algebra import *
from flask import request, render_template, session, Markup
from typing import Dict
from uuid import uuid4

with open('moe/website/partials/footer.html') as footer_html:
    footer = footer_html.read()

def render_tool_page(response):
    header =  render_template('header.html', title = "MOE Tool")
    body = render_template('tool.html', response = response)
    return  header + body + footer

def get_unif(x : str):
    if x == "unif":
        return unif
    if x == "ac_unify":
        return ac_unify
    if x == "p_unif":
        return p_unif
    if x == "p_syntactic":
        return p_syntactic
    return None  

def get_chaining(x: str):
    if x == "CipherBlockChaining":
        return CipherBlockChaining
    if x == "PropogatingCBC":
        return PropogatingCBC
    if x == "CipherFeedback":
        return CipherFeedback
    if x == "HashCBC":
        return HashCBC
    # if x == "OutputFeedback":
    #     return OutputFeedback
    # if x == "CounterMode":
    #     return CounterMode
    # if x == "AccumulatedBlockCiper":
    #     return AccumulatedBlockCiper
    # if x == "DoubleHashCBC":
    #     return DoubleHashCBC
    return None

def format_substitutions(subs: List[SubstituteTerm]):
    text = ""
    for term in subs:
        term_str = str(term)
        for line in term_str.split('\n'):
            text += Markup.escape(line) + Markup('<br />')
        text += Markup('<br />')
    return text

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        unif = get_unif(request.form.get('unif'))
        chaining = get_chaining(request.form.get('chaining'))
        schedule = request.form.get('schedule')
        length_bound = int(request.form.get('length_bound'))
        length_bound = length_bound if length_bound < 100 and length_bound > 0 else 100
        session_bound = int(request.form.get('session_bound'))
        session_bound = session_bound if session_bound < 10 and session_bound > 0 else 10
        knows_iv = request.form.get('knows_iv') == "knows_iv"
        
        result = MOE(unif, chaining, schedule, length_bound, 1, knows_iv) if unif is not None and chaining is not None else "TRY AGAIN"
        return render_tool_page(format_substitutions(result)) if result is not None else render_tool_page("NO UNIFIERS FOUND")

    # Assume GET request and return form
    return render_tool_page("")

moe_sessions : Dict[str, MOESession] = dict()    
with open('moe/website/partials/program_create.html') as program_create_html:
    program_create = program_create_html.read()

DEFAULT_SID = 1 # Since each user can only simulate one MOE at a time
@app.route('/program', methods=['GET', 'POST'])
def program():
    header =  render_template('header.html', title = "MOE Program")

    # If you step away from the simulation, destroy the previous session
    if request.method == "GET" and 'uid' in session:
        if session['uid'] in moe_sessions.keys():
            del moe_sessions[session['uid']]
        session.pop('uid', None)

    if request.method == "POST":
        if 'uid' in session and session['uid'] in moe_sessions.keys():
            uid = session['uid']
            moe_session = moe_sessions[uid]
            response = None
            x = None
            if 'next' in request.form:
                x = Variable("x_" + str(moe_session.iteration[DEFAULT_SID]))
                response = moe_session.rcv_block(DEFAULT_SID, x)
            elif 'end' in request.form:
                response = moe_session.rcv_stop(DEFAULT_SID)
                del moe_sessions[uid]
                session.pop('uid', None)
            if response is not None or moe_session.schedule == "end":
                response = response if response is not None else "Sent " + str(x) if x is not None else ""
                return header + render_template('program.html', response = str(response)) + footer
        elif 'chaining' in request.form and 'schedule' in request.form:
            # Create new session
            chaining = get_chaining(request.form.get('chaining'))
            schedule = request.form.get('schedule')
            moe_session = MOESession(chaining, schedule)
            moe_session.rcv_start(DEFAULT_SID)
            # Send an initial message
            x = Variable("x_" + str(moe_session.iteration[DEFAULT_SID]))
            response = moe_session.rcv_block(DEFAULT_SID, x)
            # Set up a userid and save the moe_session
            session['uid'] = uuid4()
            moe_sessions[session['uid']] = moe_session
            response = response if response is not None else "Sent " + str(x) 
            return header + render_template('program.html', response = str(response)) + footer
    
    # Assume GET request and return form
    return header + program_create + footer
