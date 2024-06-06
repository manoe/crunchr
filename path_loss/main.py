#!/bin/env python3

import yaml
import networkx as nx
import matplotlib.pyplot as plt

def role_to_color(role):
    if role == 'central':
        return 'tab:pink'
    elif role == 'internal':
        return 'tab:brown'
    elif role == 'border':
        return 'tab:cyan'
    elif role == 'external':
        return 'tab:blue'
    return 'tab:grey'


def graph_to_yaml(G):
    root = list()
    Grev = G.reverse()
    for i in Grev:
        routes = list()
        print("Node " + str(i) + ": ")
        for j in Grev[i]:
            print("Route to node " + str(j))
            routes.append({'node': str(j), 'pathid': '0'})
        root.append({'node': str(i), 'routes': routes})
    with open('routes.yaml', 'w') as file:
        yaml.dump(root, file)


def pl_to_graph(pl):
    DG = nx.DiGraph()
    edges = [(i['node'], j['node'], j['PL']) for i in pl for j in i['neighbors'] if i['node'] != j['node']]
    print(edges)
    DG.add_weighted_edges_from(edges)
    return DG


if __name__ == '__main__':
    stream = open('avg_pl.yaml', 'r')
    loader = yaml.safe_load(stream)
    nodes_w_pl = list(loader)
    DG = pl_to_graph(nodes_w_pl)
    print(DG)

    E = nx.algorithms.tree.Edmonds(DG)

    B = E.find_optimum(preserve_attrs=True)
    print(B.edges(data=True))



    DG.remove_edges_from([i for i in DG.edges() if i[0] == 0])

    C = nx.minimum_spanning_arborescence(DG)
    print(C.edges(data=True))

    nx.draw(DG, with_labels=True)
    pl
#    T = nx.DiGraph()
#    T.add_weighted_edges_from(t_adj)

#    nx.draw(T, pos, node_color=color_map, with_labels=True)
#    plt.show()


#    G.add_nodes_from(nodes_w_pl)
#    for i in nodes_w_pl:
#        G.add_nodes