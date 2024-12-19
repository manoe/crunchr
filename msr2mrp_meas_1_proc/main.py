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
        f_nw = filter_edges(nw,'pathid', p)
        nodes.append(list(nx.descendants(f_nw,node)))

    for i in range(len(nodes), 1 ,-1):
        for j in it.combinations([set(l) for l in nodes], i):
            isect = [set.intersection(*c) for c in it.combinations([set(l) for l in j], 2)]
            if all(map(lambda s: not len(s), isect)):
                return i/len(nodes)

    logger.debug('No disjoint path: ' + str(nodes))
    return 0


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


def get_sinks(nw, n):
    return set( e[2]['engine'] for e in nw.out_edges(n, data=True) )


def construct_dataframe(results):
    out_data = pd.DataFrame()
    for i_idx, i in enumerate(results):
        for j_idx, j in enumerate(i):
            out_data.at[i_idx,j[0]]=j[1]
    return out_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='msr2mrp_meas_1_proc', description='Process measurement data related to measurement 1', epilog=':-(')
    parser.add_argument('filename', help='Input filenames', nargs='*')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    dmp_results = []
    rm_results = []
    sink_results = []
    iso_arr = []

    for idx,filename in enumerate(args.filename):
        stream = open(filename, 'r')
        print(str(filename)+' '+str(idx+1)+'/'+str(len(args.filename)))
        loader = yaml.safe_load(stream)

        data = get_data_from_loader(loader)
        nw = construct_graph(data)


        engines = [ (n, len(get_sinks(nw,n))) for n in get_nodes_based_on_role(nw, 'external') ]
        sink_results.append(engines)

        iso_arr = [ (n, len(nx.get_node_attributes(nw, 'roles')[n]) ) for n in nw.nodes() ]

        f_nw = filter_graph(nw, filter=['internal','central'])
        dis_arr = [ (n, check_disjointness(f_nw, n)) for n in get_nodes_based_on_role(nw, 'external') if len(f_nw.out_edges(n)) >1 ]
        dmp_results.append(dis_arr)

        r_num_arr = [ (n, len(f_nw.out_edges(n))) for n in get_nodes_based_on_role(nw, 'external')]
        rm_results.append(r_num_arr)

        # Single path nodes!!!

    construct_dataframe(dmp_results).to_pickle(args.out + '_dmp.pickle')
    construct_dataframe(rm_results).to_pickle(args.out + '_rm.pickle')
    construct_dataframe(sink_results).to_pickle(args.out + '_sink.pickle')
    construct_dataframe(sink_results).to_pickle(args.out + '_iso.pickle')
