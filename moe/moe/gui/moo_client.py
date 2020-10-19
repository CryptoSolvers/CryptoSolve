#gui prototype
#pyinstaller -F moo_client.spec to create exe

from moe.check import moo_check
from moe.website.routes.custom import _temporary_parser
from moe.website.routes.utils import restrict_to_range
from moe.custom import CustomMOO
from Unification.unif import unif
from Unification.p_syntactic import p_syntactic
from Unification.ac_unif import ac_unify
from Unification.p_unif import p_unif
from Unification.xor_rooted_unif import XOR_rooted_security
from moe.filtered_generator import FilteredMOOGenerator
import PySimpleGUI as sg
import operator
import sys

unification_algorithms = ['Syntactic', 'F-Rooted P-XOR', 'XOR-Rooted P-XOR']
unif_dict = {'Syntactic': p_syntactic, 'F-Rooted P-XOR': p_unif, 'XOR-Rooted P-XOR': XOR_rooted_security}
chaining_functions = ['Cipher Block Chaining', 'Propogating Cipher Block Chaining', \
                      'Hash Cipher Block Chaining', 'Cipher Feedback', 'Output Feedback']
cf_dict = {'Cipher Block Chaining': 'cipher_block_chaining',
            'Propogating Cipher Block Chaining': 'propogating_cbc',
            'Hash Cipher Block Chaining': 'hash_cbc',
            'Cipher Feedback': 'cipher_feedback',
            'Output Feedback': 'output_feedback'}
schedules = ['Every', 'End']
scd_dict = {'Every': 'every', 'End': 'end'}

# should the user press exit then the gui will not relaunch when closed
_error = True

