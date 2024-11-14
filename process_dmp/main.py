import networkx as nx
import argparse
import yaml
import logging
logger = logging.getLogger(__name__)

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

def get_data_from_loader(top):
    if 'runs' in top:
        return top['runs'][0]['loc_pdr']
    else:
        return top


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='border_plot', description='Process MSR2MRP border node related stats', epilog=':-(')
    parser.add_argument('filename', help='Input filenames', nargs='*')
    parser.add_argument('-o', '--out', dest='out', type=str, default='out', help='Output filename')
    args = parser.parse_args()

    stream = open(args.filename[0], 'r')
    loader = yaml.safe_load(stream)

    data = get_data_from_loader(loader)

    nw = construct_graph(data)

    nf_f = filter_graph(nw, filter=['internal','central'])
