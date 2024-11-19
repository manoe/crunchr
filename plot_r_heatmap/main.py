#!/bin/env python3

import networkx as nx
import argparse
import yaml
import logging
logger = logging.getLogger(__name__)
import itertools as it
import pandas as pd
import sys

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
                                nw.add_edge(node['node'], re['node'], secl=re['secl'], engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], secl=re['secl'], engine=engine['engine'])
                roles.append((engine['engine'], engine['role']))
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw


def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_r_heatmap', description='Plot MsR2MRP network with spatial heatmap representing route numbers', epilog=':-(')
    parser.add_argument('-i','--input',dest='filename', help='Input filenames', nargs='*')
    parser.add_argument('-b', '--base', dest='base_filename', help='Base filename to plot')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    stream = open(args.base_filename, 'r')
    loader = yaml.safe_load(stream)
    data = get_data_from_loader(loader)
    nw = construct_graph(data)