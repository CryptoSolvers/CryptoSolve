from moe.website import app
from moe import *
from Unification import *
from Unification.p_unif import p_unif
from algebra import *
from flask import request, render_template, session, Markup
from typing import Dict
from uuid import uuid4

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
    p_syntactic=p_syntactic
)

chaining = dict(
    CipherBlockChaining=CipherBlockChaining,
    PropogatingCBC=PropogatingCBC,
    CipherFeedback=CipherFeedback,
    HashCBC=HashCBC
)

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
        unif = unif_algo.get(request.form.get('unif'))
        chaining_moe = chaining.get(request.form.get('chaining'))
        schedule = request.form.get('schedule')
        length_bound = int(request.form.get('length_bound'))
        length_bound = length_bound if length_bound < 100 and length_bound > 0 else 100
        session_bound = int(request.form.get('session_bound'))
        session_bound = session_bound if session_bound < 10 and session_bound > 0 else 10
        knows_iv = request.form.get('knows_iv') == "knows_iv"
        
        result = MOE(unif, chaining_moe, schedule, length_bound, 1, knows_iv) if unif is not None and chaining_moe is not None else "TRY AGAIN"
        response = format_substitutions(result) if result is not None else "NO UNIFIERS FOUND"
        return render_template('tool.html', title = 'MOE Tool', response = response, navigation=navigation)

    # Assume GET request and return form
    return render_template('tool.html', title = 'MOE Tool', navigation=navigation)

moe_sessions : Dict[str, MOESession] = dict()    

DEFAULT_SID = 1 # Since each user can only simulate one MOE at a time
@app.route('/program', methods=['GET', 'POST'])
def program():
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
                return render_template('program.html', response = str(response), navigation=navigation, title="MOE Simulation")
        elif 'chaining' in request.form and 'schedule' in request.form:
            # Create new session
            chaining = chaining.get(request.form.get('chaining'))
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
            return render_template('program.html', response = str(response), navigation=navigation, title="MOE Simulation")
    
    # Assume GET request and return form
    return render_template('program_create.html', navigation=navigation, title="MOE Simulation")
    
@app.route('/random', methods=['GET'])
def random():
    # If you step away from the simulation, destroy the previous session
    if 'uid' in session:
        if session['uid'] in moe_sessions.keys():
            del moe_sessions[session['uid']]
        session.pop('uid', None)
    # Grab parameters from URL
    rid = int(request.args.get("rid", 0))
    chaining_required = True if request.args.get("chaining", "Yes") == "Yes" else False
    iv_required = True if request.args.get("iv", "Yes") == "Yes" else False
    f_bound = int(request.args.get("bound", 1))
    random_moe_term = ""
    if rid != 0:
        filtered_gen = FilteredMOEGenerator(
            max_history=1,
            max_f_depth=f_bound,
            must_start_with_IV=iv_required,
            must_have_chaining=chaining_required
        )
        random_moe_term = [next(filtered_gen) for i in range(rid)][-1]
    return render_template(
        'random.html',
        title='Random MOE Generator',
        navigation=navigation,
        rid=1 if rid is None else rid + 1,
        chaining="Yes" if chaining_required else "No",
        iv="Yes" if iv_required else "No",
        bound=f_bound,
        random_moe=random_moe_term
    )
    
@app.route('/custom', methods=['GET', 'POST'])
def custom():
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
                return render_template('custom.html', response = str(response), title="Custom MOE Tool", navigation=navigation)
        elif 'cmoe' in request.form and 'schedule' in request.form:
            # Create new session
            cmoe_string = request.form.get('cmoe')
            schedule = request.form.get('schedule')
            moe_session = MOESession(CustomMOE, schedule, cmoe_string)
            moe_session.rcv_start(DEFAULT_SID)
            # Send an initial message
            x = Variable("x_" + str(moe_session.iteration[DEFAULT_SID]))
            response = moe_session.rcv_block(DEFAULT_SID, x)
            # Set up a userid and save the moe_session
            session['uid'] = uuid4()
            moe_sessions[session['uid']] = moe_session
            response = response if response is not None else "Sent " + str(x) 
            return render_template('custom.html', response = str(response), title="Custom MOE Tool", navigation=navigation)
    
    # Assume GET request and return form
    return render_template('custom.html', title="Custom MOE Tool", navigation=navigation)
