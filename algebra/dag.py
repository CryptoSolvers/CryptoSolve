from .term import *

#
## Directed Acyclic Graphs
#
class TermDAG:
    def __init__(self, term: Term):
        self.dag = nx.OrderedMultiGraph()
        self.term = term
        self.edge_labels = {}
        self.node_labels = {}
        self.dag.add_node(term)
        if isinstance(term, FuncTerm):
            self.node_labels[term] = term.function
            for index, t in enumerate(term.arguments):
                self._appendTermDAG(term, t, self.dag, label = str(index))
        else:
            self.node_labels[term] = term

    def _appendTermDAG(self, last_term : Term, term : Term, dag : nx.classes.digraph.DiGraph, label = ""):
        # Annotate edges with argument number
        if (last_term, term) in self.edge_labels and self.edge_labels[(last_term, term)] != label:
            self.edge_labels[(last_term, term)] = self.edge_labels[(last_term, term)] + ", " + label
        else:
            self.edge_labels[(last_term, term)] = label
        
        dag.add_edge(last_term, term)
        if isinstance(term, FuncTerm):
            # Go through each of the function arguments and add a directed edge to it
            for index, t in enumerate(term.arguments):
                self._appendTermDAG(term, t, dag, label = str(index))
            self.node_labels[term] = term.function
        else:
            self.node_labels[term] = term

    def show(self):
        fig = plt.figure()
        pos = nx.spring_layout(self.dag)
        nx.draw(self.dag, pos, font_weight = 'bold', node_size = 600, font_size = 30, node_color = ['#a8c74d'] + ['#1f78b4' for i in range(len(self.dag.nodes) - 1)])
        nx.draw_networkx_labels(self.dag, pos, labels = self.node_labels)
        nx.draw_networkx_edge_labels(self.dag, pos, edge_labels=self.edge_labels)
        fig.suptitle(self.term)
        plt.show()
    
    # Depth First Traversal
    def df_edge_traversal(self):
        return nx.dfs_edges(self.dag, source = list(self.dag.node)[0])
    def df_node_traversal(self):
        return nx.dfs_tree(self.dag, source = list(self.dag.node)[0])
    # Breadth First Traversal
    def bs_edge_traversal(self):
        return nx.bfs_edges(self.dag, source = list(self.dag.node)[0])
    def bs_node_traversal(self):
        return nx.bfs_tree(self.dag, source = list(self.dag.node)[0])
    
    def parents(self, term):
        if term in self.dag.node:
            return self.dag.predecessors(term)
        else:
            return []