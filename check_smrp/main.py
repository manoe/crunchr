#!/bin/python3

import argparse
import errno
import yaml
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import sys
import networkx as nx
import matplotlib
import pandas as pd

def construct_graph(loader):
    graph = nx.MultiDiGraph()
    pdr_dict = {i['node']: i['report_pdr'] for i in loader['pdr'] if 'report_pdr' in i}
    pdr_dict.update({i['node']: 0 for i in loader['pdr'] if 'report_pdr' not in i})
    print(pdr_dict)
    for i in loader['loc_pdr']:
        is_sink = i['node'] in i['hop']
        graph.add_node(i['node'], pos=[i['x'], i['y']], sink=is_sink, pdr=pdr_dict[i['node']])
        if 'routing_table' in i:
            for re in i['routing_table']:
                if 'next_hop' in re and re['status'] == 'AVAILABLE':
                    graph.add_edge(i['node'], re['next_hop'], prio=re['prio'], origin=re['origin'])
    return graph


def check_smrp_graph(graph, path_num):
    sinks = [node for node, attribute in graph.nodes(data=True) if attribute['sink']]
    #print(sinks)
    nodes = [node for node in graph.nodes() if node not in sinks]
    #print(nodes)

    node_path_table = []

    for node in nodes:
        node_path_table.append({'node': node})
        node_path_table[-1].update({i: False for i in range(1,path_num+1)})
        sub_graph = nx.MultiDiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['origin'] == node))

        for i in sub_graph.out_edges(node, data=True):
            #print('Edge: '+str(i))
            path_graph = nx.MultiDiGraph(((u, v, e) for u, v, e in sub_graph.edges(data=True) if e['prio'] == i[2]['prio']))
            present_sinks = [i for i in sinks if path_graph.has_node(i)]
            node_path_table[-1].update({i[2]['prio']: True in [nx.has_path(path_graph,node,s) for s in present_sinks]})

    disconnected_nodes = []
    path_count = []
    for node in node_path_table:
        paths = [i for i in list(node.values())[1:] if i]
        if len(paths) == 0:
            disconnected_nodes.append(node['node'])
        path_count.append(len(paths))
    pdr_list = [attribute['pdr'] for node, attribute in graph.nodes(data=True) if attribute['sink'] is False]
    print('Conn ratio: '+str((len(nodes)-len(disconnected_nodes))/len(nodes))+' Path ratio: '+str(sum(path_count)/(len(nodes*path_num)))+' PDR: '+str(np.average(pdr_list)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='check_smrp', description='Check SMRP network', epilog=':-(')
    parser.add_argument('filename', help='use ``-\'\' for stdin')
    parser.add_argument('-p', '--path-num', action='store', dest='path_num', type=int)

    args = parser.parse_args()

    stream = sys.stdin
    if args.filename != '-':
        stream = open(args.filename, 'r')

    loader = yaml.safe_load(stream)
    for run in loader['runs']:
        graph = construct_graph(run)
        check_smrp_graph(graph, args.path_num)

    exit(0)

    pri_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['prio'] == 1))

    sec_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['prio'] == 2))

    route_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['origin'] == 31))

    fig, ax = plt.subplots(figsize=(6, 4))

    plt.subplot(221)
    nx.draw(nx.DiGraph(graph), pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.subplot(222)
    nx.draw(pri_graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.subplot(223)
    nx.draw(sec_graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)
    plt.subplot(224)
    nx.draw(route_graph,  with_labels=True) # pos=nx.get_node_attributes(graph, 'pos'),

    def update(num):
        ax = plt.subplot(224)
        ax.clear()
        route_graph = nx.DiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['origin'] == num))
        nx.draw(route_graph, pos=nx.get_node_attributes(graph, 'pos'), with_labels=True)

#    ani = animation.FuncAnimation(fig, update, frames=63, interval=2000, repeat=True)

    plt.show()

