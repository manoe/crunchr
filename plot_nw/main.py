#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
import math
#from matplotlib.patches import Rectangle


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
    parser = argparse.ArgumentParser(prog='plot_heatmap', description='Plot PDR heatmap', epilog=':-(')
    parser.add_argument('-r', '--routing', dest='routing', choices=['hdmrp', 'efmrp', 'shmrp'],
                        default='shmrp')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-nd', '--no-dead', dest='no_dead', action='store_true')
    parser.add_argument('-u', '--unconnected', dest='unconn', action='store_true')
    parser.add_argument('-b', '--box', dest='box', action='store_true')
    parser.add_argument('-nc', '--no-color', dest='no_color', action='store_true')
    parser.add_argument('filenames', nargs=3)
    args = parser.parse_args()

    fig, axs = plt.subplots(nrows=3)
    ax = axs.ravel()

    for idx, filename in enumerate(args.filenames):
        stream = open(filename, 'r')
        loader = yaml.safe_load(stream)
        if 'runs' in loader:
            data_source = loader['runs'][0]
        else:
            data_source = loader
        size = int(math.sqrt(len(data_source['pdr'])))

        pdr_map = np.ndarray(shape=(size*size, 1))
        for i in data_source['pdr']:
            if 'report_pdr' in i:
                pdr_map[i['node']] = i['report_pdr']
            else:
                pdr_map[i['node']] = 0
        #print(size)
        color_list = list(pdr_map)

        pdr_map = np.reshape(pdr_map, (size, size))

        #print(pdr_map)

        #plt.imshow(pdr_map)

        g_nw = nx.DiGraph()

        if args.routing == 'shmrp' or args.routing == 'hdmrp':
            for i in data_source['loc_pdr']:
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
            if args.no_dead:
                rm_nodes = [node for node, data in g_nw.nodes(data=True) if data['state'] == 'DEAD']
                g_nw.remove_nodes_from(rm_nodes)

        elif args.routing == 'efmrp':
            g_nw = nx.MultiDiGraph()
            for i in data_source['loc_pdr']:
                g_nw.add_node(i['node'], pos=[i['x'], i['y']])
                if 'routing_table' in i:
                    for re in i['routing_table']:
                        #
                        if 'next_hop' in re and re['status'] == 'AVAILABLE':
                            g_nw.add_edge(i['node'], re['next_hop'], prio=re['prio'], origin=re['origin'])

        if args.unconn:
            print(len([i for i in g_nw.nodes() if g_nw.out_degree(i) == 0 and i != 0]))
            exit(0)

        if args.event:
            target_pdr = 'event_pdr'
        else:
            target_pdr = 'report_pdr'

        if args.box:
            ax = plt.gca()
            ax.add_patch(Rectangle((70, 47), 65, 65, color='tab:red'))

        node_color = [float(data_source['pdr'][i][target_pdr]) if target_pdr in data_source['pdr'][i] else 0 for i in list(g_nw)]
        node_color = [role_to_color(nx.get_node_attributes(g_nw, 'role')[i])
                      for i in nx.get_node_attributes(g_nw, 'role')]

        #print(node_color)
    #    for i in data_source['loc_pdr']:
    #        if i['state'] == 'DEAD':
    #            node_color[i['node']] = 0
        if args.no_color:
            nx.draw(nx.DiGraph(g_nw), pos=nx.get_node_attributes(g_nw, 'pos'), edgecolors='k', linewidths=1, with_labels=True)
        else:
            nx.draw(nx.DiGraph(g_nw), pos=nx.get_node_attributes(g_nw, 'pos'), edgecolors='k', linewidths=1, node_color=node_color, with_labels=True, ax=ax[i])


    #plt.title(args.filename.split('/')[-1])
    plt.tight_layout()
    plt.show()
