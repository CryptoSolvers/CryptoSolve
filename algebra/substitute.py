from algebra import *
# #
# ##
# ### Substitution Class
# ## Purpose: To hold substitutions and be able to apply them on a term
# #

# class Substitution:
#     def __init__(self):
#         self.subs = [] # Tuple of (Variable, TermDAG)
#     def add_substitution(self, variable, term):
#         assert isinstance(variable, Variable)
#         assert isinstance(term, Term) or isinstance(term, TermDAG)
        
#         td = None
#         if isinstance(term, Term):
#             td = TermDAG(term)
#         else:
#             td = term
        
#         self.subs.append((variable, td))

#     def apply_substitution(self, termdag):
#         new_dag = nx.OrderedDiGraph()
#         new_nodes = []
#         new_edges = []
#         ## Need to think of a way to handle substitutions so that
#         ## entire parts of a tree can be replaced
#         # nodes = termdag.df_node_traversal()
#         # variables, terms = zip(*self.subs)
#         # for (i, node) in enumerate(nodes):
#         #     if node in variables:
#         #         replacement = terms[variables.index(node)]
#         #         nodes[i] = replacement
#         new_dag.update(new_edges, new_nodes)
#         return new_dag


class SubstituteTerm:
    def __init__(self):
        self.subs = [] # Tuple of (Variable, Term)

    def add_substitution(self, variable, term):
        assert isinstance(variable, Variable)
        assert isinstance(term, Constant) or isinstance(term, FuncTerm) or isinstance(term, Variable)
        self.subs.append((variable, term))

    def __rmul__(self, term):
        new_term = deepcopy(term)
        new_term = self._termSubstituteHelper(term)
        return new_term
    
    def _termSubstituteHelper(self, term):
        return_value = None
        sub_vars, sub_terms = zip(*self.subs)
        if term in sub_vars:
            return_value = sub_terms[sub_vars.index(term)]
        elif isinstance(term, FuncTerm):
            term.arguments = list(term.arguments)
            for i, t in enumerate(term.arguments):
                term.arguments[i] = self._termSubstituteHelper(t)
            term.arguments = tuple(term.arguments)
            return_value = term
        else:
            return_value = term
        return return_value


# def termDAGSubstitute(dag, variable, replacement_term):
#     root = list(dag.dag.node)[0]
#     new_root = termSubstitute(root, variable, replacement_term)
#     return TermDAG(new_root)