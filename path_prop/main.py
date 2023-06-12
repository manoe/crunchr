#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
from scipy.stats import entropy
import matplotlib as mpl
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
        a_l = [(u, v, e) for u, v, e in g_nw.edges(data=True) if 'pathid' in e and i in e['pathid']]

        SG = nx.DiGraph()
        SG.add_node(i)
        SG.add_edges_from(a_l)

        pdr = np.average(get_pdr_arr(loader, list(SG.nodes())))
        if len(SG.in_edges()) > 1:
            paths_and_nodes.append({'path': i,
                                    'node_num': len(SG.nodes()),
                                    'avg_in_edges': np.average([len(SG.in_edges(n)) for n in SG.nodes() if SG.in_edges(n)]),
                                    'avg_out_edges': np.average([len(g_nw.out_edges(n))
                                                                 for n in SG.nodes() if g_nw.out_edges(n)]),
                                    'avg_distance': np.average([nx.shortest_path_length(SG, target=i, source=n)
                                                                for n in SG.nodes() if n != i]),
                                    'avg_leaf_distance': np.average([nx.shortest_path_length(SG, target=i, source=n)
                                                                     for n in SG.nodes() if not SG.in_edges(n)]),
                                    'edge_entropy': entropy([len(SG.in_edges(n))/len(SG.in_edges()) for n in SG.nodes()
                                                             if SG.in_edges(n)])/entropy([1/len(SG.in_edges())]*len(SG.in_edges())),
                                    'edge_arr': [len(SG.in_edges(n)) for n in SG.nodes() if SG.in_edges(n)],
                                    'pdr': pdr})
        else:
            paths_and_nodes.append({'path': i,
                                    'node_num': len(SG.nodes()),
                                    'avg_in_edges': 0,
                                    'avg_out_edges': 1,
                                    'avg_distance': 0,
                                    'avg_leaf_distance': 0,
                                    'edge_entropy': 1,
                                    'edge_arr': [len(SG.in_edges(n)) for n in SG.nodes() if SG.in_edges(n)],
                                    'pdr': pdr})
    return paths_and_nodes


