#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
import matplotlib

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
    parser = argparse.ArgumentParser(prog='plot_msr2mrp_network', description='Plot an MS-R2MRP network', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    g_nw = nx.DiGraph()

    if 'runs' in loader:
        data = loader['runs'][0]['loc_pdr']
    else:
        data = loader['loc_pdr']

    for i in data:
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

    node_size = [700 if nx.get_node_attributes(g_nw, 'master')[i] else 300
                 for i in nx.get_node_attributes(g_nw, 'master')]

    plt.subplot(212)
    #plt.gca().set_title('(c)', loc='left')
    plt.gca().set_axis_off()
#    nx.draw(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size, with_labels=True,
#            edgecolors='k', linewidths=1)

    nodes = []
    for u, v, e in g_nw.edges(data=True):
        if 'pathid' in e and 11 in e['pathid']:
            nodes.append(u)
            nodes.append(v)
    nodes = list(set(nodes))
    sub_g_nw=g_nw.subgraph(nodes)

    edge_labels = {}

    for u, v, e in sub_g_nw.edges.data('pathid'):
        if e:
            edge_labels[(u, v)] = str(','.join(str(i) for i in e))

    nx.draw_networkx_edge_labels(sub_g_nw, nx.get_node_attributes(sub_g_nw, 'pos'), edge_labels=edge_labels)
    plt.gca().set_aspect('equal')

    nx.draw(sub_g_nw)
#    nx.draw(sub_g_nw, pos=nx.get_node_attributes(sub_g_nw, 'pos'), node_color=node_color, node_size=node_size, with_labels=True,
#            edgecolors='k', linewidths=1)

    plt.subplot(222)
    plt.gca().set_title('(b)', loc='left')
    plt.gca().set_axis_off()
    node_size = [500 if nx.get_node_attributes(g_nw, 'master')[i] else 200
                 for i in nx.get_node_attributes(g_nw, 'master')]
    nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size,
                           edgecolors='k', linewidths=1)
    nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), font_size=8)

    edge_list = []

    for (v, w) in g_nw.edges():
        if g_nw.get_edge_data(v, w)['secl']:
            edge_list.append((v, w))

    nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), edgelist=edge_list)

    plt.gca().set_aspect('equal')

    plt.subplot(221)
    plt.gca().set_title('(a)', loc='left')
    plt.gca().set_axis_off()

    nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size,
                           edgecolors='k', linewidths=1)
    nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), font_size=8)

    edge_list = []
    for (v, w) in g_nw.edges():
        if not g_nw.get_edge_data(v, w)['secl']:
            edge_list.append((v, w))

    nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), edgelist=edge_list)

    plt.gca().set_aspect('equal')
    plt.tight_layout()
    plt.savefig('graph.pdf', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.show()
