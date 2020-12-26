# TODO: Not accounting for proof steps being longer than a line long...

from symcollab.algebra import *
from symcollab.rewrite import *
import curses

class GoalWindow:
    def __init__(self, goal_term, color = 0):
        self.window = curses.newwin(1, curses.COLS, 0, 0)
        self.color = color
        self.change_goal(goal_term)
    
    def change_goal(self, goal_term):
        self.window.clear()
        self.window.border(0, 0, 0, '-', 0, 0, 0, 0)
        goal_text = " Goal: " + str(goal_term) + " "
        self.window.addstr(
            0, 
            curses.COLS // 2 - len(goal_text) // 2, 
            goal_text,
            curses.color_pair(self.color)
        )
        self.window.refresh()
    def clear(self):
        self.window.clear()
        self.window.refresh()


class HypothesisWindow:
    def __init__(self, rules):
        self.window = curses.newwin(curses.LINES - 2, curses.COLS // 4, 1, 3 * (curses.COLS // 4))
        self.change_rules(rules)

    def change_rules(self, rules):
        self.window.clear()
        self.window.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.window.addstr(1, 1, "Hypotheses:", curses.A_UNDERLINE)
        hypotheses_text = "\n ".join(
            [str(i) + ". " + str(rule) for i, rule in enumerate(rules)]
        )
        self.window.addstr(
            3,
            1,
            hypotheses_text
        )
        self.window.refresh()
    
    def clear(self):
        self.window.clear()
        self.window.refresh()


class ProofPad:
    def __init__(self):
        MAXPADPROOF = 10 * curses.LINES
        self.pad = curses.newpad(MAXPADPROOF, 3 * (curses.COLS // 4))
        self.proof = []

    def add(self, term):
        self.proof.append(term)
        self.pad.addstr(
            0,
            0,
            "\n".join(
                [str(t) for t in self.proof]
            )
        )
        self.pad.refresh(
            0,
            0,
            2,
            0,
            curses.LINES - 2,
            3 * (curses.COLS // 4)
        )


## Initialize algebras
f = Function("f", 2)
inv = Function("inv", 1)
x = Variable("x")
a = Constant("a")

# Initial rewrite rules
rules = {
    RewriteRule(f(x, inv(x)), a),
    RewriteRule(f(inv(x), x), a),
    RewriteRule(f(a, x), f(x, a)),
    RewriteRule(f(x, a), f(a, x))
}

initial_term = f(x, f(x, f(inv(x), f(a, f(x, f(inv(x), inv(x)))))))
goal_term = f(x, f(a, inv(x)))

def main(screen):
    curses.noecho()

    # Colors
    curses.use_default_colors()
    GREEN = 1
    curses.init_pair(GREEN, curses.COLOR_GREEN, -1) # -1 to set to terminal default

    goal_window = GoalWindow(goal_term, GREEN)
    hypothesis_window = HypothesisWindow(rules)
    proof_pad = ProofPad()
    proof_pad.add(initial_term) 

    # Get input at bottom of screen
    curses.echo()
    command_window = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)
    result = command_window.getstr(0, 1)

    goal_window.clear()
    hypothesis_window.clear()

    curses.endwin()
    print(result)

curses.wrapper(main)

