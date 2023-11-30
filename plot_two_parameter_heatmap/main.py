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
        if node['role'] == 'external' and 'routing_table' in node:
            pn_arr.append(len(node['routing_table']))
    return np.average(pn_arr)


def calc_avg_pdr(run):
    pdr_arr = [node['report_pdr'] for node in run['pdr'] if 'report_pdr' in node and node['node'] not in args.exclude]
    for node in run['pdr']:
        print(type(node['node']))
        print(type(args.exclude[0]))

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
    diameters = []
    for i in outers:
        try:
            diameters.append(nx.shortest_path_length(nw, source=i, target=0))
        except nx.exception.NetworkXNoPath as exp:
            print(exp)

    return np.average(diameters)


def calc_conn_ratio(run):
    return float(len([n for n in run['loc_pdr'] if n['state'] == 'WORK'])) / float(len(run['loc_pdr']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='plot_two_parameter_heatmap', description='Plot heatmaps, yeah', epilog=':-(')
    parser.add_argument('-q', '--qos', dest='qos', action='store', nargs='+', type=float)
    parser.add_argument('-p', '--pos', dest='pos', action='store', nargs='+', type=str)
    parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', type=int, help='Exclude nodes from calculation')
    parser.add_argument('-f', '--file', dest='file', help='use the pattern blabla_qos_pos_babla.yaml')
    args = parser.parse_args()

    # arr [row][column] - inner = column, outer = row
    pdr_arr = [[[] for x in args.qos] for y in args.pos]
    # average path number
    apn_arr = [[[] for x in args.qos] for y in args.pos]
    # average network diameter
    and_arr = [[[] for x in args.qos] for y in args.pos]

    # ratio of connected nodes
    con_arr = [[[] for x in args.qos] for y in args.pos]

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
                    con_arr[idx_p][idx_q].append(calc_conn_ratio(run))

    def avg_arr(arr):
        return [[np.average(arr[idx_p][idx_q]) for idx_q, q in enumerate(args.qos)] for idx_p, p in enumerate(args.pos)]

    avg_apn_arr = avg_arr(apn_arr)
    avg_and_arr = avg_arr(and_arr)
    avg_pdr_arr = avg_arr(pdr_arr)
    avg_con_arr = avg_arr(con_arr)
    print(con_arr)

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

    fig, ax = plt.subplots(nrows=4)

    for idx, arr in enumerate([avg_pdr_arr, avg_apn_arr, avg_and_arr, avg_con_arr]):
    # Show all ticks and label them with the respective list entries
        im = ax[idx].imshow(arr)
        ax[idx].set_xticks(np.arange(len(args.qos)), labels=args.qos)
        ax[idx].set_yticks(np.arange(len(args.pos)), labels=args.pos)

    # Rotate the tick labels and set their alignment.
        plt.setp(ax[idx].get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
        for i in range(len(args.pos)):
            for j in range(len(args.qos)):
                text = ax[idx].text(j, i, "{:.2f}".format(arr[i][j]),
                               ha="center", va="center", color="w")
    for idx, label in enumerate(['Average Network PDR', 'Average Path Number', 'Average Network Diameter', 'Average Connected Node Ratio']):
        ax[idx].set_title(label)
    fig.tight_layout()
    plt.show()
