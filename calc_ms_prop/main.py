#!/bin/env python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import pandas as pd
import shelve


def shelve_out(filename, keys):
    my_shelf = shelve.open(filename, 'n')  # 'n' for new
    for key in keys:
        #print('key: '+str(key))
        try:
            my_shelf[key] = globals()[key]
        except TypeError:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            print('ERROR shelving: {0}'.format(key))
        except KeyError:
            print('ERROR shelving: {0}'.format(key))
        except:
            print('ERROR')
    my_shelf.close()


def shelve_in(filename):
    my_shelf = shelve.open(filename)
    for key in my_shelf:
        globals()[key] = my_shelf[key]
    my_shelf.close()

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


def calc_avg_path_num(run):
    pn_arr = []
    for node in run['loc_pdr']:
        if node['role'] == 'external' and 'routing_table' in node:
            pn_arr.append(len(node['routing_table']))
    return np.average(pn_arr)


def calc_avg_pdr(run):
    dead_nodes = []
    if args.no_dead:
        dead_nodes = [i['node'] for i in run['loc_pdr'] if i['state'] == 'DEAD']
        #print(dead_nodes)
    ring_nodes = []
    if args.external:
        ring_nodes = [i['node'] for i in run['loc_pdr'] if i['role'] != 'external']

    pdr_arr = []
    if args.event:
        pdr_arr = [node['event_pdr'] for node in run['pdr'] if 'event_pdr' in node
                   and node['node'] not in dead_nodes and node['node'] not in ring_nodes]
    else:
        pdr_arr = [node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node
                   and node['node'] not in dead_nodes and node['node'] not in ring_nodes]
    #print(pdr_arr)
    return np.average(pdr_arr)


def construct_graph(run):
    nw = nx.DiGraph()
    pdr_set = {i['node']: i['report_pdr'] for i in run['pdr'] if 'report_pdr' in i}
    for i in run['pdr']:
        if 'report_pdr' not in i:
            pdr_set[i['node']] = 0

    for i in run['loc_pdr']:
        nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'], pdr=pdr_set[i['node']])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if i['role'] == 'external':
                    pathid = [k['pathid'] for k in j['pathid']]
                    secl = False
                    for k in j['pathid']:
                        if k['secl']:
                            secl = True
                    nw.add_edge(i['node'], j['node'], pathid=pathid, secl=secl)
                else:
                    nw.add_edge(i['node'], j['node'], secl=j['secl'])
    return nw



def calc_path_stat(run):
    nw = construct_graph(run)
    series = []
    pathid = 0

    def filter_edge_pathid(n1,n2):
        if 'pathid' in nw[n1][n2]:
            if nw[n1][n2]['pathid'] == pathid:
                return True
            else:
                return False
        else:
            return True

    for node in nw.nodes():
        for edge in nw.out_edges(node):
            if 'pathid' in nw.get_edge_data(*edge):
                pathid = nw.get_edge_data(*edge)['pathid']
                #print('node: '+str(node)+' pathid: '+str(pathid))
                subgraph = nx.subgraph_view(nw, filter_edge=filter_edge_pathid)
                try:
                    path_list = nx.shortest_path(subgraph, node, 0)  # ugly
                except nx.NetworkXNoPath:
                    continue
            else:
                try:
                    path_list = nx.shortest_path(nw, node, 0)
                except nx.NetworkXNoPath:
                    continue
            path_list_arr = []
            for idx in range(1, len(path_list)):
                path_list_arr.append([path_list[idx-1],path_list[idx]])

            d = [np.linalg.norm(np.subtract(nx.get_node_attributes(nw, 'pos')[edge[0]],
                                            nx.get_node_attributes(nw, 'pos')[edge[1]]))
                 for edge in path_list_arr]

            series.append([nw.nodes[node]['pdr'], np.average(d), np.std(d), len(path_list)-1, np.linalg.norm(np.subtract(nx.get_node_attributes(nw, 'pos')[node],
                                            nx.get_node_attributes(nw, 'pos')[0])) ])

    return series


def to_color(p, th=0.6):
    if p < th:
        return 0.7
    if p >= th:
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_ms_properties', description='Plot bar charts, yeah', epilog=':-(')
    parser.add_argument('-d', '--no_dead', dest='no_dead', action='store_true')
    parser.add_argument('-e', '--event', dest='event', action='store_true')
    parser.add_argument('-ex', '--external', dest='external', action='store_true')
    parser.add_argument('-f', '--file', dest='file', help='the yaml file to read')
    args = parser.parse_args()

    # arr [row][column] - inner = column, outer = row
    pdr_arr = []
    # avg. Euclidian distance
    aed_arr = []
    # std. Euclidian distance
    sed_arr = []

    arr = []

    print('Opening file: ' + args.file)
    loader = yaml.safe_load(open(args.file, 'r'))

    for r_idx, run in enumerate(loader['runs']):
        if 'pdr' in run and 'loc_pdr' in run:
            arr = arr+calc_path_stat(run)

    bigarr = np.array(arr)
    bigarr = np.transpose(bigarr)

#    bigarr2d = np.reshape(bigarr, (3,len(np.array(pdr_arr).flat)))
#    #print(list(bigarr2d))
    corrm = np.corrcoef(bigarr)
    cols = ['PDR', 'E(D)', 'D(D)', 'Hop', 'D']
    df = pd.DataFrame(corrm, columns=cols, index=cols)
    print(df.to_string())
