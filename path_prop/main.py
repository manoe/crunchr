#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
from scipy.stats import entropy
import matplotlib
import pydot
from networkx.drawing.nx_pydot import graphviz_layout


# https://matplotlib.org/stable/tutorials/colors/colors.html
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

def load_network(loader):
    g_nw = nx.DiGraph()

    for i in loader['loc_pdr']:
        g_nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if i['role'] == 'external':
                    pathid = [k['pathid'] for k in j['pathid']]
                    secl = False
                    for k in j['pathid']:
                        if k['secl']:
                            secl = True

                    g_nw.add_edge(i['node'], j['node'], pathid=pathid, secl=secl)
                else:
                    g_nw.add_edge(i['node'], j['node'], secl=j['secl'])
    return g_nw


def get_pdr_arr(loader, nodes):
    return [loader['pdr'][i]['pkt_recv']/loader['pdr'][i]['pkt_sent'] for i in loader['pdr'] if i in nodes]


def get_path_stat(loader):
    g_nw = load_network(loader)

    paths = [n for n, v in g_nw.nodes(data=True) if v['role'] == 'border']

    paths_and_nodes = []

    for i in paths:
        a_l = [(u, v) for u, v, e in g_nw.edges(data=True) if 'pathid' in e and i in e['pathid']]
        l = [i]
        for j in a_l:
            l = l + list(j)
        l = [*set(l)]

        SG = g_nw.subgraph(l)

        pdr = np.average(get_pdr_arr(loader, list(SG.nodes())))
        if SG.in_edges():
            paths_and_nodes.append({'path': i,
                                    'node_num': len(SG.nodes()),
                                    'avg_in_edges': np.average([len(SG.in_edges(n)) for n in l if SG.in_edges(n)]),
                                    'avg_out_edges': np.average([len(g_nw.out_edges(n))
                                                                 for n in l if g_nw.out_edges(n)]),
                                    'avg_distance': np.average([nx.shortest_path_length(SG, target=i, source=n)
                                                              for n in SG.nodes() if n != i]),
                                    'avg_leaf_distance': np.average([nx.shortest_path_length(SG, target=i, source=n)
                                                                     for n in SG.nodes() if not SG.in_edges(n)]),
                                    'edge_entropy': entropy([SG.in_edges(n) for n in l if SG.in_edges(n)]),
                                    'pdr': pdr})
        else:
            paths_and_nodes.append({'path': i,
                                    'node_num': len(SG.nodes()),
                                    'avg_in_edges': 0,
                                    'avg_out_edges': 1,
                                    'avg_distance': 0,
                                    'avg_leaf_distance': 0,
                                    'edge_entropy': 0,
                                    'pdr': pdr})
    return paths_and_nodes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='path_prop', description='Analyze path properties', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')
    parser.add_argument('-H', '--header', action='store_true', dest='header')
    parser.add_argument('-P', '--plot', action='store_true', dest='plot')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)
    paths_and_nodes = []
    for i in loader['runs']:
        paths_and_nodes = paths_and_nodes + get_path_stat(i)

    if args.header:
        print('filename#avg.node.num#avg.edge.num#avg.len')
    print(str(args.filename)+'#'+str(np.average([i['node_num'] for i in paths_and_nodes]))+'#' +
          str(np.average([i['avg_edges'] for i in paths_and_nodes]))+'#' +
          str(np.average([i['avg_length'] for i in paths_and_nodes])))

    node_num = [i['node_num'] for i in paths_and_nodes]
    edge_num = [i['avg_edges'] for i in paths_and_nodes]
    length = [i['avg_length'] for i in paths_and_nodes]
    pdr = [i['pdr'] for i in paths_and_nodes]
    stat_arr = np.array([node_num, edge_num, length, pdr])
    #print('node num, edge num, length, pdr')
    #print(np.corrcoef(stat_arr))

    if args.plot:
        plt.subplot(311)
        plt.title('Node number')
        bins = np.arange(np.min(node_num), np.max(node_num), 1)
        plt.hist(node_num, bins)

        plt.subplot(312)
        plt.title('Edge number')
        bins = np.arange(np.min(edge_num), np.max(edge_num), 0.1)
        plt.hist(edge_num, bins)

        plt.subplot(313)
        plt.title('Length')
        bins = np.arange(np.min(length), np.max(length), 0.1)
        plt.hist(length, bins)

        plt.tight_layout()

        plt.show()


    #  ___ _     _
    # | _ \ |___| |_
    # |  _/ / _ \  _|
    # |_| |_\___/\__|
#    node_color = [role_to_color(nx.get_node_attributes(g_nw, 'role')[i])
#                  for i in nx.get_node_attributes(g_nw, 'role')]
#
#    node_size = [700 if nx.get_node_attributes(g_nw, 'master')[i] else 300
#                 for i in nx.get_node_attributes(g_nw, 'master')]
#
#
#    plt.gca().set_axis_off()
#
#    #    pos = graphviz_layout(g_nw, prog="dot")
#
#    nx.draw(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size, with_labels=True,
#            edgecolors='k', linewidths=1)
#    #nx.draw(g_nw, pos=pos, node_color=node_color, node_size=node_size, with_labels=True,
#    #        edgecolors='k', linewidths=1)
#
#    edge_labels = {}
#    for u, v, e in g_nw.edges.data('pathid'):
#        if e:
#            edge_labels[(u, v)] = str(','.join(str(i) for i in e))
#
#    nx.draw_networkx_edge_labels(g_nw, nx.get_node_attributes(g_nw, 'pos'), edge_labels=edge_labels)
#    plt.gca().set_aspect('equal')
#
#    plt.tight_layout()
##    plt.savefig('graph.pdf', transparent=True, bbox_inches='tight', pad_inches=0)
#    plt.show()
