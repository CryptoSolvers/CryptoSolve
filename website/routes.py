from website import app
from moe import *
from Unification import *
from Unification.p_unif import p_unif
from algebra import *
from flask import request, render_template

with open('website/footer.html') as footer_html:
    footer = footer_html.read()

with open('website/style.css','r') as css_file:
    styles = css_file.read()

def render_tool_page(response):
    header =  render_template('header.html', title = "MOE Tool", styles = styles)
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
    # if x is "OutputFeedback":
    #     return OutputFeedback
    # if x is "CounterMode":
    #     return CounterMode
    # if x is "AccumulatedBlockCiper":
    #     return AccumulatedBlockCiper
    # if x is "DoubleHashCBC":
    #     return DoubleHashCBC
    return None

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
        result = MOE(unif, chaining, schedule, length_bound, 1) if unif is not None and chaining is not None else "TRY AGAIN"
        return render_tool_page(str(result)) if result is not None else render_tool_page("NO UNIFIERS FOUND")

    # Assume GET request and return form
    print(request.method)
    return render_tool_page("")


# [TODO] Should probably implement locks here in the future
moe_sessions : List[MOESession] = []
sids : List[int] = []
def find_moe_session(sid : int) -> Optional[MOESession]:
    for moe_session in moe_sessions:
        if sid in moe_session.sessions:
            return moe_session
    return None

def new_moe_session(chaining, schedule : str) -> Tuple[int, MOESession]:
    similar_session : Optional[MOESession] = None
    for moe_session in moe_sessions:
        if moe_session.chaining_function == chaining and moe_session.schedule == schedule:
            similar_session = moe_session
            break # Done looking
    # No similar MOE session found
    if similar_session == None:
        similar_session = MOESession(chaining, schedule)
        moe_sessions.append(similar_session)
    # Add new session
    sid = sids[-1] + 1 if len(sids) > 0 else 1
    sids.append(sid)
    similar_session.rcv_start(sid)
    return sid, similar_session

def get_fresh_variable(session : MOESession) -> Variable:
    return Variable("x_" + str(session.iteration))
    
with open('website/program_create.html') as program_create_html:
    program_create = program_create_html.read()

@app.route('/program', methods=['GET', 'POST'])
def program():
    if request.method == "POST":
        if 'sid' in request.form:
            # Continue existing session
            sid = int(request.form.get('sid'))
            moe_session = find_moe_session(sid)
            if moe_session != None:
                response = None
                if 'next' in request.form:
                    x = get_fresh_variable(moe_session)
                    response = moe_session.rcv_block(sid, x)
                elif 'end' in request.form:
                    response = moe_session.rcv_stop(sid)
                    sids.remove(sid)
                if response != None:
                    return render_template('program.html', response = str(response), sid = sid)
        elif 'chaining' in request.form and 'schedule' in request.form:
            # Create new session
            chaining = get_chaining(request.form.get('chaining'))
            schedule = request.form.get('schedule')
            sid, moe_session = new_moe_session(chaining, schedule)
            # Send an initial message
            x = get_fresh_variable(moe_session)
            response = moe_session.rcv_block(sid, x)
            return render_template('program.html', response = str(response), sid = sid)



    # Assume GET request and return form
    header =  render_template('header.html', title = "MOE Program", styles = styles)
    return  header + program_create + footer