# returns the window that will be the client gui
# contains all of the formatting and other cool stuff that makes the gui window
def make_window():
    # theme properties for a theme that uses UMW colors
    sg.LOOK_AND_FEEL_TABLE['UMW'] = {'BACKGROUND': 'white',
            'TEXT': '#002a5a',
            'INPUT': 'white',
            'TEXT_INPUT': '#000000',
            'SCROLL': '#898c91',
            'BUTTON': ('white', '#002a5a'),
            'PROGRESS': ('#01826B', '#D0D0D0'),
            'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,}

    sg.theme('UMW')

    box_size = (30, 1) #for all input boxes
    ml_box_size = (70, 15) #for output boxes
    c_pad = (0, 3) #padding amount for checkboxes

    #------------------------tool page layout------------------------
    m = [sg.Multiline('', size=add_t(ml_box_size, (0, 7)), pad=((10, 0),(10, 10)), key='-O1-')]#output box1
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    # left hand side input titles
    t_left_column = [[sg.Text('Unification Algorithm:')],
            [sg.Text('Chaining Function:')],
            [sg.Text('Schedule:')],
            [sg.Text('Session Length Bound:')],
            [sg.Text('Adversary knows IV?')]]

    # right hand side input boxes
    t_right_column = [[sg.InputCombo((unification_algorithms), size=box_size)],
            [sg.InputCombo((chaining_functions), size=box_size)],
            [sg.InputCombo((schedules), size=box_size)],
            [sg.InputText('10', size=box_size)],
            [sg.Checkbox('', pad=c_pad)]]

    # overall layout of the tab with both input titles and boxes, execute, and output box
    tool_layout = [[sg.Frame('Settings', [[
        sg.Column(t_left_column),
        sg.Column(t_right_column, key='-TOOL-INPUT-'),
        sg.Column([], pad=(56,0))]],
        pad=(11,10))],
        [sg.Button('Execute!', pad=(10,0))],
        output]


    #---------------------simulation page layout---------------------
    m = [sg.Multiline('', size=add_t(ml_box_size, (0, 10)), pad=((10, 0),(10, 10)), key='-O2-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    # left hand side input titles
    s_left_column = [[sg.Text('Chaining Function:')],
            [sg.Text('Schedule:')]]

    # right hand side input boxes
    s_right_column = [[sg.InputCombo((chaining_functions), size=box_size)],
            [sg.InputCombo((schedules), size=box_size)]]

    # overall layout of the tab with both input titles and boxes, execute, and output box
    simulation_layout = [[sg.Frame('Settings', [[
        sg.Column(s_left_column),
        sg.Column(s_right_column),
        sg.Column([], pad=(70,0))]],
        pad=(10,10))],
        [sg.Button('Execute!', pad=(10,0))],
        output,
        [sg.Button('Next>>', pad=(10,0))]]


    #-----------------------custom page layout-----------------------
    m = [sg.Multiline('', size=add_t(ml_box_size, (0, 7)), pad=((10, 0),(10, 10)), key='-O3-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    # left hand side input titles
    c_left_column = [[sg.Text('Custom MOO:')],
            [sg.Text('Unification Algorithm:')],
            [sg.Text('Schedule:')],
            [sg.Text('Session Length Bound:')],
            [sg.Text('Adversary knows IV?')]]

    # right hand side input boxes
    c_right_column = [[sg.InputText(('f(xor(P[i],C[i-1]))'), size=box_size)],
            [sg.InputCombo((unification_algorithms), size=box_size)],
            [sg.InputCombo((schedules), size=box_size)],
            [sg.InputText(('10'), size=box_size)],
            [sg.Checkbox('', pad=c_pad)]]

    # overall layout of the tab with both input titles and boxes, execute, and output box
    custom_layout = [[sg.Frame('Settings', [[
        sg.Column(c_left_column),
        sg.Column(c_right_column),
        sg.Column([], pad=(56,0))]],
        pad=(10,10))],
        [sg.Button('Execute!', pad=(10, 0))],
        output]


    #----------------------random page layout-----------------------
    m = [sg.Multiline('', size=ml_box_size, pad=((10, 0),(10, 10)), key='-O4-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    # left hand side input titles
    r_left_column = [[sg.Text('Unification Algorithm:')],
            [sg.Text('Schedule:')],
            [sg.Text('Session Length Bound:')],
            [sg.Text('Encryption F-Bound:')],
            [sg.Text('Based on number of MOO to Generate:')],
            [sg.Text('Chaining Required:')],
            [sg.Text('IV Required:')],
            [sg.Text('Test Each MOO for Security:')],
            [sg.Text('Adversary knows IV?')]]

    # right hand side input boxes
    r_right_column = [[sg.InputCombo((unification_algorithms), size=box_size)],
            [sg.InputCombo((schedules), size=box_size)],
            [sg.InputText('1', size=box_size)],
            [sg.InputText('6', size=box_size)],
            [sg.InputText('4', size=box_size)],            
            [sg.Checkbox('', pad=c_pad)],
            [sg.Checkbox('', pad=c_pad)],
            [sg.Checkbox('', pad=c_pad)],
            [sg.Checkbox('', pad=c_pad)]]

    # overall layout of the tab with both input titles and boxes, execute, and output box
    random_layout = [[sg.Frame('Settings', [[
        sg.Column(r_left_column),
        sg.Column(r_right_column),
        sg.Column([], pad=(10,0))]],
        pad=(10,10))],
        [sg.Button('Execute!', pad=(10,0))],
        output]


    #------------------------------TabGroup layout------------------------------
    # the keys allow for input to be differentiated among the tab events, for
    # example, in the Launcher events, there are 4 different execute events, 1
    # for each tab because of these keys
    # this allows you to tell which tab the user pressed the 'Execute!' button on
    tab_group_layout = [[sg.Tab('Tool', tool_layout, key='-TOOL-'),
        sg.Tab('Simulation', simulation_layout, key='-SIMULATION-'),
        sg.Tab('Custom', custom_layout, key='-CUSTOM-'),
        sg.Tab('Random', random_layout, key='-RANDOM-')]]

    # menu definitions
    menu_layout = [['&Help', ['&Tool', '&Simulation', '&Custom', '&Random']],
            ['&About', ['&README', '&Authors', '&Usage']]]

    # The window layout - defines the entire window
    layout = [[sg.Menu(menu_layout, tearoff=True)],[sg.TabGroup(tab_group_layout,
        tab_location='topleft',
        tab_background_color='#002a5a',
        selected_background_color="grey",
        title_color='white',
        selected_title_color='white',
        enable_events=True,)]]

    return sg.Window('MOO Tool', layout, no_titlebar=False)

# where the window is created and runs
# contains all of the events that occur when a user does something in the gui window
# contains all of the input that are in the window
def Launcher():
    window = make_window()
    # event loop
    while True:
        event, values = window.read()       # type: str, dict
        # if the window is closed leave loop immediately
        if event == sg.WIN_CLOSED:
            break
        # print(event, values)

        start, stop = 1, 5
        result = []
        popup = True
        goodInput = True
        function = ''

        # all tool tab events
        if event == 'Execute!':
            # check all input
            start, stop = 1, 5
            function = 'tool'
            for i in range(start, stop):
                result.append(values[i])

        sim_next = False
        # all simulation tab events
        if event == 'Execute!0' or event =='Next>>':
            if event == 'Next>>':
                sim_next = True
            # check all input
            start, stop = 6, 7
            function = 'simulation'
            for i in range(start, stop):
                result.append(values[i])
            result.append(values[stop])

        # all custom tab events
        if event == 'Execute!1':
            # check all input
            start, stop = 8, 12
            function = 'custom'
            for i in range(start, stop):
                result.append(values[i])

        # all random tab events
        if event == 'Execute!2':
            #check all input
            start, mid, stop = 13, 17, 21
            function = 'random'
            for i in range(start, mid):
                result.append(values[i])
            result.append(values[mid])

        # check if any of the inputs are blank
        if all(result) is not True:
            sg.Popup('Input left blank, please enter a value.', title='ERROR')
            popup = False
            goodInput = False

        if function == 'tool' and goodInput:
            if valid_moo_unif_pair(result[0], result[1]) == False:
                goodInput = False
                sg.Popup('Invalid unfication algorithm and chaining function combination, see Help -> Tool for more information', title='ERROR')

        # these pages have the checkbox input which is default false, which messes
        # up the check for blank inputs, so here we add those values back in
        if function == 'tool' or function == 'custom':
            result.append(values[stop])
        elif function == 'random':
            for i in range(mid+1, stop+1):
                result.append(values[i])


        # if none of the input is blank / combinations are good
        #then perform tool functions and output results to window
        if goodInput:
            if function == 'tool':
                unif = unif_dict[result[0]]
                chaining = cf_dict[result[1]]
                sched = scd_dict[result[2]]
                length_bound = restrict_to_range(int(result[3]), 0, 100)
                knows_iv = result[4]
                # check for security and catch exceptions
                try:
                    result = moo_check(chaining, sched, unif, length_bound, knows_iv)
                except ValueError as v_err:
                    message = 'ValueError: ' + str(v_err)
                    sg.Popup(message, title='VALUE ERROR')
                    window.close()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    window.close()
                response = get_response(result)
                window['-O1-'].update(response)
            if function == 'simulation':
                if sim_next:
                    window['-O2-'].update(str(result) + " next")
                else:
                    window['-O2-'].update(result)
            if function == 'custom':
                chaining = CustomMOO(_temporary_parser(result[0])).name
                unif = unif_dict[result[1]]
                sched = scd_dict[result[2]]
                length_bound = restrict_to_range(int(result[3]), 0, 100)
                knows_iv = result[4]
                try:
                    result = moo_check(chaining, sched, unif, length_bound, knows_iv)
                except ValueError as v_err:
                    message = 'ValueError: ' + str(v_err)
                    sg.Popup(message, title='VALUE ERROR')
                    window.close()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    window.close()
                response = get_response(result)
                window['-O3-'].update(response)
            if function == 'random':
                unif = unif_dict[result[0]]
                sched = scd_dict[result[1]]
                length_bound = restrict_to_range(int(result[2]), 0, 100)
                f_bound = int(result[3])
                moo_bound = restrict_to_range(int(result[4]), 1, 100)
                c_req = result[5]
                iv_req = result[6]
                sec_req = result[7]
                knows_iv = result[8]

                # generate random moos
                filtered_gen = FilteredMOOGenerator(1, f_bound, iv_req, c_req)
                moo_list = (next(filtered_gen) for i in range(moo_bound))

                # Check security of the modes of operation
                moo_safe_list: List[Term] = list()
                for random_moo_term in moo_list:
                    print("Considering...", random_moo_term)
                    cm = CustomMOO(random_moo_term)
                    moo_result = moo_check(cm.name, sched, unif, length_bound, knows_iv)
                    if moo_result.secure:
                        moo_safe_list.append(random_moo_term)

                if len(moo_safe_list) == 0:
                    response = "No same MOOs found. The following MOO(s) were tested: \n"
                    for term in moo_list:
                        response += str(term) + "\n"
                else:
                    response = "Safe MOO(s) found. The following MOO(s) pass the security test: \n"
                    for term in moo_safe_list:
                        response += str(term) + "\n"
                window['-O4-'].update(response)

        # menu button events create popups
        # my intent with these is for this to be a place to give users more information
        # about how to use each part of the tool, but any of this can be removed as desired
        if event == 'Tool':
            sg.Popup('Valid unification algorithm and chaining function pairs:\n\n'
                     'Syntactic: Cipher Block Chaining, Propogating Cipher Block Chaining,' \
                     ' Hash Cipher Block Chaining, Cipher Feedback, Output Feedback\n'
                     'F-Rooted P-XOR: Cipher Block Chaining, Propogating Cipher Block Chaining, Hash Cipher Block Chaining\n'
                     'XOR-Rooted P-XOR: Cipher Feedback, Output Feedback', title='Tool usage', line_width=200)
        if event == 'Simulation':
            sg.Popup('This is a blurb about how to use the simulation page', title='Simulation usage')
        if event == 'Custom':
            sg.Popup('This is a blurb about how to use the custom page', title='Custom usage')
        if event == 'Random':
            sg.Popup('This is a blurb about how to use the random page', title='Random usage')

    window.close()

def valid_moo_unif_pair(unif_choice: str, cf_choice: str) -> bool:
    # syntactic
    if unif_choice == unification_algorithms[0]:
        return True
    # p-unif
    if unif_choice == unification_algorithms[1]:
        supported_chaining = ['Cipher Block Chaining', 'Propogating Cipher Block Chaining', 'Hash Cipher Block Chaining']
    # xor rooted
    else:
	    supported_chaining = ['Cipher Feedback', 'Output Feedback']
    return cf_choice in supported_chaining

def get_response(result) -> str:
    response = ""
    if result.secure:
        response = "MOO IS SECURE: "
        if result.syntactic_result:
            response += "PASSES SYNTACTIC CHECK"
        else:
            response += "NO UNIFIERS FOUND"
    else:
        response = "MOO IS INSECURE. COLLISIONS WITH SUBSTITUTION(S) "
        for i in result.collisions:
            response += str(i) + " "
    return response

# tuple addition
def add_t(t1: tuple, t2: tuple) -> tuple:
    return tuple(map(operator.add, t1, t2))

if __name__ == '__main__':
    while _error:
        try:
            Launcher()
            _error = False
        except:
            sg.Popup('Error: Relaunching gui')
            _error = True


