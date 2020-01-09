# -*- coding: utf-8 -*-
"""
Author : Vincent Genin ESGI-3AL 2018
"""

import uuid
import graphviz as gv

def print_tree_graph(t, name):
    graph = gv.Digraph(format='svg')
    graph.attr('node', shape='circle')
    add_node(graph, t)
    graph.render(filename=name) #Pour Sauvegarder
    #graph.view() #Pour afficher

def add_node(graph, t):
    my_id = uuid.uuid4()

    if type(t) != tuple:
        graph.node(str(my_id), label=str(t))
        return my_id

    graph.node(str(my_id), label=str(t[0]))
    graph.edge(str(my_id), str(add_node(graph, t[1])), arrowsize='0')
    graph.edge(str(my_id), str(add_node(graph, t[2])), arrowsize='0')

    return my_id
