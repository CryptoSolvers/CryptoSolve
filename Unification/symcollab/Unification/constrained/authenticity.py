
class Unification_state():
    #Each "unification state" has a set of equations and a substitution
    #Initially, there is one equation, and the substitution is the identity substitution.
    #The goal is to apply some inference rules so that the set of equations are simplified
    #and become empty eventually. As the rules are applied, we build up the substitution.
    #Eventually when the set of equations become empty, the substitution is the solution
    #that we are looking for.

    def __init__(self, equations, substitution):
        self.equations = equations
        self.substitution = substitution

    def is_empty(self):
        return self.equations == []

    def get_result(self):
        return self.substitution

def decompose(state):
    #Try applying the "decompose" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

def decompose_n(state):
    #Try applying the "decompose_n" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

def elim_c(state):
    #Try applying the "elim_c" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

def elim_tk(state):
    #Try applying the "elim_tk" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

def split(state):
    #Try applying the "split" rule
    #If successful, returns "True" and the new state
    #Otherwise, returns "False" and the original state

def apply_rules(state):
    while(not state.is_empty()):
        (successful, new_state) = decompose(state)
        if(successful):
            state = new_state
            break

        (successful, new_state) = decompose_n(state)
        if(successful):
            state = new_state
            break

        (successful, new_state) = elim_c(state)
        if(successful):
            state = new_state
            break

        (successful, new_state) = elim_tk(state)
        if(successful):
            state = new_state
            break

        (successful, new_state) = split(state)
        if(successful):
            state = new_state
            break

    return state.get_result()

    

    
