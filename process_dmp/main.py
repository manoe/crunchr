#!/bin/env python3

import networkx as nx
import argparse
import yaml
import logging
logger = logging.getLogger(__name__)
import itertools as it
import pandas as pd


def construct_graph(run):
    nw = nx.MultiDiGraph()
    for node in run:
        nw.add_node(node['node'], master=node['master'], pos=[node['x'], node['y']])
        if 'engines' in node:
            roles = []
            for engine in node['engines']:
                if 'routing_table' in engine:
                    for re in engine['routing_table']:
                        if engine['role'] == 'external':
                            pathid = [pe['pathid'] for pe in re['pathid']]
                            secl = False
                            for k in re['pathid']:
                                if k['secl']:
                                    secl = True
                            nw.add_edge(node['node'], re['node'], pathid=pathid, secl=secl, engine=engine['engine'])
                        else:
                            nw.add_edge(node['node'], re['node'], secl=re['secl'], engine=engine['engine'])
                roles.append((engine['engine'], engine['role']))
            nx.set_node_attributes(nw, {node['node']: roles}, 'roles')
    return nw


def get_nodes_based_on_role(nw, role):
    roles = nx.get_node_attributes(nw, name='roles')
    out_nodes = set()
    for n in roles.keys():
        for r in roles[n]:
            if r[1] == role:
                out_nodes.add(n)
    return list(out_nodes)


def filter_graph(nw, filter):
    roles = nx.get_node_attributes(nw, name='roles')
    rm_nodes = []
    for node in nw.nodes():
        for f in filter:
            for r in roles[node]:
                if f == r[1]:
                    logger.debug(str(node)+' removed due to '+str(r)+' in filter '+str(f))
                    rm_nodes.append(node)
    logger.debug('Nodes to remove: '+str(rm_nodes))
    nw.remove_nodes_from(rm_nodes)
    return nw


def get_nodes_patids(nw,node):
    pathids = []
    for e in nw.out_edges([node], data=True):
        if 'pathid' in e[2]:
            pathids+=e[2]['pathid']
        else:
            logger.debug('Edge without pathid: ' + str(e))
    return pathids


def check_disjointness(nw, node):
    nodes = []

    for p in get_nodes_patids(nw,node):
        f_nw = filter_edges(nw,'pathid',p)
        nodes.append(list(nx.descendants(f_nw,node)))
    return [set(c[0]) & set(c[1]) for c in it.combinations(nodes,2) ]


def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


def filter_edges(nw, prop, value):
    f_nw = nx.MultiDiGraph(nw)
    f_nw.remove_edges_from(list(f_nw.edges()))
    for edge in nw.edges(data=True):
        if prop not in edge[2]:
            logger.debug('Property '+str(prop)+' not present in '+str(edge))
        elif value in edge[2][prop]:
            f_nw.add_edges_from([edge])
    f_nw.remove_nodes_from(list(nx.isolates(f_nw)))
    return f_nw


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filenames', nargs='*')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    args = parser.parse_args()

    results = []

    for idx,filename in enumerate(args.filename):
        stream = open(filename, 'r')
        print(str(filename)+' '+str(idx+1)+'/'+str(len(args.filename)))
        loader = yaml.safe_load(stream)

        data = get_data_from_loader(loader)
        nw = construct_graph(data)
        f_nw = filter_graph(nw, filter=['internal','central'])

        dis_arr = [ check_disjointness(f_nw, n) for n in get_nodes_based_on_role(nw, 'external') ]
        dis_rat_arr = [ len([j for j in i if len(j) > 0])/len(i) if len(i) > 0 else 1 for i in dis_arr]
        results.append(len([i for i in dis_rat_arr if i == 1])/len(dis_rat_arr))
        # Single path nodes!!!

    pd.Series(results).to_pickle(args.out+'.pickle')

