from flask import request, render_template, session, Markup
from moe.website import app

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
    moe_bound = int(request.args.get("moenum", 1))
    security_required = True if request.args.get("sectest", "Yes") == "Yes" else False
    unif = unif_algo.get(request.args.get('unif'))
    schedule = request.args.get('schedule')
    length_bound = int(request.args.get("length_bound", 1))
    length_bound = length_bound if length_bound < 100 and length_bound > 0 else 100
    session_bound = int(request.args.get("session_bound", 1))
    session_bound = session_bound if session_bound < 10 and session_bound > 0 else 10
    knows_iv = request.form.get('knows_iv') == "knows_iv"
    random_moe_term = ""
    response = ""
    moe_list=[]
    moe_safe_list=[]
    moe_unsafe_list=[]
    result = []
    if rid != 0:
        filtered_gen = FilteredMOEGenerator(
            max_history=1,
            max_f_depth=f_bound,
            must_start_with_IV=iv_required,
            must_have_chaining=chaining_required
        )
        #random_moe_term = [next(filtered_gen) for i in range(rid)][-1]
        for i in range(moe_bound):
            moe_list.append(next(filtered_gen))

        print("----Print moe_list:")
        for i in moe_list:
            print(i)

        for random_moe_term in moe_list:
            tm = TermMOE(random_moe_term)
            temp = MOE(unif, tm, schedule, length_bound, session_bound)
            result = temp if temp is not None else list()
            if len(result) == 0:
                moe_safe_list.append(random_moe_term)
            else:
                moe_unsafe_list.append(random_moe_term)
        if len(moe_safe_list) == 0:
            response = "No Safe MOEs Found. The follow MOE were tested: \n"
            for i in moe_list:
                response = response + str(i) + "\n"
        else:
            response = "Safe MOEs Found. The following MOE(s) pass the security Test: \n"
            for i in moe_safe_list:
                response = response + str(i) +"\n"
    return render_template(
        'random.html',
        title='Random MOE Generator',
        navigation=navigation,
        rid=1 if rid is None else rid + 1,
        chaining="Yes" if chaining_required else "No",
        iv="Yes" if iv_required else "No",
        bound=f_bound,
        moenum=moe_bound,
        sectest="Yes" if security_required else "No",
        random_moe=random_moe_term,
        response = response
    )