def get_all_path_pdr(loader):
    pdr_arr = []
    for i in loader['runs']:
        for j in i['pdr']:
            for k in i['loc_pdr']:
                if k['node'] == j and ( k['role'] == 'border' or k['role'] == 'external'):
                    pdr_arr.append( i['pdr'][j]['pkt_recv']/i['pdr'][j]['pkt_sent'] )
    return np.average(pdr_arr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='path_prop', description='Analyze path properties', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')
    parser.add_argument('-H', '--header', action='store_true', dest='header')
    parser.add_argument('-P', '--plot', action='store_true', dest='plot')
    parser.add_argument('-C', '--correlation', action='store_true', dest='corr')
    parser.add_argument('-S', '--stat', action='store_true', dest='stat')
    parser.add_argument('-R', '--pdr', action='store_true', dest='pdr')
    parser.add_argument('-E', '--edge', action='store_true', dest='edge')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    if args.pdr:
        print(get_all_path_pdr(loader))
        exit(0)

    paths_and_nodes = []
    for i in loader['runs']:
        paths_and_nodes = paths_and_nodes + get_path_stat(i)

    def fun(x): return str(np.average([i[x] for i in paths_and_nodes]))

    if args.stat:
        if args.header:
            print('filename#avg.node.num#avg.in.edge#avg.out.edge#avg.dist#avg.leaf.dist#edge.entr#pdr')
        print(str(args.filename)+'#'+fun('node_num')+'#' + fun('avg_in_edges')+'#'+fun('avg_out_edges')+'#'
              +fun('avg_distance')+'#'+fun('avg_leaf_distance')+'#'+fun('edge_entropy')+'#'+fun('pdr'))

    node_num = [i['node_num'] for i in paths_and_nodes]
    in_edge_num = [i['avg_in_edges'] for i in paths_and_nodes]
    out_edge_num = [i['avg_out_edges'] for i in paths_and_nodes]
    distance = [i['avg_distance'] for i in paths_and_nodes]
    leaf_distance = [i['avg_leaf_distance'] for i in paths_and_nodes]
    edge_entr = [i['edge_entropy'] for i in paths_and_nodes]
    pdr = [i['pdr'] for i in paths_and_nodes]
    stat_arr = np.array([node_num, in_edge_num, out_edge_num, distance, leaf_distance, edge_entr, pdr])

    if args.edge:
        plt.subplot(121)
        plt.scatter([i['edge_entropy'] for i in paths_and_nodes if i['node_num'] > 2], [i['pdr'] for i in paths_and_nodes if i['node_num'] > 2], c=[i['node_num']/max(node_num) for i in paths_and_nodes if i['node_num'] > 2], cmap=mpl.colormaps['hot'])
        plt.xlabel('Entropy')
        plt.ylabel('E2e PDR')
        plt.subplot(122)
        plt.scatter([i['node_num'] for i in paths_and_nodes if i['edge_entropy'] == 1 and i['node_num'] > 2],
                    [i['pdr'] for i in paths_and_nodes if i['edge_entropy'] == 1 and i['node_num'] > 2])
        plt.xlabel('Node number')
        plt.ylabel('E2e PDR')
        plt.show()


    if args.corr:
        header = [args.filename,'node_num','in_edge_num','out_edge_num','distance','leaf_distance','edge_entr','pdr']
        corr_stat = np.corrcoef(stat_arr)
        for i in header:
            print(i+'#',end='')
        print()
        for i in np.arange(0,len(stat_arr)):
            print(header[i+1]+'#',end='')
            for j in corr_stat[i]:
                print(str(j)+'#',end='')
            print()

    #  ___ _     _
    # | _ \ |___| |_
    # |  _/ / _ \  _|
    # |_| |_\___/\__|
    if args.plot:
        plt.subplot(231)
        plt.title('Node number')
        bins = np.linspace(np.min(node_num), np.max(node_num), 20)
        plt.hist(node_num, bins)
        plt.subplot(232)
        plt.title('Entropy - all paths')
        edge_entr = [i['edge_entropy'] for i in paths_and_nodes]
        bins = np.linspace(np.min(edge_entr), np.max(edge_entr), 20)
        plt.hist(edge_entr, bins)
        plt.subplot(233)
        plt.title('Entropy - single nodes excluded')
        edge_entr = [i['edge_entropy'] for i in paths_and_nodes if i['node_num'] > 1]
        bins = np.linspace(np.min(edge_entr), np.max(edge_entr), 20)
        plt.hist(edge_entr, bins)

        plt.subplot(234)
        plt.title('Entropy - single and double nodes excluded')
        edge_entr = [i['edge_entropy'] for i in paths_and_nodes if i['node_num'] > 2]
        bins = np.linspace(np.min(edge_entr), np.max(edge_entr), 20)
        plt.hist(edge_entr, bins)

        plt.subplot(235)
        knots = [i['node_num'] for i in paths_and_nodes if i['edge_entropy'] == 0]
        plt.title('Knot node number')
        plt.hist(knots, np.linspace(np.min(knots), np.max(knots), 10))

        plt.subplot(236)
        plt.title('Non-knot node number')
        non_knot = [i['node_num'] for i in paths_and_nodes if i['edge_entropy'] != 0]
        plt.hist(non_knot, np.linspace(np.min(non_knot), np.max(non_knot), 10))

        plt.tight_layout()
        plt.show()

        #plt.subplot(312)
        #plt.title('Edge number')
        #bins = np.arange(np.min(edge_num), np.max(edge_num), 0.1)
        #plt.hist(edge_num, bins)

        #plt.subplot(313)
        #plt.title('Length')
        #bins = np.arange(np.min(length), np.max(length), 0.1)
        #plt.hist(length, bins)





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
