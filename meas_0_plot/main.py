#!/bin/env python3

import argparse
import copy
import logging
import matplotlib

logger = logging.getLogger(__name__)
import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec
from matplotlib import colormaps
from matplotlib import cm
import numpy as np
import networkx as nx
import yaml

from matplotlib import rcParams
rcParams['font.family'] = ['serif']
rcParams['font.serif'] = ['Times New Roman']

def construct_graph(run):
    nw = nx.MultiDiGraph()
    for node in run:
        nw.add_node(node['node'], master=node['master'], pos=[node['x'], node['y']])
        if 'engines' in node:
            roles = []
            for engine in node['engines']:
                if 'routing_table' in engine:
                    for re in engine['routing_table']:
                        pathid = [pe['pathid'] for pe in re['pathid']]
                        if engine['role'] == 'external':
                            secl = False
                            for k in re['pathid']:
                                if k['secl']:
                                    secl = True
                            nw.add_edge(node['node'], re['node'], pathid=pathid, secl=secl, engine=engine['engine'])
                        elif engine['role'] == 'border':
                            if re['node'] in pathid:
                                nw.add_edge(node['node'], re['node'], pathid=pathid, engine=engine['engine'])
                            else:
                                # ulgy hack
                                nw.add_edge(node['node'], re['node'], pathid=[0], secl=re['secl'], engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], pathid=[], secl=re['secl'], engine=engine['engine'])
                roles.append((engine['engine'], engine['role']))
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meas_0_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('-n1', '--network1', dest='network1', type=str, help='Network 1')
    parser.add_argument('-n2', '--network2', dest='network2', type=str, help='Network 2')
    parser.add_argument('-s1', '--sensor1', dest='sensor1', type=int, help='Sensor 1', nargs='?')
    parser.add_argument('-s2', '--sensor2', dest='sensor2', type=int, help='Sensor 2', nargs='?')
    parser.add_argument('-p1', '--path1', dest='path1', type=int, help='Path 1', nargs='?')
    parser.add_argument('-p2', '--path2', dest='path2', type=int, help='Path 2', nargs='?')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('-o', '--out', dest='out', type=str,  help='Out file', default='out')
    args = parser.parse_args()

    title = ['('+i+')' for i in 'abcd']

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    #fig, axs = plt.subplots(nrows=2, ncols=1, layout='compressed', figsize=(12, 15), height_ratios=[9, 7])

    gs = matplotlib.gridspec.GridSpec(2, 3, height_ratios=[1, 1.4],
                                      width_ratios=[1, 3, 1])

    fig = plt.figure(figsize=(24, 20))
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 1])
    axs = [ax1, ax2]
    for nw_filename, ax, ratio, anchor, sensor, path in zip([args.network1]+[args.network2], axs,[1,1],['S','N'],[args.sensor1, args.sensor2],[args.path1, args.path2]):
        logger.debug('Filename: ' + str(nw_filename))
        stream = open(nw_filename, 'r')
        loader = yaml.safe_load(stream)
        nw = construct_graph(loader)
        roles = nx.get_node_attributes(nw, 'roles')
        colors = [ 'tab:blue' if 'external' in i[0][1] else 'tab:brown' if 'border' in i[0][1] else 'tab:pink' for i in nx.get_node_attributes(nw, 'roles').values() ]

        if sensor is not None:
            des = [sensor] + list(nx.descendants(nw, sensor))
            n_alpha = [ 1 if i in des else 0.5 for i in nw ]

            if path is not None:
                t_nw = copy.deepcopy(nw)
                for i in nw.edges(data=True):
                    if not (path in i[2]['pathid'] or 0 in i[2]['pathid']):

                        t_nw.remove_edge(i[0], i[1])
                s_nw = nx.subgraph(t_nw, [sensor] + list(nx.descendants(t_nw, sensor)))
                pathids = nx.get_edge_attributes(s_nw, 'pathid')
                edges = nx.get_edge_attributes(nw, 'pathid')
                e_alpha = [ 1 if e in pathids else 0.1 for e in edges] # and path in pathids[e]
                nodes_on_path = set([ i for e in edges if e in pathids for i in e]) # and path in pathids[e]
                n_alpha = [ 1 if i in nodes_on_path else 0.5 for i in nw ]
            else:
                e_alpha=1
        else:
            n_alpha=1
            e_alpha=1

        pos = nx.get_node_attributes(nw, 'pos')

        nx.draw_networkx_nodes(nw, ax=ax, pos=pos, alpha=n_alpha, node_color=colors)
        nx.draw_networkx_labels(nw, ax=ax, pos=pos)
        nx.draw_networkx_edges(nw, ax=ax, pos=pos, alpha=e_alpha)
        #nx.draw_networkx_edge_labels(nw, ax=ax, pos=pos, edge_labels=nx.get_edge_attributes(nw, 'pathid'))
        ax.set_aspect(ratio,anchor=anchor) # lekérni az utolsó csomópont koordinátáit
        ax.axis('off')
    plt.show()
    fig.savefig(args.out+".pdf", bbox_inches='tight')
