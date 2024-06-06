#!/bin/env python3

import copy
import yaml
import networkx as nx
import matplotlib.pyplot as plt
import operator

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


def get_centrality(G):
    G_Cb = nx.betweenness_centrality(G, weight='weight', normalized=True)
    return sum([max(G_Cb.values())-i for i in G_Cb.values()])/(len(G)-1)


def get_msa(G):
    Gp = copy.deepcopy(G)
    Gp.remove_edges_from([i for i in DG.edges() if i[0] == 0])
    E = nx.algorithms.tree.Edmonds(Gp.reverse())
    return E.find_optimum(preserve_attrs=True, kind='max').reverse()



def pl_to_graph(pl):
    DG = nx.DiGraph()
    edges = [(i['node'], j['node'], 100 - j['PL']) for i in pl for j in i['neighbors'] if i['node'] != j['node']]
    print(edges)
    DG.add_weighted_edges_from(edges)
    return DG


if __name__ == '__main__':
    stream = open('avg_pl.yaml', 'r')
    loader = yaml.safe_load(stream)
    nodes_w_pl = list(loader)
    DG = pl_to_graph(nodes_w_pl)
    print(DG)

    print(nx.betweenness_centrality(DG))
    print(get_centrality(DG))
    DG.remove_edges_from([i for i in DG.edges() if i[0] == 0])

    E = nx.algorithms.tree.Edmonds(DG)
    B = E.find_optimum(attr='weight', kind='max', preserve_attrs=True)

    C = get_msa(DG)
#    F = nx.algorithms.tree.Edmonds(DG.reverse())
#    C = F.find_optimum(preserve_attrs=True)

    print(get_centrality(C))
    print('Most central node for Ur-graph: '+str(max(nx.betweenness_centrality(DG).items(), key=operator.itemgetter(1))[0]))
    print('Most central node for MSA: ' + str(
        max(nx.betweenness_centrality(C).items(), key=operator.itemgetter(1))[0]))

    fig = plt.figure()
    ax = fig.subplots(1, 2)
    nx.draw(B, with_labels=True, ax=ax[0], pos=nx.planar_layout(B))
    nx.draw(C, with_labels=True, ax=ax[1], pos=nx.planar_layout(C))

    plt.tight_layout()
    plt.show()


