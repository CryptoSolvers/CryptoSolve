from moe.website import app
from flask import request, render_template, session, Markup
from .utils import render_moo_template
@app.route('/custom', methods=['GET', 'POST'])
def custom():
    if request.method == 'POST':
        cmoe_string = request.form.get('cmoe')
        unif = unif_algo.get(request.form.get('unif'))
        #chaining_moe = chaining.get(request.form.get('chaining'))
        schedule = request.form.get('schedule')
        length_bound = int(request.form.get('length_bound'))
        length_bound = length_bound if length_bound < 100 and length_bound > 0 else 100
        session_bound = int(request.form.get('session_bound'))
        session_bound = session_bound if session_bound < 10 and session_bound > 0 else 10
        knows_iv = request.form.get('knows_iv') == "knows_iv"
        #moe_session = MOESession(CustomMOE, schedule, cmoe_string)


        result = MOE(unif, CustomMOE, schedule, length_bound, 1, knows_iv, cmoe_string) if unif is not None and cmoe_string != "" else "TRY AGAIN"
        response = format_substitutions(result) if result is not None else "NO UNIFIERS FOUND"
        return render_moo_template('custom.html', response=response)
        # Assume GET request and return form
    return render_moo_template('custom.html')

