import networkx as nx
import argparse
import yaml
import logging
logger = logging.getLogger(__name__)
import itertools as it

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
    roles = nx.get_node_attributes(nw, name=role)
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
    print(rm_nodes)
    nw.remove_nodes_from(rm_nodes)
    return nw


def get_nodes_patids(nw,node):
    pathids = []
    for e in nw.out_edges([node], data=True):
        pathids+=e[2]['pathid']
    return pathids

def check_disjointness(nw, node):
    nodes = []
    for p in get_nodes_patids(nw,node):
        f_nw = filter_edges(nw,'pathid',p)
        nodes.append(list(nx.descendants(f_nw,node)))

    for c in it.combinations(nodes,2):
        print(set(c[0]) & set(c[1]))

def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


def filter_edges(nw, property, value):
    f_nw = nx.MultiDiGraph(nw)
    f_nw.remove_edges_from(list(f_nw.edges()))
    for edge in nw.edges(data=True):
        if value in edge[2][property]:
            f_nw.add_edges_from([edge])
    f_nw.remove_nodes_from(list(nx.isolates(f_nw)))
    return f_nw


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filenames', nargs='*')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    args = parser.parse_args()

    stream = open(args.filename[0], 'r')
    loader = yaml.safe_load(stream)

    data = get_data_from_loader(loader)
    nw = construct_graph(data)
    f_nw = filter_graph(nw, filter=['internal','central'])

    ext_nodes = get_nodes_based_on_role(nw,'external')
    borders = get_nodes_based_on_role(nw,'border')

    n_nw = filter_edges(nw, 'pathid', 62)


