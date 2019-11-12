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

def render_page(response):
    header =  render_template('header.html', title = "MOE Tool", styles = styles)
    body = render_template('template.html', response = response)
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
        return render_page(str(result)) if result is not None else render_page("NO UNIFIERS FOUND")

    # Assume GET request and return form
    print(request.method)
    return render_page("")
