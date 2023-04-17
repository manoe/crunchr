#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import sys
import networkx as nx

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

    parser.add_argument('filename')

    args = parser.parse_args()
    stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)

    g_nw = nx.DiGraph()

    for i in loader['loc_pdr']:
        g_nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if i['role'] == 'external':
                    pathid = [k['pathid'] for k in j['pathid']]
                    g_nw.add_edge(i['node'], j['node'], pathid=pathid, secl=j['secl'])
                else:
                    g_nw.add_edge(i['node'], j['node'], secl=j['secl'])

    nx.draw(g_nw, nx.get_node_attributes(g_nw, 'pos'))
    plt.draw()
    plt.show()