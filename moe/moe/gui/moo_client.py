#gui prototype
#pyinstaller -wF moo_client.py to create exe

import PySimpleGUI as sg


#returns the window that will be the client gui
#contains all of the formatting and other cool stuff that makes the gui window
def make_window():
    #theme properties for a theme that uses UMW colors
    sg.LOOK_AND_FEEL_TABLE['UMW'] = {'BACKGROUND': 'white',
                                     'TEXT': '#002a5a',
                                     'INPUT': 'white',
                                     'TEXT_INPUT': '#000000',
                                     'SCROLL': '#898c91',
                                     'BUTTON': ('white', '#002a5a'),
                                     'PROGRESS': ('#01826B', '#D0D0D0'),
                                     'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,}

    sg.theme('UMW')

    #size of all input boxes
    box_size = (30, 1) #for all input boxes
    ml_box_size = (70, 1) #for output boxes


    #------------------------tool page layout------------------------
    m = [sg.Multiline('', size=ml_box_size, pad=((10, 0),(110, 10)), key='-O1-')]#output box1
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    #left hand side input titles
    t_left_column = [[sg.Text('Unification Algorithm:')],
                     [sg.Text('Chaining Function:')],
                     [sg.Text('Schedule:')],
                     [sg.Text('Session Length Bound:')],
                     [sg.Text('Adversary knows IV?')]]

    #right hand side input boxes
    t_right_column = [[sg.InputCombo(('Syntactic', 'F-Rooted P-XOR'), size=box_size)],
                      [sg.InputCombo(('Cipher Block Chaining', 'Propogating Cipher Block Chaining', 'Hash Cipher Block Chaining', 'Cipher Feedback', 'Output Feedback'), size=box_size)],
                      [sg.InputCombo(('Every', 'End'), size=box_size)],
                      [sg.InputText('10', size=box_size)],
                      [sg.Checkbox('')]]

    #overall layout of the tab with both input titles and boxes, execute, and output box
    tool_layout = [[sg.Frame('Settings', [[
                    sg.Column(t_left_column),
                    sg.Column(t_right_column, key='-TOOL-INPUT-'),
                    sg.Column([], pad=(56,0))]],
                    pad=(11,10))],
                   [sg.Button('Execute!', pad=(10,0))],
                    output]


    #---------------------simulation page layout---------------------
    m = [sg.Multiline('', size=ml_box_size, pad=((10, 0),(190, 10)), key='-O2-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    #left hand side input titles
    s_left_column = [[sg.Text('Chaining Function:')],
                     [sg.Text('Schedule:')]]

    # right hand side input boxes
    s_right_column = [[sg.InputCombo(('Cipher Block Chaining', 'Propogating Cipher Block Chaining', 'Hash Cipher Block Chaining', 'Cipher Feedback', 'Output Feedback'), size=box_size)],
                      [sg.InputCombo(('Every', 'End'), size=box_size)]]

    #overall layout of the tab with both input titles and boxes, execute, and output box
    simulation_layout = [[sg.Frame('Settings', [[
                          sg.Column(s_left_column),
                          sg.Column(s_right_column),
                          sg.Column([], pad=(70,0))]],
                          pad=(10,10))],
                         [sg.Button('Execute!', pad=(10,0))],
                          output]


    #-----------------------custom page layout-----------------------
    m = [sg.Multiline('', size=ml_box_size, pad=((10, 0),(110, 10)), key='-O3-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    #left hand side input titles
    c_left_column = [[sg.Text('Custom MOO:')],
                     [sg.Text('Unification Algorithm:')],
                     [sg.Text('Schedule:')],
                     [sg.Text('Session Length Bound:')],
                     [sg.Text('Adversary knows IV?')]]

    # right hand side input boxes
    c_right_column = [[sg.InputText(('f(xor(P[i],C[i-1]))'), size=box_size)],
                      [sg.InputCombo(('Syntactic', 'F-Rooted P-XOR', 'XOR-Rooted P-XOR'), size=box_size)],
                      [sg.InputCombo(('Every', 'End'), size=box_size)],
                      [sg.InputText(('10'), size=box_size)],
                      [sg.Checkbox('')]]

    #overall layout of the tab with both input titles and boxes, execute, and output box
    custom_layout = [[sg.Frame('Settings', [[
                      sg.Column(c_left_column),
                      sg.Column(c_right_column),
                      sg.Column([], pad=(56,0))]],
                      pad=(10,10))],
                     [sg.Button('Execute!', pad=(10, 0))],
                      output]


    #----------------------random page layout-----------------------
    m = [sg.Multiline('', size=ml_box_size, pad=((10, 0),(6, 10)), key='-O4-')]
    output = [sg.Frame('Output', [m], pad=(10, 10))]

    #left hand side input titles
    r_left_column = [[sg.Text('Chaining Required:')],
                     [sg.Text('IV Required:')],
                     [sg.Text('Encryption F-Bound:')],
                     [sg.Text('Based on number of MOO to Generate:')],
                     [sg.Text('Test Each MOO for Security:')],
                     [sg.Text('Unification Algorithm:')],
                     [sg.Text('Schedule:')],
                     [sg.Text('Session Length Bound:')],
                     [sg.Text('Adversary knows IV?')]]

    # right hand side input boxes
    r_right_column = [[sg.InputCombo(('Yes', 'No'), size=box_size)],
                      [sg.InputCombo(('Yes', 'No'), size=box_size)],
                      [sg.InputText('6', size=box_size)],
                      [sg.InputText('4', size=box_size)],
                      [sg.InputCombo(('Yes', 'No'), size=box_size)],
                      [sg.InputCombo(('Syntactic', 'F-Rooted P-XOR', 'XOR-Rooted P-XOR'), size=box_size)],
                      [sg.InputCombo(('Every', 'End'), size=box_size)],
                      [sg.InputText('1', size=box_size)],
                      [sg.Checkbox('')]]

    #overall layout of the tab with both input titles and boxes, execute, and output box
    random_layout = [[sg.Frame('Settings', [[
                      sg.Column(r_left_column),
                      sg.Column(r_right_column),
                      sg.Column([], pad=(10,0))]],
                      pad=(10,10))],
                     [sg.Button('Execute!', pad=(10,0))],
                      output]


    #------------------------------TabGroup layout------------------------------
    #the keys allow for input to be differentiated among the tab events, for
    #example, in the Launcher events, there are 4 different execute events, 1
    #for each tab because of these keys
    #this allows you to tell which tab the user pressed the 'Execute!' button on
    tab_group_layout = [[sg.Tab('Tool', tool_layout, key='-TOOL-'),
                         sg.Tab('Simulation', simulation_layout, key='-SIMULATION-'),
                         sg.Tab('Custom', custom_layout, key='-CUSTOM-'),
                         sg.Tab('Random', random_layout, key='-RANDOM-')]]

    #menu definitions
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



#where the window is created and runs
#contains all of the events that occur when a user does something in the gui window
#contains all of the input that are in the window
def Launcher():
    window = make_window()
    #event loop
    while True:
        event, values = window.read()       # type: str, dict
        #if the window is closed leave loop immediately
        if event == sg.WIN_CLOSED:
            break
        #print(event, values)

        #all tool tab events
        if event == 'Execute!':
            #check all input
            start, stop = 1, 5
            popup = True
            result = []
            goodInput = True
            for i in range(start, stop):
                result.append(values[i])

            #check if any elements are empty, if so inform user
            if all(result) is not True:
                sg.Popup('Input left blank, please enter a value.', title='ERROR')
                popup = False
                goodInput = False

            result.append(values[stop]) #checkbox value should be allowed to be false

            # perform function call on input:
            if goodInput:
                window['-O1-'].update(result)

        # all simulation tab events
        if event == 'Execute!0':
            #check all input
            start, stop = 6, 7
            popup = True
            result = []
            goodInput = True
            for i in range(start, stop):
                result.append(values[i])
            result.append(values[stop])

            if all(result) is not True:
                sg.Popup('Input left blank, please enter a value.', title='ERROR')
                popup = False
                goodInput = False

            # perform function call on input:
            if goodInput:
                window['-O2-'].update(result)

        # all custom tab events
        if event == 'Execute!1':
            #check all input
            start, stop = 8, 12
            popup = True
            result = []
            goodInput = True
            for i in range(start, stop):
                result.append(values[i])

            if all(result) is not True:
                sg.Popup('Input left blank, please enter a value.', title='ERROR')
                popup = False
                goodInput = False

            result.append(values[stop])  # checkbox value should be allowed to be false

            # perform function call on input:
            if goodInput:
                window['-O3-'].update(result)

        # all random tab events
        if event == 'Execute!2':
            #check all input
            start, stop = 13, 21
            popup = True
            result = []
            goodInput = True
            for i in range(start, stop):
                result.append(values[i])

            if all(result) is not True:
                sg.Popup('Input left blank, please enter a value.', title='ERROR')
                popup = False
                goodInput = False

            result.append(values[stop])  # checkbox value should be allowed to be false

            #perform function call on input:
            if goodInput:
                window['-O4-'].update(result)

        #menu button events create popups
        #my intent with these is for this to be a place to give users more information
        #about how to use each part of the tool, but any of this can be removed as desired
        if event == 'Tool':
            sg.Popup('This is a blurb about how to use the tool page', title='Tool usage')
        if event == 'Simulation':
            sg.Popup('This is a blurb about how to use the simulation page', title='Simulation usage')
        if event == 'Custom':
            sg.Popup('This is a blurb about how to use the custom page', title='Custom usage')
        if event == 'Random':
            sg.Popup('This is a blurb about how to use the random page', title='Random usage')



    window.close()

if __name__ == '__main__':
    Launcher()