import networkx as nx

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