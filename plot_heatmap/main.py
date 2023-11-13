#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
import math

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_heatmap', description='Plot PDR heatmap', epilog=':-(')
    parser.add_argument('-r', '--routing', dest='routing', choices=['hdmrp', 'efmrp', 'shmrp'],
                        default='shmrp')
    parser.add_argument('filename')
    args = parser.parse_args()

    stream = open(args.filename, 'r')
    loader = yaml.safe_load(stream)
    size = int(math.sqrt(len(loader['pdr'])))

    pdr_map = np.ndarray(shape=(size*size, 1))
    for i in loader['pdr']:
        if 'report_pdr' in i:
            pdr_map[i['node']] = i['report_pdr']
        else:
            pdr_map[i['node']] = 0
    print(size)
    color_list = list(pdr_map)

    pdr_map = np.reshape(pdr_map, (size, size))

    print(pdr_map)

    plt.imshow(pdr_map)

    g_nw = nx.DiGraph()

    if args.routing == 'shmrp' or args.routing == 'hdmrp':
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
    elif args.routing == 'efmrp':

        g_nw = nx.MultiDiGraph()
        for i in loader['loc_pdr']:
            g_nw.add_node(i['node'], pos=[i['x'], i['y']])
            if 'routing_table' in i:
                for re in i['routing_table']:
                    #
                    if 'next_hop' in re and re['status'] == 'AVAILABLE':
                        g_nw.add_edge(i['node'], re['next_hop'], prio=re['prio'], origin=re['origin'])

    node_color = [str(loader['pdr'][i]['report_pdr']) if 'report_pdr' in loader['pdr'][i] else 0 for i in list(g_nw)]
    nx.draw(nx.DiGraph(g_nw), pos=nx.get_node_attributes(g_nw, 'pos'), edgecolors='k', linewidths=1, node_color=node_color)
    plt.title(args.filename.split('/')[-1])
    plt.show()
