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

def calc_aspect_ratio(nw):
    max_d = max(list(nx.get_node_attributes(nw, 'pos').values()), key=np.linalg.norm)
    return max_d[1]/max_d[0]

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

    node_size = [300 if nx.get_node_attributes(g_nw, 'master')[i] else 200
                 for i in nx.get_node_attributes(g_nw, 'master')]

    edge_lists = [[], [], []]
    for (v, w) in g_nw.edges():
        edge_lists[0].append((v, w))
        if not g_nw.get_edge_data(v, w)['secl']:
            edge_lists[1].append((v, w))
        else:
            edge_lists[2].append((v, w))
    fig, axs = plt.subplots(1, 3, figsize=(12, 12))
    for idx, ax in enumerate(axs.flat):
        ax.axis('off')
        ax.set_box_aspect(calc_aspect_ratio(g_nw))
        nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), node_color=node_color, node_size=node_size,
                           edgecolors='k', linewidths=1, ax=ax)
        nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), font_size=8, ax=ax)
        nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), edgelist=edge_lists[idx], ax=ax)
    plt.tight_layout()
    plt.show()
