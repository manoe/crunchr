#!/bin/env python3

import matplotlib.pyplot as plt
import networkx as nx
import yaml

def role_to_color(role):
    print(role)
    if role == 'central':
        return 'tab:pink'
    elif role == 'internal':
        return 'tab:brown'
    elif role == 'border':
        return 'tab:cyan'
    elif role == 'external':
        return 'tab:blue'
    return 'tab:grey'


if __name__ == '__main__':
    img = plt.imread('real_example_background.png')
    fig = plt.figure(figsize=(4, 4))

    ax = fig.add_axes(rect=[0,0,1,1])
    x = range(160)
    ax.imshow(img, extent=[0, 160, 0, 160])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.axis('off')
    ax = fig.add_axes(rect=[0,0,1,1])

    stream = open('pdr.yaml', 'r')
    loader = yaml.safe_load(stream)
    if 'runs' in loader:
        data_source = loader['runs'][0]
    else:
        data_source = loader

    g_nw = nx.DiGraph()
    for i in data_source['loc_pdr']:
        g_nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'])
        if 'routing_table' in i:
            for j in i['routing_table']:
                if i['role'] == 'external':
                    pathid = [k['pathid'] for k in j['pathid']]
                    secl = False
                    for k in j['pathid']:
                        if k['secl']:
                            secl = True

                    g_nw.add_edge(i['node'], j['node'], pathid=pathid, secl=secl)
                else:
                    g_nw.add_edge(i['node'], j['node'], secl=j['secl'])

    nx.nodes(g_nw)
    ax.patch.set_alpha(0)

    master_nodes = [i[0] for i in g_nw.nodes(data=True) if i[1]['master'] is True]
    sensor_nodes = [i[0] for i in g_nw.nodes(data=True) if i[1]['master'] is False]

    master_node_color = [role_to_color(nx.get_node_attributes(g_nw, 'role')[i])
                         for i in master_nodes]

    sensor_node_color = [role_to_color(nx.get_node_attributes(g_nw, 'role')[i])
                         for i in sensor_nodes]
    print(master_nodes)
    print(master_node_color)
    print(sensor_node_color)

    if len(master_nodes) > 0:
        nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), nodelist=master_nodes, ax=ax, node_shape='s', node_size=180, node_color=master_node_color)
    nx.draw_networkx_nodes(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), nodelist=sensor_nodes, ax=ax, node_size=180, node_color=sensor_node_color)
    nx.draw_networkx_edges(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'))
    nx.draw_networkx_labels(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), font_size=9)
    #nx.draw(g_nw, pos=nx.get_node_attributes(g_nw, 'pos'), ax=ax, with_labels=True)

    plt.show()


