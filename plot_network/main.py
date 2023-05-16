#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_network', description='Plot network', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('-d', '--data',
                        action='store_true', dest='data')
    parser.add_argument('-n', '--no-header',
                        action='store_true', dest='no_header')
    parser.add_argument('-g', '--gap', dest='gap')
    parser.add_argument('-s', '--sheet',
                        action='store_true', dest='sheet')
    parser.add_argument('-r', '--remove-outlier',
                        action='store_true', dest='remove_outlier')

    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

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

    node_color = [role_to_color(nx.get_node_attributes(g_nw, 'role')[i])
                  for i in nx.get_node_attributes(g_nw, 'role')]

    node_size = [700 if nx.get_node_attributes(g_nw, 'master')[i] else 400
                 for i in nx.get_node_attributes(g_nw, 'master')]

    plt.subplot(133)

    nx.draw(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size, with_labels=True,
            edgecolors='k', linewidths=2)

    edge_labels = {}
    for u, v, e in g_nw.edges.data('pathid'):
        if e:
            edge_labels[(u, v)] = str(','.join(str(i) for i in e))

    nx.draw_networkx_edge_labels(g_nw, nx.get_node_attributes(g_nw, 'pos'), edge_labels=edge_labels)
    plt.box(False)
    plt.subplot(132)

    nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size,
                           edgecolors='k', linewidths=2)
    nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'))

    edge_list = []

    for (v, w) in g_nw.edges():
        if g_nw.get_edge_data(v, w)['secl']:
            edge_list.append((v, w))

    nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), edgelist=edge_list)


    plt.box(False)
    plt.subplot(131)

    nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size,
                           edgecolors='k', linewidths=2)
    nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'))

    edge_list = []
    for (v, w) in g_nw.edges():
        if not g_nw.get_edge_data(v, w)['secl']:
            edge_list.append((v, w))

    nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), edgelist=edge_list)
    plt.box(False)
    plt.show()
