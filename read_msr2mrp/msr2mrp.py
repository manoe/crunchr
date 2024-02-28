import networkx as nx
import argparse
import yaml


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
                            nw.add_edge(node['node'], re['node'], pathid=pathid, secl=secl)
                        else:
                            nw.add_edge(node['node'], re['node'], secl=re['secl'])
    return nw

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_msr2mrp', description='Read msr2mrp traces, yeah', epilog=':-(')
    parser.add_argument('-f', '--file', dest='filename', help='File to read, hopefully yaml format', required=True)
    args = parser.parse_args()

    loader = yaml.safe_load(open(args.filename, 'r'))

    if loader['protocol'] != 'msr2mrp':
        raise Exception('Not MSR2MRP protocol trace')

    graph = construct_graph(loader)

