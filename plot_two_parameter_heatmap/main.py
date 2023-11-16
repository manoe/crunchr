#!/bin/python3

import argparse
import yaml
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

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
        if node['role'] == 'external':
            pn_arr.append(len(node['routing_table']))
    return np.average(pn_arr)


def calc_avg_pdr(run):
    print(run['pdr'])
    pdr_arr = [node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node]
    return np.average(pdr_arr)


def calc_avg_nw_diameter(run):
    nw = nx.DiGraph()
    for i in run['loc_pdr']:
        nw.add_node(i['node'], role=i['role'], master=i['master'], pos=[i['x'], i['y']], state=i['state'])
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
    outers = [node for node, in_degree in nw.in_degree() if in_degree == 0]
    print(outers)
    return np.average([nx.shortest_path_length(nw, source=i, target=0) for i in outers])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_two_parameter_heatmap', description='Plot heatmaps, yeah', epilog=':-(')
    parser.add_argument('-q', '--qos', dest='qos', action='store', nargs='+', type=float)
    parser.add_argument('-p', '--pos', dest='pos', action='store', nargs='+', type=str)

    # shmrp_0.0_center_pdr.yaml
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_qos_pos_babla.yaml')
    args = parser.parse_args()

    # arr [row][column] - inner = column, outer = row
    pdr_arr = [[[] for x in args.qos] for y in args.pos]
    # average path number
    apn_arr = pdr_arr.copy()
    # average network diameter
    and_arr = pdr_arr.copy()

    for idx_q, q in enumerate(args.qos):
        for idx_p, p in enumerate(args.pos):
            filename = args.file.replace('qos', str(q)).replace('pos', str(p))
            print('Opening file: ' + filename)
            loader = yaml.safe_load(open(filename, 'r'))
            for run in loader['runs']:
                if 'pdr' in run and 'loc_pdr' in run:
                    pdr_arr[idx_p][idx_q].append(calc_avg_pdr(run))
                    apn_arr[idx_p][idx_q].append(calc_avg_path_num(run))
                    and_arr[idx_p][idx_q].append(calc_avg_nw_diameter(run))

    def avg_arr(arr):
        return [[np.average(arr[idx_p][idx_q]) for idx_q, q in enumerate(args.qos)] for idx_p, p in enumerate(args.pos)]

    avg_apn_arr = avg_arr(apn_arr)
    avg_and_arr = avg_arr(and_arr)
    avg_pdr_arr = avg_arr(pdr_arr)

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

    fig, ax = plt.subplots()
    im = ax.imshow(avg_pdr_arr)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(args.qos)), labels=args.qos)
    ax.set_yticks(np.arange(len(args.pos)), labels=args.pos)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(args.pos)):
        for j in range(len(args.qos)):
            text = ax.text(j, i, avg_pdr_arr[i][j],
                           ha="center", va="center", color="w")

    ax.set_title("QoS parameter and sink placement")
    fig.tight_layout()
    plt.show()
