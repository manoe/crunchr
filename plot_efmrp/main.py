#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx
import matplotlib



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_efmrp', description='Plot EFMRP network', epilog=':-(')
    parser.add_argument('-i', '--image',
                        action='store_true', dest='image')
    parser.add_argument('filename', help='use ``-\'\' for stdin')

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    graph = nx.MultiDiGraph()

    for i in loader['loc_pdr']:
        graph.add_node(i['node'], pos=[i['x'], i['y']])
        if 'routing_table' in i:
            for re in i['routing_table']:
                #
                if 'next_hop' in re and re['status'] == 'AVAILABLE':
                    graph.add_edge(i['node'], re['next_hop'], prio=re['prio'], origin=re['origin'])

    pri_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['prio'] == 1))

    sec_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['prio'] == 2))

    plt.subplot(131)
    nx.draw(graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.subplot(132)
    nx.draw(pri_graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.subplot(133)
    nx.draw(sec_graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.show()

