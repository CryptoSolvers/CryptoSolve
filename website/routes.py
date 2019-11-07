from website import app
from moe import *
from Unification import *
from Unification.p_unif import p_unif
from algebra import *
from flask import request

def render_page(response):
    header_form = """
    <!DOCTYPE html>
    <html>
    <head><title>MOE Tool</title></head>
    <body>
        <h1>MOE Tool</h1>
        <form action='/' method='POST'>
            <div>
                <label for='unif'>Unification Algorithm:</label>
                <select id='unif' name='unif'>
                    <!--<option value='unif'>Syntactic</option>-->
                    <!--<option value='ac_unify'>AC</option>-->
                    <option value='p_unif'>Xor</option>
                </select>
            </div>
            <div>
                <label for='chaining'>Chaining Function:</label>
                <select id='chaining' name='chaining'>
                    <option value='CipherBlockChaining'>Cipher Block Chaining</option>
                    <option value='PropogatingCBC'>Propogating Cipher Block Chaining</option>
                    <option value='CipherFeedback'>Cipher Feedback</option>
                    <option value='HashCBC'>Hash Cipher Block Chaining</option>
                    <!--<option value='OutputFeedback'>Output Feedback</option>-->
                    <!--<option value='CounterMode'>Counter Mode</option>-->
                    <!--<option value='AccumulatedBlockCiper'>Accumulated Block Cipher</option>-->
                    <!--<option value='DoubleHashCBC'>Double Hash Cipher Block Chaining</option>-->
                </select>
            </div>
            <div>
                <label for='schedule'>Schedule:</label>
                <select id='schedule' name='schedule'>
                    <option value='every'>Every</option>
                    <option value='end'>End</option>
                </select>
            </div>
            <div>
                <label for='length_bound'>Session Length Bound</label>
                <input type='number' min='1' max='10' name='length_bound' id='length_bound' required/>
            </div>
            <div>
                <label for='session_bound'>Number of Sessions Bound</label>
                <input type='number' min='1' max='10' name='session_bound' id='session_bound' required/>
            </div>
            <input type='submit' value='Execute!'/>
        </form>
    """
    response_block = "" if response is "" else "<div><code>" + response + "</code></div>"
    print(response)
    return header_form + response_block + "</body></html>"

def get_unif(x : str):
    if x == "unif":
        return unif
    if x == "ac_unify":
        return ac_unify
    if x == "p_unif":
        return p_unif
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
        return render_page(str(result)) if result is not None else render_page("NO UNIFIERS FOUND")

    # Assume GET request and return form
    print(request.method)
    return render_page("")
