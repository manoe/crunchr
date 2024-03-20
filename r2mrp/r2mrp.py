
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