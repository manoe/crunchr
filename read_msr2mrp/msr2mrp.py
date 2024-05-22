import networkx as nx

import argparse
import yaml
import matplotlib.pyplot as plt
import pygraphviz as pgv
def construct_graph(run):
    nw = nx.MultiDiGraph()
    for node in run['loc_pdr']:
        nw.add_node(node['node'], master=node['master'], pos=[node['x'], node['y']])
        if 'engines' in node:
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
    return nw

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_msr2mrp', description='Read msr2mrp traces, yeah', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='File to read, hopefully yaml format', required=True)
    parser.add_argument('-b','--base-size', dest='base_size', help='Base size', type=int, default=4)
    args = parser.parse_args()

    loader = yaml.safe_load(open(args.filename, 'r'))

    if loader['protocol'] != 'msr2mrp':
        raise Exception('Not MSR2MRP protocol trace')

    graph = construct_graph(loader)

    sink_list = [node['node'] for node in loader['loc_pdr'] if len([engine['engine']
                 for engine in node['engines'] if engine['role'] == 'central']) > 0]

    plot_list = [sink_list]
    for j in sink_list:
        plot_list.append([j])

    fig, axs = plt.subplots(nrows=len(plot_list), ncols=1, figsize=(args.base_size, args.base_size*len(plot_list)))
    plt.subplots_adjust(wspace=0, hspace=0)

    for idx, ax in enumerate(axs.ravel()):
        ax.set_adjustable('box')
        ax.set_aspect('equal')
        sub_graph = nx.MultiDiGraph(((u, v, e) for u, v, e in graph.edges(data=True) if e['engine'] in plot_list[idx]))
        sub_graph.add_nodes_from(graph.nodes)
        nx.draw(sub_graph, nx.get_node_attributes(graph, 'pos'), ax=ax, with_labels=True, connectionstyle="arc3,rad=0.1")

    plt.tight_layout()
    plt.show()
    A = nx.nx_agraph.to_agraph(graph)
    A.layout()
    A.draw('networkx_graph.png')
